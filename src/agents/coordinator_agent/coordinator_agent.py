"""
CoordinatorAgent — single entry point for the ExamOps formatting pipeline.

Orchestrates the full job lifecycle:
  FileHandlerAgent → FormattingEngineAgent → DiffGeneratorAgent

All agent calls are routed through here; agents never call each other directly.
"""

import os
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class JobState:
    """Tracks lifecycle state for a single formatting job."""

    job_id: str
    user_id: str
    file_url: str
    status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    error: Optional[str] = None

    def update_status(self, status: str, error: Optional[str] = None) -> None:
        self.status = status
        self.updated_at = datetime.now(timezone.utc)
        if error:
            self.error = error


class CoordinatorAgent:
    """
    Orchestrates the end-to-end exam formatting pipeline.

    Entry points:
      - process_job()  — called by the Azure Function HTTP trigger
      - process_job()  — called by the Teams Bot ActivityHandler

    Sequential call chain:
      1. FileHandlerAgent.download_from_blob()
      2. FileHandlerAgent.get_template_from_vectordb()
      3. FormattingEngineAgent.process_and_validate()
      4. DiffGeneratorAgent.create_html_diff()
      5. FileHandlerAgent.save_outputs()
      6. FileHandlerAgent.create_onedrive_link()
    """

    def __init__(self) -> None:
        # Lazy imports to avoid circular dependencies at module load time.
        from src.agents.file_handler_agent.file_handler_agent import FileHandlerAgent
        from src.agents.formatting_engine.formatting_engine import FormattingEngineAgent
        from src.agents.diff_generator.diff_generator import DiffGeneratorAgent

        self.file_handler = FileHandlerAgent()
        self.formatting_engine = FormattingEngineAgent()
        self.diff_generator = DiffGeneratorAgent()

    async def process_job(
        self, job_id: str, user_id: str, file_url: str
    ) -> dict:
        """
        Run the full formatting pipeline for one exam paper.

        Args:
            job_id:   Unique identifier for this job (UUID string).
            user_id:  Teams / AAD user ID of the requester.
            file_url: Azure Blob SAS URL of the uploaded .docx file.

        Returns:
            dict with keys:
                status          — "success" | "partial" | "failed"
                compliance_score — 0–100 float, or None if LLM unavailable
                formatted_url   — SAS URL of the formatted .docx
                diff_url        — SAS URL of the HTML diff report
                onedrive_link   — Shareable OneDrive URL
                summary         — Human-readable summary string
                error           — Error message if status != "success"

        Error codes (returned in result["error"]):
            ERR_CORRUPTED_FILE      — .docx could not be parsed
            ERR_TEMPLATE_NOT_FOUND  — Azure AI Search returned no template rules
            ERR_LLM_TIMEOUT         — LLM validation timed out; rule-based only
            ERR_STORAGE             — Azure Blob upload/download failure
        """
        job = JobState(job_id=job_id, user_id=user_id, file_url=file_url)
        logger.info("Job %s started for user %s", job_id, user_id)

        # ── Step 1: Download original document ─────────────────────────────
        job.update_status("downloading")
        try:
            original_doc = await self.file_handler.download_from_blob(file_url)
        except Exception as exc:
            logger.error("Job %s: download failed — %s", job_id, exc)
            job.update_status("failed", error="ERR_CORRUPTED_FILE")
            return self._failure_result(job, "ERR_CORRUPTED_FILE", str(exc))

        # ── Step 2: Retrieve template rules ────────────────────────────────
        job.update_status("retrieving_template")
        try:
            template_rules = await self.file_handler.get_template_from_vectordb(
                query="Southern University College exam paper formatting rules"
            )
        except Exception as exc:
            logger.error("Job %s: template retrieval failed — %s", job_id, exc)
            job.update_status("failed", error="ERR_TEMPLATE_NOT_FOUND")
            return self._failure_result(job, "ERR_TEMPLATE_NOT_FOUND", str(exc))

        if not template_rules:
            job.update_status("failed", error="ERR_TEMPLATE_NOT_FOUND")
            return self._failure_result(
                job, "ERR_TEMPLATE_NOT_FOUND", "Azure AI Search returned no results"
            )

        # ── Step 3: Format + validate ───────────────────────────────────────
        job.update_status("formatting")
        try:
            formatted_doc, validation_result = (
                await self.formatting_engine.process_and_validate(
                    original_doc, template_rules
                )
            )
        except Exception as exc:
            logger.error("Job %s: formatting failed — %s", job_id, exc)
            job.update_status("failed")
            return self._failure_result(job, "ERR_FORMATTING", str(exc))

        # Detect LLM timeout fallback
        llm_timed_out = validation_result.get("fallback_mode", False)
        if llm_timed_out:
            logger.warning("Job %s: LLM timed out, proceeding with rule-based only", job_id)

        # ── Step 4: Generate diff ───────────────────────────────────────────
        job.update_status("generating_diff")
        try:
            diff_result = self.diff_generator.create_html_diff(
                original_doc, formatted_doc, validation_result
            )
        except Exception as exc:
            logger.error("Job %s: diff generation failed — %s", job_id, exc)
            diff_result = {"html_report": "", "summary_stats": {}}

        # ── Step 5: Save outputs ────────────────────────────────────────────
        job.update_status("saving")
        try:
            output_urls = await self.file_handler.save_outputs(
                formatted_doc, diff_result["html_report"], job_id
            )
        except Exception as exc:
            logger.error("Job %s: save outputs failed — %s", job_id, exc)
            job.update_status("failed", error="ERR_STORAGE")
            return self._failure_result(job, "ERR_STORAGE", str(exc))

        # ── Step 6: Create OneDrive sharing link ────────────────────────────
        try:
            onedrive_link = await self.file_handler.create_onedrive_link(
                output_urls["docx"]
            )
        except Exception as exc:
            logger.warning("Job %s: OneDrive link creation failed — %s", job_id, exc)
            onedrive_link = output_urls.get("docx", "")

        # ── Build result ────────────────────────────────────────────────────
        stats = diff_result.get("summary_stats", {})
        compliance_score = validation_result.get("compliance_score")
        status = "partial" if llm_timed_out else "success"

        job.update_status(status)
        logger.info(
            "Job %s completed — status=%s compliance=%.1f",
            job_id,
            status,
            compliance_score or 0.0,
        )

        return {
            "status": status,
            "compliance_score": compliance_score,
            "formatted_url": output_urls.get("docx", ""),
            "diff_url": output_urls.get("html", ""),
            "onedrive_link": onedrive_link,
            "summary": self._build_summary(stats, compliance_score, llm_timed_out),
            "error": None,
        }

    # ── Helpers ─────────────────────────────────────────────────────────────

    def _failure_result(self, job: JobState, error_code: str, detail: str) -> dict:
        return {
            "status": "failed",
            "compliance_score": None,
            "formatted_url": "",
            "diff_url": "",
            "onedrive_link": "",
            "summary": f"Job failed: {error_code}",
            "error": f"{error_code}: {detail}",
        }

    def _build_summary(
        self,
        stats: dict,
        compliance_score: Optional[float],
        llm_timed_out: bool,
    ) -> str:
        total = stats.get("total_changes", 0)
        score_str = (
            f"{compliance_score:.1f}%" if compliance_score is not None else "N/A"
        )
        fallback_note = " (LLM timed out — rule-based only)" if llm_timed_out else ""
        return (
            f"Formatting complete. {total} change(s) applied. "
            f"Compliance score: {score_str}.{fallback_note}"
        )
