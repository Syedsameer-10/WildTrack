# ADR 0001: Deployable monorepo

- Status: Accepted
- Date: 2026-09-09

## Decision

Use one repository with separately deployable frontend, backend, and analytics components. Docker packages services but does not provide service discovery or databases required by production code.

## Consequences

Shared documentation and coordinated changes remain simple. Each component must keep an independent build command, health contract, and environment configuration.

