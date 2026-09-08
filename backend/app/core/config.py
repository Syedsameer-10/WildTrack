import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")


def _cors_origins() -> tuple[str, ...]:
    raw = os.getenv("APP_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return tuple(origin.strip() for origin in raw.split(",") if origin.strip())


@dataclass(frozen=True)
class Settings:
    app_name: str = "WildTrack API"
    environment: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("APP_LOG_LEVEL", "INFO").upper()
    cors_origins: tuple[str, ...] = _cors_origins()
    api_version: str = "v1"
    database_url: str | None = os.getenv("DATABASE_URL")
    database_pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    database_max_overflow: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "5"))
    mongodb_uri: str | None = os.getenv("MONGODB_URI")
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "wildtrack")


@lru_cache
def get_settings() -> Settings:
    return Settings()
