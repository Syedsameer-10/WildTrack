# ruff: noqa: E501, SIM105, I001
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from pymongo.errors import DuplicateKeyError

from app.core.config import get_settings
from app.db.engine import DatabaseNotConfiguredError
from app.db.mongo import MongoDBNotConfiguredError, insert_event, list_events, mongodb_probe_payload
from app.db.probe import database_probe_payload
from app.db.spatial import managed_areas_feature_collection, query_point
from app.db.temporal import observation_timeline, observation_versions
from app.db.active import evaluate_event, list_alerts

router = APIRouter(prefix="/api/v1")


class EventInput(BaseModel):
    event_id: str
    event_type: str
    source_type: str
    source_id: str
    zone_code: str | None = None
    occurred_at: datetime
    severity: str = "info"
    dedupe_key: str
    payload: dict[str, object] = Field(default_factory=dict)


@router.get("/status", tags=["system"])
async def service_status() -> dict[str, str]:
    settings = get_settings()
    return {
        "service": "wildtrack-api",
        "status": "operational",
        "environment": settings.environment,
        "api_version": settings.api_version,
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }


@router.get("/database/status", tags=["system"])
def database_status() -> dict[str, str | int]:
    try:
        return database_probe_payload()
    except DatabaseNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "database_not_configured",
                "message": "The hosted database connection has not been configured.",
            },
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "database_unavailable",
                "message": "The hosted database did not pass its readiness check.",
            },
        ) from exc


@router.get("/database/mongodb/status", tags=["system"])
def mongodb_status() -> dict[str, str]:
    try:
        return mongodb_probe_payload()
    except MongoDBNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "mongodb_not_configured",
                "message": "The hosted MongoDB connection has not been configured.",
            },
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "mongodb_unavailable",
                "message": "The hosted MongoDB database did not pass its readiness check.",
            },
        ) from exc


@router.get("/events", tags=["nosql"])
def events(
    event_type: Annotated[str | None, Query(max_length=80)] = None,
    zone_code: Annotated[str | None, Query(max_length=100)] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 25,
) -> dict[str, object]:
    try:
        return list_events(event_type=event_type, zone_code=zone_code, limit=limit)
    except MongoDBNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "mongodb_not_configured",
                "message": "Event storage is not configured.",
            },
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "event_query_failed", "message": "The event feed could not be loaded."},
        ) from exc


@router.post("/events", status_code=status.HTTP_201_CREATED, tags=["nosql"])
def create_event(event: EventInput) -> dict[str, object]:
    try:
        document = event.model_dump()
        document["received_at"] = datetime.now(UTC)
        stored = insert_event(document)
        try:
            evaluate_event(document)
        except Exception:
            pass
        return stored
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "duplicate_event",
                "message": "An event with this dedupe key already exists.",
            },
        ) from exc
    except MongoDBNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "mongodb_not_configured",
                "message": "Event storage is not configured.",
            },
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "event_insert_failed", "message": "The event could not be stored."},
        ) from exc


@router.get("/alerts", tags=["active"])
def alerts(limit: Annotated[int, Query(ge=1, le=50)] = 25) -> dict[str, object]:
    try:
        items = list_alerts(limit)
        return {"count": len(items), "alerts": items}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "alerts_unavailable", "message": "Active alerts are not available until the active-rules migration is applied."}) from exc


@router.get("/map/areas", tags=["spatial"])
def map_areas() -> dict[str, object]:
    try:
        return managed_areas_feature_collection()
    except DatabaseNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "database_not_configured",
                "message": "Spatial data is not configured.",
            },
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "spatial_data_unavailable",
                "message": "Spatial data could not be loaded.",
            },
        ) from exc


@router.get("/map/query", tags=["spatial"])
def map_point_query(
    latitude: Annotated[float, Query(ge=-90, le=90)],
    longitude: Annotated[float, Query(ge=-180, le=180)],
) -> dict[str, object]:
    try:
        return query_point(longitude=longitude, latitude=latitude)
    except DatabaseNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "database_not_configured",
                "message": "Spatial data is not configured.",
            },
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "spatial_query_failed",
                "message": "The spatial query could not be completed.",
            },
        ) from exc


@router.get("/observations", tags=["temporal"])
def observations(
    as_of: Annotated[
        datetime | None,
        Query(description="Valid-time snapshot in ISO 8601 format"),
    ] = None,
    system_at: Annotated[
        datetime | None,
        Query(description="Transaction-time snapshot in ISO 8601 format"),
    ] = None,
) -> dict[str, object]:
    try:
        if as_of is not None and as_of.tzinfo is None:
            as_of = as_of.replace(tzinfo=UTC)
        if system_at is not None and system_at.tzinfo is None:
            system_at = system_at.replace(tzinfo=UTC)
        return observation_timeline(valid_at=as_of, system_at=system_at)
    except DatabaseNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "database_not_configured",
                "message": "Temporal data is not configured.",
            },
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "temporal_query_failed",
                "message": "The observation timeline could not be loaded.",
            },
        ) from exc


@router.get("/observations/{observation_key}/versions", tags=["temporal"])
def observation_history(observation_key: str) -> dict[str, object]:
    try:
        versions = observation_versions(observation_key)
        if not versions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Observation not found"
            )
        return {"observation_key": observation_key, "versions": versions}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "temporal_query_failed",
                "message": "Version history could not be loaded.",
            },
        ) from exc
