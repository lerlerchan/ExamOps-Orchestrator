"""
DiffPlugin — Semantic Kernel plugin wrapping DiffGeneratorAgent.

Exposes a single @kernel_function that produces the color-coded HTML
diff report and summary stats, storing the result in JobContext.
"""

import logging

from semantic_kernel.functions import kernel_function

from src.agents.job_context import registry

logger = logging.getLogger(__name__)


class DiffPlugin:
    """SK plugin exposing DiffGeneratorAgent as a kernel function."""

    def __init__(self, diff_generator_agent) -> None:
        self._agent = diff_generator_agent

    @kernel_function(
        name="generate_diff",
        description=(
            "Generate a color-coded HTML diff report comparing the original "
            "and formatted documents. Stores the report and summary stats in "
            "the job context."
        ),
    )
    def generate_diff(self, job_id: str) -> str:
        """
        Create the HTML diff report and store it in JobContext.

        Note: DiffGeneratorAgent.create_html_diff is synchronous.

        Args:
            job_id: Unique job identifier.

        Returns:
            Status string with change count for the team leader.
        """
        ctx = registry.get(job_id)
        if ctx is None:
            return f"ERROR: No job context found for job_id={job_id}"
        try:
            ctx.diff_result = self._agent.create_html_diff(
                ctx.original_doc,
                ctx.formatted_doc,
                ctx.validation_result or {},
            )
            changes = (
                ctx.diff_result.get("summary_stats", {}).get("total_changes", 0)
            )
            logger.info(
                "[SK] generate_diff completed for job %s — %d change(s)",
                job_id,
                changes,
            )
            return (
                f"Diff report generated for job {job_id}. "
                f"Total changes: {changes}."
            )
        except Exception as exc:
            ctx.last_error = str(exc)
            ctx.diff_result = {"html_report": "", "summary_stats": {}}
            logger.error(
                "[SK] generate_diff failed for job %s: %s", job_id, exc
            )
            return f"ERROR: {exc}"
