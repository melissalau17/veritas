"""
Veritas backend configuration.

Loads settings from environment / .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MEDIA_DIR = BASE_DIR / "media"
UPLOADS_DIR = MEDIA_DIR / "uploads"
MASKS_DIR = MEDIA_DIR / "masks"
ASSETS_DIR = BASE_DIR / "assets"

# Ensure directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
MASKS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Load .env if present
_env_path = BASE_DIR / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)


class Settings:
    """Application settings sourced from environment variables."""

    MODEL_API_KEY: str = os.getenv("MODEL_API_KEY", "") or os.getenv("BASETEN_API_KEY", "")
    MODEL_BASE_URL: str = os.getenv("MODEL_BASE_URL", "https://inference.baseten.co/v1")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "meta-models/muse-spark-open-1026")

    # Meta / SAM 3.1 configuration
    META_API_KEY: str = os.getenv("META_API_KEY", "")
    META_MODEL_BASE_URL: str = os.getenv("META_MODEL_BASE_URL", "https://api.meta.ai/v1")
    SAM_MODEL: str = os.getenv("SAM_MODEL", "sam-3.1")

    # Day 4: Demo Mode (preloads flagship scenario assets, controls interactive latency)
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
    ]


settings = Settings()
