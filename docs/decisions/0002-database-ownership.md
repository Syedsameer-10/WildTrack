# ADR 0002: Polyglot database ownership

- Status: Accepted
- Date: 2026-09-09

## Decision

Use hosted Supabase PostgreSQL/PostGIS as the source of truth for relational, spatial, temporal, and alert data. Use hosted MongoDB Atlas for flexible event documents.

## Consequences

Cross-database writes require correlation IDs and retry handling. MongoDB outages must not invalidate committed tracking observations in PostgreSQL.
