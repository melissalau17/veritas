"""
VeriMaint FastAPI Backend

Local development:
    uv run uvicorn main:app --reload --port 8000

Cloudflare Worker:
    uv run pywrangler dev
    ./deploy.sh
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from api.investigations import router as investigations_router
from api.vision import router as vision_router


def _configure_logging() -> None:
    """Configure application logging."""

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )


def create_app() -> FastAPI:
    """Create the VeriMaint API."""

    _configure_logging()

    app = FastAPI(
        title="VeriMaint",
        description="Engineering Verification Agent — Backend API",
        version="0.1.0",
    )

    # CORS
    # Add your Cloudflare frontend domain to
    # settings.ALLOWED_ORIGINS later.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check
    @app.get("/api/health")
    async def health():
        return {
            "status": "ok",
            "service": "VeriMaint",
            "version": "0.1.0",
        }

    # API routes
    app.include_router(
        investigations_router,
        prefix="/api",
    )

    app.include_router(
        vision_router,
        prefix="/api",
    )

    return app


app = create_app()


# Only runs when executing:
#
# python main.py
#
# Cloudflare imports `app`, so this block does NOT run
# inside the Worker.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )