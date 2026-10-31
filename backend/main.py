"""
Veritas FastAPI Backend — Entry Point

Run with:
    cd backend
    python -m uvicorn main:app --reload --port 8000

Or:
    python main.py
"""

import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings, MEDIA_DIR, ASSETS_DIR
from api.investigations import router as investigations_router
from api.vision import router as vision_router


def _configure_logging() -> None:
    """Set up simple structured logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    _configure_logging()

    app = FastAPI(
        title="Veritas",
        description="Engineering Verification Agent — Backend API",
        version="0.1.0",
    )

    # ── CORS (permissive for local engineering & demo environments) ──
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routes ───────────────────────────────────────────
    app.include_router(investigations_router, prefix="/api")
    app.include_router(vision_router, prefix="/api")

    # ── Static Media (Uploads & Generated Masks) ─────────
    app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

