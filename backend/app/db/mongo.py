# ruff: noqa: E501

from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Any

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection
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


def event_collection() -> Collection[dict[str, Any]]:
    settings = get_settings()
    collection = get_mongodb_client()[settings.mongodb_database]["wildlife_events"]
    collection.create_index("dedupe_key", unique=True, name="uq_event_dedupe_key")
    collection.create_index([("occurred_at", DESCENDING)], name="ix_event_occurred_at")
    collection.create_index(
        [("zone_code", ASCENDING), ("occurred_at", DESCENDING)], name="ix_event_zone_time"
    )
    return collection


def seed_demo_events(collection: Collection[dict[str, Any]]) -> None:
    if collection.estimated_document_count() > 0:
        return
    now = datetime.now(UTC)
    collection.insert_many(
        [
            {
                "event_id": "EVT-OOTY-001",
                "event_type": "wildlife_sighting",
                "source_type": "camera",
                "source_id": "CAM-NORTH-04",
                "zone_code": "ooty-north-monitoring",
                "occurred_at": now - timedelta(minutes=18),
                "received_at": now - timedelta(minutes=17),
                "severity": "info",
                "dedupe_key": "CAM-NORTH-04:001",
                "payload": {"species": "Nilgiri langur", "count": 3, "confidence": 0.94},
            },
            {
                "event_id": "EVT-OOTY-002",
                "event_type": "sensor_reading",
                "source_type": "weather_station",
                "source_id": "WX-LOVEDALE-01",
                "zone_code": "lovedale-patrol-sector",
                "occurred_at": now - timedelta(hours=1),
                "received_at": now - timedelta(hours=1),
                "severity": "info",
                "dedupe_key": "WX-LOVEDALE-01:001",
                "payload": {"temperature_c": 14.8, "humidity_pct": 82, "battery_pct": 76},
            },
            {
                "event_id": "EVT-OOTY-003",
                "event_type": "boundary_crossing",
                "source_type": "tag",
                "source_id": "TAG-AE-044",
                "zone_code": "doddabetta-conservation",
                "occurred_at": now - timedelta(hours=2),
                "received_at": now - timedelta(hours=2),
                "severity": "warning",
                "dedupe_key": "TAG-AE-044:001",
                "payload": {
                    "species": "Asian elephant",
                    "direction": "inbound",
                    "confidence": 0.88,
                },
            },
            {
                "event_id": "EVT-OOTY-004",
                "event_type": "acoustic_detection",
                "source_type": "acoustic_sensor",
                "source_id": "MIC-KETTI-02",
                "zone_code": "ketti-monitoring-zone",
                "occurred_at": now - timedelta(hours=3),
                "received_at": now - timedelta(hours=2, minutes=58),
                "severity": "low",
                "dedupe_key": "MIC-KETTI-02:001",
                "payload": {
                    "call_type": "alarm",
                    "species_hint": "Sambar deer",
                    "confidence": 0.71,
                },
            },
        ]
    )


def list_events(
    event_type: str | None = None, zone_code: str | None = None, limit: int = 25
) -> dict[str, Any]:
    collection = event_collection()
    seed_demo_events(collection)
    query: dict[str, Any] = {}
    if event_type:
        query["event_type"] = event_type
    if zone_code:
        query["zone_code"] = zone_code
    events = list(collection.find(query, {"_id": 0}).sort("occurred_at", DESCENDING).limit(limit))
    return {"count": len(events), "events": events}


def insert_event(event: dict[str, Any]) -> dict[str, Any]:
    collection = event_collection()
    document = event.copy()
    collection.insert_one(document)
    document.pop("_id", None)
    return document
