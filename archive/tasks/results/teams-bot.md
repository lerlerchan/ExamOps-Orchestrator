# Result: Teams Bot

**Status**: Complete
**Date**: 2026-02-26

## Files Created

- `src/bot/bot.py`
- `src/bot/app.py`

## Summary

### `bot.py` — ExamOpsBot

- Implements `ExamOpsBot(ActivityHandler)` with `on_message_activity`.
- Detects `.docx` attachment by filename extension.
- Downloads attachment bytes via `requests.get(attachment.content_url)`.
- Uploads to `examops-input` via `FileHandlerAgent.upload_to_blob`.
- Sends a "Processing…" acknowledgement message.
- Calls `CoordinatorAgent.process_job` with a generated UUID job_id.
- On success, sends an adaptive card with: compliance score, fix summary, OneDrive link button, diff report link button.
- On failure, sends a plain error message.
- On no-attachment message, replies with usage instructions.

### `app.py` — Bot Framework adapter

- Configures `BotFrameworkAdapter` with `MICROSOFT_APP_ID` / `MICROSOFT_APP_PASSWORD` from env.
- Registers `POST /api/messages` route via aiohttp.
- Exposes `create_app()` factory for easy testing.
- Runs on `PORT` env var (default 3978) when invoked directly.

## Caveats

- Requires `botbuilder-core`, `botbuilder-schema`, `aiohttp` (all added to `requirements.txt`).
- `attachment.content_url` in Teams contains a short-lived token — production deployments should use the Bot Framework `connector_client` to download attachments rather than a plain `requests.get`.
