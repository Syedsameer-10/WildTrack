from unittest.mock import patch

from fastapi.testclient import TestClient

from app.db.engine import DatabaseNotConfiguredError
from app.db.mongo import MongoDBNotConfiguredError
from app.main import app

client = TestClient(app)


def test_health_is_independent_and_healthy() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    assert response.headers["X-Request-ID"]


def test_versioned_status_contract() -> None:
    response = client.get("/api/v1/status", headers={"X-Request-ID": "phase-one-test"})
    body = response.json()
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "phase-one-test"
    assert body["service"] == "wildtrack-api"
    assert body["status"] == "operational"
    assert body["api_version"] == "v1"
    assert body["timestamp"].endswith("Z")


def test_unknown_endpoint_returns_not_found() -> None:
    assert client.get("/api/v1/not-real").status_code == 404


def test_database_readiness_is_separate_from_process_health() -> None:
    with patch(
        "app.api.v1.router.database_probe_payload",
        side_effect=DatabaseNotConfiguredError,
    ):
        response = client.get("/api/v1/database/status")

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "database_not_configured"


def test_mongodb_readiness_is_separate_from_process_health() -> None:
    with patch(
        "app.api.v1.router.mongodb_probe_payload",
        side_effect=MongoDBNotConfiguredError,
    ):
        response = client.get("/api/v1/database/mongodb/status")

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "mongodb_not_configured"


def test_spatial_area_api_has_a_separate_unavailable_state() -> None:
    with patch(
        "app.api.v1.router.managed_areas_feature_collection",
        side_effect=DatabaseNotConfiguredError,
    ):
        response = client.get("/api/v1/map/areas")

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "database_not_configured"


def test_spatial_point_query_validates_coordinates() -> None:
    response = client.get("/api/v1/map/query?latitude=91&longitude=76.7")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "request_validation_failed"


def test_temporal_snapshot_validates_timestamp() -> None:
    response = client.get("/api/v1/observations?as_of=not-a-timestamp")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "request_validation_failed"
