# Result: Azure Function HTTP Trigger

**Status**: Complete
**Date**: 2026-02-26

## Files Created

- `src/functions/format_exam/__init__.py`
- `src/functions/format_exam/function.json`

## Summary

Implemented the `format-exam` Azure Function HTTP trigger:

- Accepts `multipart/form-data` POST with `file` (.docx binary) and `user_id` fields.
- Validates inputs — returns 400 for missing fields or non-.docx files.
- Uploads received bytes to `examops-input` via `FileHandlerAgent.upload_to_blob`.
- Generates a UUID4 `job_id` and calls `CoordinatorAgent.process_job`.
- Returns 200 JSON job result on success.
- Maps CoordinatorAgent error codes to HTTP status codes: `ERR_CORRUPTED_FILE` / `ERR_TEMPLATE_NOT_FOUND` → 422, `ERR_STORAGE` → 500.
- `function.json` configures `httpTrigger`, POST only, `authLevel: function`, route `format-exam`.

## Caveats

- `async def main` requires `azure-functions` >= 1.11 with async support enabled in `host.json`.
- All Azure SDK imports are lazy (inside `main`) to keep cold-start overhead minimal.
