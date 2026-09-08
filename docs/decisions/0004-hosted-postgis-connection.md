# ADR 0004: Hosted PostGIS connection

- Status: Accepted
- Date: 2026-09-09

## Decision

Connect FastAPI to hosted Supabase PostgreSQL through SQLAlchemy's pooled psycopg driver. FastAPI dispatches blocking database endpoints through its worker threadpool. Use a distinct migration URL when Supabase supplies different runtime and session-pooler endpoints. Disable automatic prepared statements for pooler compatibility and keep process health separate from database readiness.

## Consequences

The API can stay alive and report a precise dependency failure while Supabase is unavailable. Synchronous psycopg avoids platform-specific event-loop behaviour on Windows and remains portable to Linux containers. Both URLs are backend-only secrets. Schema changes are bundled with the API image and executed explicitly, never during ordinary application startup.
