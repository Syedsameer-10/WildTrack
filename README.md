# WildTrack

WildTrack is an advanced-database wildlife monitoring platform built around spatial, temporal, active, event-driven, and NoSQL database concepts. The first study area will be a clearly labelled synthetic reserve near Ooty, Tamil Nadu.

## Current status

Phase 1 provides a runnable React/TypeScript frontend and FastAPI backend with health checks, failure-state UI, Docker-safe packaging, and cloud deployment definitions.

## Planned deployed system

| Responsibility | Technology |
|---|---|
| Web interface | React, TypeScript, Vite |
| Interactive map | MapLibre GL JS with OpenStreetMap tiles |
| API and live updates | FastAPI and WebSockets |
| Relational, spatial, temporal, active data | Hosted Supabase PostgreSQL with PostGIS |
| Flexible event documents | Hosted MongoDB Atlas |
| Authentication | Supabase Auth, added after core features |

## Repository layout

```text
frontend/                 Browser application
backend/                  API and domain services
database/migrations/      Versioned PostgreSQL changes
database/seeds/           Repeatable demonstration data
infrastructure/           Docker and deployment definitions
docs/                     Architecture, decisions and contracts
```

The document-generation files at the repository root are retained as project artifacts and are independent of the application.

## Configuration

Copy `.env.example` to `.env` only when Phase 1 begins. Real credentials must never be committed. Variables beginning with `VITE_` are exposed to the browser and therefore must not contain database passwords or service-role keys.

## Delivery rules

- Every phase must produce a testable checkpoint.
- The user tests and approves each phase before work proceeds.
- Hosted databases are used from their first implementation phase.
- Database migrations are versioned and repeatable.
- Spatial decisions are made by PostGIS, not by the map UI.
- Docker images remain stateless and configured through environment variables.

See [docs/architecture.md](docs/architecture.md), [docs/phase-gates.md](docs/phase-gates.md), and [infrastructure/phase-1.md](infrastructure/phase-1.md).
