from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.core.config import get_settings
from app.db.engine import DatabaseNotConfiguredError
from app.db.mongo import MongoDBNotConfiguredError, mongodb_probe_payload
from app.db.probe import database_probe_payload
from app.db.spatial import managed_areas_feature_collection, query_point

router = APIRouter(prefix="/api/v1")


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
