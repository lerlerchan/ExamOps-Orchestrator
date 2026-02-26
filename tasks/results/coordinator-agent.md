# Result: CoordinatorAgent

**Status**: Complete
**Date**: 2026-02-26

## Files Created

- `src/agents/coordinator_agent/coordinator_agent.py`
- `src/agents/coordinator_agent/coordinator_agent.md`
- `src/agents/coordinator_agent/__init__.py`

## Summary

Implemented `CoordinatorAgent` with:

- `JobState` dataclass tracking `job_id`, `user_id`, `file_url`, `status`, `created_at`, `updated_at`, `error`.
- `async def process_job(job_id, user_id, file_url) -> dict` — drives the full 6-step pipeline.
- Sequential call chain enforced: `FileHandlerAgent` → `FormattingEngineAgent` → `DiffGeneratorAgent`.
- Error handling for all four defined error codes (`ERR_CORRUPTED_FILE`, `ERR_TEMPLATE_NOT_FOUND`, `ERR_LLM_TIMEOUT`, `ERR_STORAGE`).
- LLM timeout handled gracefully — pipeline completes with `status="partial"`.
- Returns `{status, compliance_score, formatted_url, diff_url, onedrive_link, summary, error}`.

## Caveats

- Sub-agent imports are deferred to `__init__` to avoid circular import issues at module load.
- `_build_summary` produces a human-readable string suitable for Teams card display.
