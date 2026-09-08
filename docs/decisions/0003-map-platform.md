# ADR 0003: MapLibre with OpenFreeMap

- Status: Accepted
- Date: 2026-09-09

## Decision

Use MapLibre GL JS as the browser renderer and OpenFreeMap as the initial hosted vector basemap. Keep the style URL configurable.

## Consequences

The UI gains vector styling, animation, pitch, and future terrain support. Provider attribution is mandatory. PostGIS, not MapLibre, remains responsible for spatial truth. A future tile provider can be selected without changing domain APIs.

