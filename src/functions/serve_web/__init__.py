"""
Azure Function HTTP trigger — GET /api/web

Serves the ExamOps web frontend (src/web/index.html) as a static HTML page.
Auth level is anonymous so users can access the UI without a function key.
"""

import logging
import os
from pathlib import Path

import azure.functions as func

logger = logging.getLogger(__name__)

# Resolve the HTML file path relative to this module's location.
# Deployed layout: serve_web/__init__.py  AND  src/web/index.html are both
# included in the zip, so we walk up two levels from this file.
_THIS_DIR = Path(__file__).resolve().parent
_HTML_PATH = _THIS_DIR.parent.parent / "src" / "web" / "index.html"

# Fallback: try sibling path if deployed at root (after cp in workflow)
_ALT_HTML_PATH = _THIS_DIR.parent / "web" / "index.html"


def _load_html() -> str:
    """Load the frontend HTML from disk, trying both known paths."""
    for candidate in (_HTML_PATH, _ALT_HTML_PATH):
        if candidate.exists():
            logger.debug("Serving HTML from %s", candidate)
            return candidate.read_text(encoding="utf-8")

    # Last-resort inline fallback so the function never 500s
    logger.warning(
        "index.html not found at %s or %s — returning minimal fallback",
        _HTML_PATH,
        _ALT_HTML_PATH,
    )
    return (
        "<!DOCTYPE html><html><head><title>ExamOps</title></head><body>"
        "<h1>ExamOps Orchestrator</h1>"
        "<p>Frontend asset not found. Please redeploy the application.</p>"
        "</body></html>"
    )


def main(req: func.HttpRequest) -> func.HttpResponse:
    """Serve the ExamOps web UI."""
    html = _load_html()
    return func.HttpResponse(
        html,
        status_code=200,
        mimetype="text/html",
        charset="utf-8",
    )
