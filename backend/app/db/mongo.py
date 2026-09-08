from functools import lru_cache

from pymongo import MongoClient
from pymongo.server_api import ServerApi

from app.core.config import get_settings


class MongoDBNotConfiguredError(RuntimeError):
    """Raised when the hosted MongoDB connection is not configured."""


@lru_cache
def get_mongodb_client() -> MongoClient:
    settings = get_settings()
    if not settings.mongodb_uri:
        raise MongoDBNotConfiguredError("MONGODB_URI has not been configured.")

    return MongoClient(
        settings.mongodb_uri,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=5_000,
        connectTimeoutMS=5_000,
    )


def mongodb_probe_payload() -> dict[str, str]:
    settings = get_settings()
    get_mongodb_client().admin.command("ping")
    return {
        "provider": "mongodb_atlas",
        "status": "ready",
        "database": settings.mongodb_database,
    }
