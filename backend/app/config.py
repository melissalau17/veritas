import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

# Read-only bundled files
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

# Ephemeral writable storage
TMP_DIR = Path("/tmp/verimaint")
UPLOADS_DIR = TMP_DIR / "uploads"
MASKS_DIR = TMP_DIR / "masks"


def ensure_temp_dirs() -> None:
    """Create temporary directories for the current Worker execution."""
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    MASKS_DIR.mkdir(parents=True, exist_ok=True)


try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass


def get_setting(name: str, default: str = "") -> str:
    try:
        from workers import env
    except ImportError:
        return os.getenv(name, default)

    value = getattr(env, name, None)
    if value is not None:
        return str(value)
    return os.getenv(name, default)


class Settings:
    MODEL_API_KEY = (
        get_setting("MODEL_API_KEY")
        or get_setting("BASETEN_API_KEY")
    )

    MODEL_BASE_URL = get_setting(
        "MODEL_BASE_URL",
        "https://inference.baseten.co/v1",
    )

    MODEL_NAME = get_setting(
        "MODEL_NAME",
        "meta-models/muse-spark-open-1026",
    )

    META_API_KEY = get_setting("META_API_KEY")

    META_MODEL_BASE_URL = get_setting(
        "META_MODEL_BASE_URL",
        "https://api.meta.ai/v1",
    )

    SAM_MODEL = get_setting(
        "SAM_MODEL",
        "sam-3.1",
    )

    DEMO_MODE = (
        get_setting("DEMO_MODE", "true").lower()
        in ("true", "1", "yes")
    )

    FRONTEND_ORIGIN = get_setting(
        "FRONTEND_ORIGIN",
        "",
    )

    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "https://veritas-api.melissalau17300.workers.dev"
    ]


settings = Settings()

if settings.FRONTEND_ORIGIN:
    settings.ALLOWED_ORIGINS.append(settings.FRONTEND_ORIGIN)