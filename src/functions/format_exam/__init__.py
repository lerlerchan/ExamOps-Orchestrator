"""
Azure Function HTTP trigger — POST /api/format-exam

Accepts multipart/form-data with:
  file     : .docx binary
  user_id  : string

Returns job result JSON from CoordinatorAgent.
"""

import io
import json
import logging
import uuid

import azure.functions as func

logger = logging.getLogger(__name__)


async def main(req: func.HttpRequest) -> func.HttpResponse:
    """Entry point for the format-exam HTTP trigger."""

    # --- Parse request ---
    user_id = req.form.get("user_id") or req.params.get("user_id")
    file_data = req.files.get("file")

    if not user_id or not file_data:
        return func.HttpResponse(
            json.dumps({"error": "Missing required fields: 'file' and 'user_id'."}),
            status_code=400,
            mimetype="application/json",
        )

    filename = file_data.filename or "upload.docx"
    if not filename.lower().endswith(".docx"):
        return func.HttpResponse(
            json.dumps({"error": "Only .docx files are supported."}),
            status_code=400,
            mimetype="application/json",
        )

    file_bytes = file_data.read()
    if not file_bytes:
        return func.HttpResponse(
            json.dumps({"error": "Uploaded file is empty."}),
            status_code=400,
            mimetype="application/json",
        )

    job_id = str(uuid.uuid4())
    logger.info("format-exam triggered job_id=%s user_id=%s filename=%s", job_id, user_id, filename)

    # --- Upload to Blob Storage ---
    try:
        from src.agents.file_handler_agent.file_handler_agent import FileHandlerAgent

        file_handler = FileHandlerAgent()
        blob_url = await file_handler.upload_to_blob(
            file_stream=io.BytesIO(file_bytes),
            filename=filename,
            user_id=user_id,
        )
    except ValueError as exc:
        logger.warning("Upload rejected for job_id=%s: %s", job_id, exc)
        return func.HttpResponse(
            json.dumps({"error": str(exc)}),
            status_code=422,
            mimetype="application/json",
        )
    except Exception as exc:
        logger.exception("Blob upload failed for job_id=%s", job_id)
        return func.HttpResponse(
            json.dumps({"error": "Failed to upload file to storage.", "detail": str(exc)}),
            status_code=500,
            mimetype="application/json",
        )

    # --- Run pipeline ---
    try:
        from src.agents.coordinator_agent.coordinator_agent import CoordinatorAgent

        coordinator = CoordinatorAgent()
        result = await coordinator.process_job(
            job_id=job_id,
            user_id=user_id,
            file_url=blob_url,
        )
    except Exception as exc:
        logger.exception("Pipeline failed for job_id=%s", job_id)
        return func.HttpResponse(
            json.dumps({"error": "Pipeline execution failed.", "detail": str(exc)}),
            status_code=500,
            mimetype="application/json",
        )

    # Map CoordinatorAgent error codes to HTTP status codes
    error_to_status = {
        "ERR_CORRUPTED_FILE": 422,
        "ERR_TEMPLATE_NOT_FOUND": 422,
        "ERR_STORAGE": 500,
    }
    status_code = error_to_status.get(result.get("error"), 200)

    return func.HttpResponse(
        json.dumps(result),
        status_code=status_code,
        mimetype="application/json",
    )
