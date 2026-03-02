# Result: FileHandlerAgent

**Status**: Complete
**Date**: 2026-02-26

## Files Created

- `src/agents/file_handler_agent/file_handler_agent.py`
- `src/agents/file_handler_agent/file_handler_agent.md`
- `src/agents/file_handler_agent/__init__.py`

## Summary

Implemented `FileHandlerAgent` with all five async methods:

- `upload_to_blob` — uploads to `examops-input`, blob name `{timestamp}_{user_id}_{filename}`, returns 1-hour SAS URL.
- `download_from_blob` — fetches blob via `requests.get`, parses as python-docx `Document`, raises `ValueError` on parse failure.
- `get_template_from_vectordb` — ada-002 embedding via `AzureOpenAI`, `VectorizedQuery` against `exam-templates` index, returns `template_rules` dict.
- `save_outputs` — saves `.docx` and HTML diff to `examops-output` with 1-hour SAS URLs.
- `create_onedrive_link` — client-credentials Graph API token, uploads to OneDrive root, creates anonymous view link.

All 7 env vars are read via `os.getenv()` at `__init__` time with no import-time side effects.

## Caveats

- Azure SDK imports (`BlobServiceClient`, `SearchClient`, `AzureOpenAI`) are deferred inside each method to avoid import errors when packages are not installed during testing.
- `_get_graph_token` uses client credentials flow — requires `GRAPH_CLIENT_SECRET` to be a valid secret for a registered Entra ID app with `Files.ReadWrite.All` delegated or application permission.
