# Research: Backend Foundation

**Branch**: `002-backend-foundation` | **Date**: 2026-08-09
**Phase**: 0 — Technical decisions

---

## Decision 1: JWT Library

**Decision**: Use `PyJWT[crypto]>=2.13.0`

**Rationale**:
- `python-jose` carries four CVEs as of 2026 (including CVE-2024-33663 critical algorithm-confusion attack and a `alg=none` bypass). Its `ecdsa` dependency is unpatched and its `rsa` dependency was retired.
- `PyJWT` 2.13.0 (May 2026) is actively maintained, has no active CVEs, and is now the library FastAPI's own documentation examples use.
- `PyJWT[crypto]` pulls only the PyCA `cryptography` package as an extra; no abandoned sub-dependencies.

**Alternatives considered**:
- `python-jose[cryptography]` — rejected due to multiple unpatched CVEs and stale maintenance.

---

## Decision 2: Password Hashing

**Decision**: Use `bcrypt>=4.2.0` via the `bcrypt` PyPI package directly (not passlib)

**Rationale**:
- `passlib` is unmaintained (last release 2020, deprecated in 2024). Its `passlib.context` abstraction adds no value for a single-algorithm project.
- `bcrypt` 4.x (Rust-backed) is actively maintained, fast, and straightforward to use.
- Work factor 12 is the accepted default for web applications in 2026 (balances security and ~250ms per hash on typical cloud hardware).

**Alternatives considered**:
- `passlib[bcrypt]` — rejected due to deprecation warnings and no active maintenance.
- `argon2-cffi` — valid alternative but introduces a C dependency; bcrypt is simpler and sufficient for this use case.

---

## Decision 3: Account Role and Approval State Storage

**Decision**: Store `role` (enum: `parent`, `administrator`) and `approval_status` (enum: `pending`, `approved`, `rejected`) as nullable-false VARCHAR columns with CHECK constraints on the `accounts` table. Use Python `StrEnum` for type safety.

**Rationale**:
- PostgreSQL CHECK constraints enforce valid values at the DB layer — no invalid states can be written even by direct SQL.
- `StrEnum` values are stored as human-readable strings (not integers), making the DB directly queryable without joins.
- No separate roles or permissions table needed: the two-role model (parent/administrator) is simple and stable; a full RBAC table would be premature.

**Alternatives considered**:
- PostgreSQL native ENUM type — rejected because altering a PG enum type requires a migration that cannot be rolled back transactionally.
- Separate `roles` table — rejected as YAGNI for a two-role model.

---

## Decision 4: Administrator Seeding Strategy

**Decision**: On every application startup, after migrations run, check whether any administrator account exists. If none exists, create one from `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables. The check is idempotent — running on every startup is safe and ensures the invariant holds after a clean DB reset.

**Rationale**:
- Putting seeding in an Alembic migration would tie admin credentials to a schema version (wrong layer). Alembic manages schema, not runtime data.
- An explicit startup hook (in the FastAPI lifespan, after `_run_migrations()`) is the correct layer. The check is cheap — one `SELECT COUNT(*)`.
- Failing startup if `ADMIN_EMAIL`/`ADMIN_PASSWORD` env vars are absent is correct: the service must not start without the ability to enforce the minimum-one-admin invariant.

**Alternatives considered**:
- Alembic data migration — rejected: mixes credentials with schema versioning; breaks `alembic downgrade`.
- CLI management command — rejected: too easy to forget in fresh deployments; startup guarantee is stronger.

---

## Decision 5: Minimum-One-Administrator Enforcement

**Decision**: Enforce at the application-service layer (Python), not via DB trigger. The administrator deletion/demotion path queries `SELECT COUNT(*) WHERE role = 'administrator' AND approval_status = 'approved'` before committing the change. If count would become 0, raise a `DomainError` and reject the operation.

**Rationale**:
- DB triggers are harder to test, version, and reason about in a Python-first codebase.
- The constraint is a business rule (belongs in domain service), not a relational integrity rule (belongs in DB).
- Seeding guarantees at least one admin exists on startup; the deletion guard ensures it stays true at runtime.

**Alternatives considered**:
- PostgreSQL trigger — rejected: untestable in unit tests, invisible to application-layer logic.
- DB CHECK constraint on row count — not possible in standard SQL without a trigger.

---

## Decision 6: Approval-Gated Login Response

**Decision**: Return HTTP 403 with error code `ACCOUNT_PENDING` or `ACCOUNT_REJECTED` (not 401). Use 403 rather than 401 because the credentials are valid — the account simply lacks authorisation to access the system.

**Rationale**:
- HTTP 401 semantically means "unauthenticated" (credentials missing or invalid). Using it for a pending account would mislead clients into retrying with different credentials.
- HTTP 403 means "authenticated but not authorised" — accurate for a pending/rejected account.
- Distinct error codes (`ACCOUNT_PENDING` vs `ACCOUNT_REJECTED`) allow the frontend to present contextually correct messages without parsing response bodies.

**Alternatives considered**:
- HTTP 401 for all login failures — rejected: semantically incorrect; would also require the client to distinguish pending vs bad-credentials by parsing the body, not the status code.

---

## Decision 7: Rate Limiting on Auth Endpoints

**Decision**: Defer to a middleware concern (not implemented in this feature). The spec's FR-016 and the technical-requirements security section both call for rate limiting on authentication endpoints. Implementation belongs in the `presentation/api/middleware/` layer as a separate task. This research notes the requirement for the tasks phase.

**Rationale**: Rate limiting depends on Redis, which is already in the stack. The simplest approach is a sliding-window counter keyed by IP + endpoint. However, implementing this correctly (including distributed rate limiting across multiple uvicorn workers) is a non-trivial middleware task. Scoping it out of this feature's MVP to avoid blocking the core auth flow is acceptable per the spec's priority ordering.

---

## Existing Backend — What Is Already Built

The infrastructure sprint (001) delivered the following, all of which this feature builds on:

| Component | Status | File |
|---|---|---|
| Pydantic config (`Config`) | Done | `infrastructure/config.py` |
| Structured JSON logging | Done | `infrastructure/logging.py` |
| Correlation ID middleware | Done | `app/presentation/api/middleware/correlation_id.py` |
| Health endpoint | Done | `app/presentation/api/v1/health.py` |
| Alembic setup + async env | Done | `backend/alembic/env.py` |
| Initial migration (job_audit) | Done | `alembic/versions/0001_initial_schema.py` |
| Worker loop (Redis BLPOP) | Done | `app/worker.py` |
| Job recovery on startup | Done | `infrastructure/queue/recovery.py` |
| FastAPI app factory | Done | `app/main.py` |

**New environment variables required** (to add to `Config`):

| Variable | Required | Notes |
|---|---|---|
| `ADMIN_EMAIL` | Yes — no default | Seeded administrator email |
| `ADMIN_PASSWORD` | Yes — no default | Seeded administrator password (hashed on first write) |
| `JWT_ACCESS_TTL_MINUTES` | No — default 15 | Access token TTL |
| `JWT_REFRESH_TTL_DAYS` | No — default 30 | Refresh token TTL |
