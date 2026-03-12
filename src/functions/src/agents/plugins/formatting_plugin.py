"""
FormattingPlugin — Semantic Kernel plugin wrapping FormattingEngineAgent.

Exposes a single @kernel_function that runs Layer 1 (rule-based) and
Layer 2 (LLM validation) and stores the results in JobContext.
"""

import logging

from semantic_kernel.functions import kernel_function

from src.agents.job_context import registry

logger = logging.getLogger(__name__)


class FormattingPlugin:
    """SK plugin exposing FormattingEngineAgent as a kernel function."""

    def __init__(self, formatting_engine_agent) -> None:
        self._agent = formatting_engine_agent

    @kernel_function(
        name="format_and_validate",
        description=(
            "Apply institutional formatting rules to the document and validate "
            "compliance via GPT-4o-mini. Stores the formatted document and "
            "compliance score in the job context."
        ),
    )
    async def format_and_validate(self, job_id: str) -> str:
        """
        Run the two-layer formatter and store results in JobContext.

        Args:
            job_id: Unique job identifier.

        Returns:
            Status string with compliance score for the team leader.
        """
        ctx = registry.get(job_id)
        if ctx is None:
            return f"ERROR: No job context found for job_id={job_id}"
        try:
            ctx.formatted_doc, ctx.validation_result = (
                await self._agent.process_and_validate(
                    ctx.original_doc, ctx.template_rules
                )
            )
            score = ctx.validation_result.get("compliance_score")
            score_str = (
                f"{score:.1f}%" if score is not None else "N/A (LLM fallback)"
            )
            logger.info(
                "[SK] format_and_validate completed for job %s — score=%s",
                job_id,
                score_str,
            )
            return (
                f"Formatting complete for job {job_id}. "
                f"Compliance score: {score_str}."
            )
        except Exception as exc:
            ctx.last_error = str(exc)
            logger.error(
                "[SK] format_and_validate failed for job %s: %s", job_id, exc
            )
            return f"ERROR: {exc}"
