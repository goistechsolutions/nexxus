# ADR-0002 — Canonical Backend and Migration Strategy

## Status

Accepted

## Date

2026-10-13

## Context

The repository currently contains two overlapping Python application trees:

- A legacy application at the repository root, including `app/`, `migrations/`, `tests/`, `pyproject.toml` and `alembic.ini`.
- The governed foundation under `backend/`, including `backend/app/`, `backend/migrations/`, `backend/tests/`, `backend/pyproject.toml` and `backend/alembic.ini`.

The root tree contains useful authentication, tenant isolation, RBAC and RLS implementation. However, `backend/` contains the newer governed architecture, its own migrations, tests and packaging configuration, and is the application tree targeted by Foundation CI.

Maintaining both trees creates a critical risk of divergent migrations, inconsistent security fixes, ambiguous local execution and CI validation of only one implementation.

## Decision

`backend/` is the canonical application tree for Nexxus.

All new application code, tests, migrations, configuration and operational scripts must target `backend/`.

The following root-level paths are declared legacy and must not receive new features:

- `app/`
- `migrations/`
- `tests/`
- `pyproject.toml`
- `alembic.ini`

Legacy code may be migrated, reimplemented or removed only after equivalent behavior is covered by tests in `backend/tests/`.

## Rules

1. Do not add routes, domain models, schemas, services, migrations or tests to the repository root.
2. Do not create a second FastAPI application, database session factory, Alembic environment or test suite.
3. Migrate useful behavior from the root tree into the backend architecture before removing it.
4. Preserve tenant isolation and RLS guarantees during every migration step.
5. Maintain one Alembic migration graph with exactly one head.
6. CI must validate the canonical backend tree, including linting, unit tests, integration tests and migration checks.

## Target Structure

```text
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── domain/
│   ├── infrastructure/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── migrations/
│   ├── env.py
│   └── versions/
├── tests/
├── pyproject.toml
└── alembic.ini
```

## Migration Sequence

1. Inventory differences between the root application and `backend/`.
2. Validate the Alembic graph in `backend/`.
3. Consolidate migrations into a single linear or explicitly branched-and-merged graph with one head.
4. Migrate authentication, refresh-token, logout, RBAC and RLS behavior into `backend/`.
5. Migrate and enable security and RLS isolation tests.
6. Add PostgreSQL integration tests using a disposable database with pgvector.
7. Remove root-level legacy application files only after backend tests cover the migrated behavior.

## Consequences

- Developers must work exclusively inside `backend/` for backend changes.
- The repository will temporarily contain legacy files while migration is in progress.
- CI coverage must expand progressively until it validates the complete canonical application.
- The legacy root tree must not be used for deployment, local execution or new feature development.
