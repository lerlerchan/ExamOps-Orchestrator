"""
Azure Function HTTP trigger — GET /api/diff-report?job_id=...

Returns the HTML diff report for a format-exam job from blob storage (same-origin),
so the Step 5 iframe can display it without X-Frame-Options / CORS issues.
"""

import logging

import azure.functions as func

logger = logging.getLogger(__name__)


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Serve the diff report HTML for a job by job_id."""
    job_id = req.params.get("job_id")
    if not job_id or not job_id.strip():
        return func.HttpResponse(
            "Missing job_id",
            status_code=400,
            mimetype="text/plain",
        )

    job_id = job_id.strip()

    try:
        from src.agents.file_handler_agent.file_handler_agent import FileHandlerAgent

        file_handler = FileHandlerAgent()
        html = file_handler.get_diff_html(job_id)
    except Exception as exc:
        logger.exception("Failed to get diff report for job_id=%s", job_id)
        return func.HttpResponse(
            f"Diff report not found or failed to load: {exc!s}",
            status_code=404,
            mimetype="text/plain",
        )

    return func.HttpResponse(
        html,
        status_code=200,
        mimetype="text/html",
        charset="utf-8",
        headers={
            "Cache-Control": "private, max-age=300",
            "X-Content-Type-Options": "nosniff",
        },
    )
