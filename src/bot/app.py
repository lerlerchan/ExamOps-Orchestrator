"""
Bot Framework adapter + AIOHTTP app entry point.

Exposes POST /api/messages for the Teams channel.
Environment variables required:
  MICROSOFT_APP_ID       — Bot App ID from Azure Bot registration
  MICROSOFT_APP_PASSWORD — Bot App Password
"""

import logging
import os

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity

from src.bot.bot import ExamOpsBot

logger = logging.getLogger(__name__)

# --- Adapter ---
adapter_settings = BotFrameworkAdapterSettings(
    app_id=os.environ.get("MICROSOFT_APP_ID", ""),
    app_password=os.environ.get("MICROSOFT_APP_PASSWORD", ""),
)
adapter = BotFrameworkAdapter(adapter_settings)


async def on_error(context, error: Exception):
    logger.exception("Unhandled exception in bot", exc_info=error)
    await context.send_activity("An unexpected error occurred. Please try again.")


adapter.on_turn_error = on_error

bot = ExamOpsBot()


# --- Routes ---
async def messages(req: Request) -> Response:
    """Main bot endpoint — receives all Teams channel traffic."""
    if req.content_type != "application/json":
        return Response(status=415, text="Unsupported Media Type")

    body = await req.json()
    activity = Activity().deserialize(body)

    auth_header = req.headers.get("Authorization", "")

    response = await adapter.process_activity(activity, auth_header, bot.on_turn)
    if response:
        return json_response(data=response.body, status=response.status)
    return Response(status=201)


# --- App factory ---
def create_app() -> web.Application:
    app = web.Application()
    app.router.add_post("/api/messages", messages)
    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = create_app()
    web.run_app(app, host="0.0.0.0", port=int(os.environ.get("PORT", 3978)))
