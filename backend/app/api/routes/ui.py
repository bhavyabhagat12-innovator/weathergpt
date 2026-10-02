"""
UI router serving the single-page chat interface.
"""

from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])

STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "static"


@router.get("/", response_class=HTMLResponse)
@router.get("/chat", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
@router.get("/alerts", response_class=HTMLResponse)
@router.get("/climate", response_class=HTMLResponse)
@router.get("/briefing", response_class=HTMLResponse)
async def serve_chat_ui():
    """Serves the WeatherGPT web user interface application."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>WeatherGPT UI loading error: index.html not found</h1>", status_code=500)

