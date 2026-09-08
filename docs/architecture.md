# WildTrack Architecture

## 1. System boundaries

WildTrack is divided into independently deployable components:

```text
Browser (React + MapLibre)
          |
          | HTTPS / WebSocket
          v
FastAPI application service
     |                    |
     | SQL                | MongoDB protocol
     v                    v
Supabase PostgreSQL       MongoDB Atlas
PostGIS + triggers        Event documents
     ^
     | aggregate writes
Hive analytics worker
```

The frontend never connects directly to either operational database during the pre-authentication phases. FastAPI owns validation, orchestration, and public API contracts.

## 2. Database responsibility matrix

| Concern | System of record | Reason |
|---|---|---|
| Animals, species and devices | PostgreSQL | Relational integrity |
| Forests, zones and positions | PostGIS | Indexed spatial operations |
| Position history and validity periods | PostgreSQL | Temporal querying and constraints |
| ECA rules and authoritative alerts | PostgreSQL triggers/tables | Transactional active-database behaviour |
| Raw and enriched event payloads | MongoDB Atlas | Flexible event shapes |
| Analytics outputs | PostgreSQL aggregate tables | Fast dashboard reads |
| Batch processing | Hive | Historical analytical workloads |

Data is not duplicated without an explicit ownership rule. An alert in PostgreSQL may reference an event document in MongoDB through a correlation ID; PostgreSQL remains authoritative for ranger workflow state.

## 3. Spatial contract

- Stored coordinates use WGS 84 (`SRID 4326`).
- GeoJSON and MapLibre use longitude-latitude order.
- Forest areas and zones are stored as polygon or multipolygon geometries.
- Observations are stored as points with spatial indexes.
- Point-in-zone, containment and distance decisions execute in PostGIS.
- The first Ooty boundary is synthetic and must be labelled as demonstration data.
- Map attribution remains visible.

## 4. Temporal contract

Every position record distinguishes:

- `observed_at`: when the device measured the location.
- `received_at`: when the API received the payload.
- `recorded_at`: when persistence completed.

Historical observations are append-only. Corrections are represented explicitly rather than silently overwriting the original measurement.

## 5. Event and active-database contract

An event has a stable UUID correlation ID. ECA processing separates:

1. Event: a position or device-status change occurs.
2. Condition: a spatial, temporal, or threshold predicate is evaluated.
3. Action: an alert or workflow record is created.

Rules must be idempotent so retrying an input does not create duplicate alerts. Database triggers enforce transactional rules; application services publish live notifications only after successful persistence.

## 6. API contract

- Public endpoints are prefixed with `/api/v1`.
- Health probes use `/health` and do not require a database.
- Readiness probes may validate external dependencies separately.
- JSON property names use `snake_case`.
- Timestamps use ISO 8601 UTC values ending in `Z`.
- Coordinates are represented as GeoJSON wherever practical.
- Errors use a stable shape with `code`, `message`, `details`, and `request_id`.
- List endpoints use bounded pagination.
- Breaking changes require a new API version.

Example error:

```json
{
  "error": {
    "code": "invalid_position",
    "message": "The supplied position is outside valid coordinate ranges.",
    "details": {},
    "request_id": "uuid"
  }
}
```

## 7. Deployment contract

- The frontend compiles to static assets.
- The backend is a stateless container and binds to `0.0.0.0` on the platform-provided port.
- Hosted Supabase and MongoDB endpoints are supplied through secrets.
- Docker Compose is a local convenience, not an application dependency.
- No code relies on Docker-only hostnames such as `db` or `mongo`.
- Database schema changes run as an explicit migration step.
- Long-running simulation and analytics work cannot block API requests.
- Hive failure cannot interrupt live tracking or map reads.
- Each service exposes health information suitable for cloud deployment.

## 8. Security boundaries

- Browser bundles contain no privileged keys.
- Database credentials are backend-only secrets.
- Logs exclude passwords, connection strings, tokens, and precise secrets.
- Inputs are validated at the API and constrained again in the database.
- Authentication is added in a later phase, but the service boundaries already support it.
- CORS uses an explicit allowlist outside local development.

## 9. Testing layers

| Layer | Purpose |
|---|---|
| Unit tests | Domain rules and transformations |
| API tests | Contracts, validation and error handling |
| Migration tests | Repeatability and schema correctness |
| Spatial tests | Boundary, distance and geometry behaviour |
| Temporal tests | Ordering, ranges, late and duplicate observations |
| Integration tests | Supabase, MongoDB and WebSocket flows |
| UI tests | Critical user journeys and failure states |
| Deployment smoke tests | Public frontend, API, map and hosted dependencies |

