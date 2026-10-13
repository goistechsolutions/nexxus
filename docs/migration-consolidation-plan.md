# Backend Consolidation Plan

## Objective

Consolidate the Nexxus backend into `backend/` as the single canonical application tree, while preserving functional authentication, tenant isolation, RBAC and RLS behavior from the legacy root implementation.

This plan intentionally avoids deleting the root application before its useful behavior has been migrated and covered by automated tests.

## Current State

- `backend/` contains the governed foundation and is targeted by Foundation CI.
- The repository root contains an additional application tree with authentication, tenant context, RBAC, RLS and migrations.
- The two trees have different internal structures and migration sets.
- `backend/` must become the only executable, testable and deployable backend.

## Phase 1 — Establish Canonical Tree

### Deliverables

- `docs/adr/0002-canonical-backend-and-migration-strategy.md`
- Updated README instructions targeting `backend/`
- CI commands targeting `backend/`

### Acceptance Criteria

- All backend development instructions use `backend/`.
- No new code is added to the root application tree.
- The canonical execution command is:

```bash
cd backend
uvicorn app.main:app --reload
```

## Phase 2 — Inventory and Compatibility

### Deliverables

- A component-by-component inventory of the root application.
- A migration decision for each component: migrate, reimplement or discard.
- A test coverage map for authentication, tenant context, RBAC and RLS.

### Required Inventory Areas

| Root component | Target backend location | Required tests |
|---|---|---|
| `app/api/routes/auth.py` | `backend/app/api/v1/routers/auth.py` | Login, refresh, logout, invalid credentials, expired token |
| `app/api/deps.py` | `backend/app/api/v1/dependencies/security.py` | Tenant mismatch, invalid tenant UUID, inactive user, missing permission |
| `app/core/security.py` | `backend/app/core/security.py` | Token signature, issuer, audience, expiry, token type |
| `app/core/database.py` | `backend/app/infrastructure/database/session.py` | RLS context and transaction rollback |
| `app/models/*` | `backend/app/domain/*` | Persistence and tenant constraints |
| `app/services/auth_service.py` | `backend/app/services/auth_service.py` | Refresh rotation, replay, revocation |
| `migrations/*` | `backend/migrations/versions/*` | Upgrade, downgrade and clean-database migration |
| `tests/*` | `backend/tests/*` | Full suite execution in CI |

## Phase 3 — Migration Graph Consolidation

### Mandatory Validation

Run from the canonical directory:

```bash
cd backend
alembic heads
alembic history --verbose
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

### Acceptance Criteria

- `alembic heads` returns exactly one head.
- No migration has an unresolved parent.
- A clean PostgreSQL database can be migrated from zero to head.
- A one-step downgrade and subsequent upgrade succeed.
- The migration graph is documented.

## Phase 4 — Security and Tenant Isolation Migration

### Deliverables

- JWT authentication implementation in `backend/`.
- Refresh-token rotation and replay protection.
- Logout and token revocation behavior.
- Tenant context validation.
- RLS transaction context.
- RBAC permission checks.

### Required Tests

- Access token accepted only with valid signature, issuer, audience and expiry.
- Refresh token cannot be reused after rotation.
- Revoked or logged-out refresh token is rejected.
- Tenant ID from the JWT must match `X-Tenant-ID`.
- Invalid tenant UUID returns a controlled client error.
- Inactive user cannot authenticate or access protected resources.
- Permission changes are enforced according to the selected token policy.
- Two tenants cannot read, insert, update or delete each other's data.

## Phase 5 — CI Expansion

### Target CI Steps

```bash
cd backend
ruff check .
ruff format --check .
pytest -q
```

### Required Integration Environment

- Disposable PostgreSQL service.
- pgvector extension installed.
- Alembic migrations executed before integration tests.
- Integration tests executed against the migrated database.

### Acceptance Criteria

- CI runs the complete backend test suite.
- CI executes security and RLS isolation tests.
- CI validates migrations from a clean database.
- CI fails when there is more than one Alembic head.

## Phase 6 — Legacy Removal

### Removal Criteria

The following root paths may be removed only after all applicable behavior is migrated and tested in `backend/`:

```text
app/
migrations/
tests/
pyproject.toml
alembic.ini
```

### Removal Checklist

- [ ] Authentication flows are implemented in `backend/`.
- [ ] Refresh-token rotation and revocation are tested.
- [ ] Tenant context and RLS behavior are tested.
- [ ] RBAC permission checks are tested.
- [ ] Migrations are unified with one head.
- [ ] PostgreSQL integration tests pass in CI.
- [ ] README and operational scripts no longer reference the root application.
- [ ] CI validates the complete canonical backend.

## Definition of Done

The consolidation is complete when:

1. `backend/` is the only executable backend.
2. There is one Alembic migration graph with one head.
3. The complete backend test suite runs in CI.
4. Tenant isolation is proven with real PostgreSQL and RLS tests.
5. The legacy root application tree has been removed.
