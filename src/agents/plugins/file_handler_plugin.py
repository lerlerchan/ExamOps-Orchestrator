"""
FileHandlerPlugin — Semantic Kernel plugin wrapping FileHandlerAgent.

Each @kernel_function takes only a job_id string, reads/writes the shared
JobContext via the module-level registry, and returns a plain status string
that the SK team leader uses to track progress.
"""

import logging

from semantic_kernel.functions import kernel_function

from src.agents.job_context import registry

logger = logging.getLogger(__name__)


class FileHandlerPlugin:
    """SK plugin exposing FileHandlerAgent operations as kernel functions."""

    def __init__(self, file_handler_agent) -> None:
        self._agent = file_handler_agent

    @kernel_function(
        name="download_document",
        description="Download the .docx file from blob storage for the given job.",
    )
    async def download_document(self, job_id: str) -> str:
        """
        Download the original exam document and store it in JobContext.

        Args:
            job_id: Unique job identifier.

        Returns:
            Status string for the team leader.
        """
        ctx = registry.get(job_id)
        if ctx is None:
            return f"ERROR: No job context found for job_id={job_id}"
        try:
            ctx.original_doc = await self._agent.download_from_blob(ctx.file_url)
            logger.info("[SK] download_document completed for job %s", job_id)
            return f"Document downloaded successfully for job {job_id}."
        except Exception as exc:
            ctx.last_error = str(exc)
            logger.error("[SK] download_document failed for job %s: %s", job_id, exc)
            return f"ERROR: {exc}"

    @kernel_function(
        name="get_template",
        description="Retrieve institutional formatting rules from the vector database.",
    )
    async def get_template(self, job_id: str) -> str:
        """
        Retrieve template rules from Azure AI Search and store in JobContext.

        Args:
            job_id: Unique job identifier.

        Returns:
            Status string for the team leader.
        """
        ctx = registry.get(job_id)
        if ctx is None:
            return f"ERROR: No job context found for job_id={job_id}"
        try:
            ctx.template_rules = await self._agent.get_template_from_vectordb(
                "Southern University College exam paper formatting rules"
            )
            logger.info("[SK] get_template completed for job %s", job_id)
            return f"Template rules retrieved for job {job_id}."
        except Exception as exc:
            ctx.last_error = str(exc)
            logger.error("[SK] get_template failed for job %s: %s", job_id, exc)
            return f"ERROR: {exc}"

    @kernel_function(
        name="save_outputs",
        description="Save the formatted document and HTML diff report to blob storage.",
    )
    async def save_outputs(self, job_id: str) -> str:
        """
        Upload formatted .docx and HTML diff to examops-output container.

        Args:
            job_id: Unique job identifier.

        Returns:
            Status string with output URLs for the team leader.
        """
        ctx = registry.get(job_id)
        if ctx is None:
            return f"ERROR: No job context found for job_id={job_id}"
        try:
            diff_html = (
                ctx.diff_result["html_report"] if ctx.diff_result else ""
            )
            ctx.output_urls = await self._agent.save_outputs(
                ctx.formatted_doc, diff_html, job_id
            )
            logger.info("[SK] save_outputs completed for job %s", job_id)
            return f"Outputs saved for job {job_id}. URLs: {ctx.output_urls}"
        except Exception as exc:
            ctx.last_error = str(exc)
            logger.error("[SK] save_outputs failed for job %s: %s", job_id, exc)
            return f"ERROR: {exc}"

    @kernel_function(
        name="create_sharing_link",
        description="Create a shareable OneDrive link for the formatted document.",
    )
    async def create_sharing_link(self, job_id: str) -> str:
        """
        Generate a shareable OneDrive link and store it in JobContext.

        Falls back to the blob URL if OneDrive link creation fails.

        Args:
            job_id: Unique job identifier.

        Returns:
            Status string with the sharing URL for the team leader.
        """
        ctx = registry.get(job_id)
        if ctx is None:
            return f"ERROR: No job context found for job_id={job_id}"
        try:
            docx_url = ctx.output_urls["docx"] if ctx.output_urls else ""
            ctx.onedrive_link = await self._agent.create_onedrive_link(docx_url)
            logger.info(
                "[SK] create_sharing_link completed for job %s", job_id
            )
            return (
                f"OneDrive link created for job {job_id}: {ctx.onedrive_link}"
            )
        except Exception as exc:
            ctx.last_error = str(exc)
            ctx.onedrive_link = (
                ctx.output_urls.get("docx", "") if ctx.output_urls else ""
            )
            logger.warning(
                "[SK] create_sharing_link failed for job %s: %s", job_id, exc
            )
            return (
                f"OneDrive link unavailable; using blob URL: {ctx.onedrive_link}"
            )
