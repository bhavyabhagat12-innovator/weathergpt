"""
WeatherGPT FastAPI main application entrypoint.
Features latency tracking middleware, health checks, and modular routing.
"""

import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pathlib import Path
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db.session import init_db
from app.api.routes.data import router as data_router
from app.api.routes.chat import router as chat_router
from app.api.routes.ui import router as ui_router
from app.alerts.router import router as alerts_router
from app.voice.router import router as voice_router
from app.climate.router import router as climate_router

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("weathergpt")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing WeatherGPT services...")
    await init_db()
    logger.info("WeatherGPT backend initialized and ready.")
    yield
    logger.info("Shutting down WeatherGPT backend.")


app = FastAPI(
    title="WeatherGPT Intelligence Platform API",
    description="Conversational, multilingual weather intelligence platform for India with grounded data ingestion.",
    version="0.1.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Measures and logs API response latency on every request."""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"
    logger.info(f"{request.method} {request.url.path} completed in {process_time_ms:.2f}ms with status {response.status_code}")
    return response


# Mount static assets
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health", tags=["system"])
async def health_check():
    """System health check and dependency status."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "env": settings.APP_ENV,
        "database": "sqlite_fallback" if "sqlite" in settings.DATABASE_URL else "postgres_active",
        "llm_provider": settings.LLM_PROVIDER,
        "timestamp": time.time()
    }


# Include Routers
app.include_router(data_router)
app.include_router(chat_router)
app.include_router(alerts_router)
app.include_router(voice_router)
app.include_router(climate_router)
app.include_router(ui_router)



