# Data Model: Infrastructure Setup

**Phase**: 1 — Design
**Date**: 2026-08-08
**Feature**: Infrastructure Setup (`specs/001-infrastructure-setup`)

Infrastructure phase does not introduce application domain entities. It
establishes the persistence, queue, and configuration substrate that all
domain entities will use. This document records the structural entities and
configuration schemas for the infrastructure layer.

---

## Configuration Entity (`infrastructure/config.py`)

Managed by Pydantic `BaseSettings`. All values injected via environment
variables. No defaults for secret fields.

| Field | Type | Source | Notes |
|-------|------|--------|-------|
| `DATABASE_URL` | `SecretStr` | Env | PostgreSQL DSN; never logged |
| `REDIS_URL` | `str` | Env | Redis DSN |
| `JWT_SECRET` | `SecretStr` | Env | Signing key; rotation invalidates all sessions |
| `OPENAI_API_KEY` | `SecretStr` | Env | AI provider key; never logged |
| `STORAGE_ENDPOINT` | `str` | Env | S3-compatible endpoint |
| `STORAGE_ACCESS_KEY` | `SecretStr` | Env | Storage credentials |
| `STORAGE_SECRET_KEY` | `SecretStr` | Env | Storage credentials |
| `STORAGE_BUCKET` | `str` | Env | Asset bucket name |
| `ENVIRONMENT` | `str` | Env | `development` / `staging` / `production` |
| `VERSION` | `str` | Env | Git SHA injected at build time |
| `LOG_LEVEL` | `str` | Env | Default: `INFO` |

**Validation rules**:
- `DATABASE_URL` must be a valid PostgreSQL DSN.
- `ENVIRONMENT` must be one of `development`, `staging`, `production`.
- Secret fields must never appear in serialised config output or logs.

---

## Log Entry Schema

Every service emits log entries conforming to this schema (JSON).

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `timestamp` | ISO8601 string | Yes | UTC |
| `level` | string | Yes | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `service` | string | Yes | `backend`, `worker`, `nginx` |
| `request_id` | UUID string | Yes | Correlation identifier; generated per request |
| `message` | string | Yes | Human-readable description |
| `context` | object | No | Structured key-value pairs; never contains secrets |

**Exclusion rules**: `DATABASE_URL`, `JWT_SECRET`, `OPENAI_API_KEY`,
`STORAGE_SECRET_KEY`, `STORAGE_ACCESS_KEY`, any field whose name contains
`password`, `secret`, `token`, or `key` must never appear in `context`.

---

## Health Check Response Schema

`GET /health` returns HTTP 200 on success; HTTP 503 on degraded/unavailable.

```json
{
  "status": "ok | degraded | unavailable",
  "version": "<git-sha>",
  "checks": {
    "database": "ok | unavailable",
    "redis": "ok | unavailable",
    "storage": "ok | unavailable"
  }
}
```

**State rules**:
- `status: ok` — all checks pass.
- `status: degraded` — non-critical check failing (e.g., storage).
- `status: unavailable` — critical check failing (database).
- Backend MUST start and serve `/health` even when storage is unreachable
  (returns `degraded`).
- Backend MUST refuse to start if database is unreachable at startup time.

---

## Alembic Migration Record

Alembic maintains a `alembic_version` table (created by Alembic; not manually
managed) with a single row holding the current revision identifier. No
application code reads or writes this table directly.

**Policy**:
- Every migration file named `<revision>_<slug>.py`.
- Contains `upgrade()` (required) and `downgrade()` (required where practical;
  documented as `# No downgrade — destructive` when impossible).
- Applied automatically on container start via `alembic upgrade head`.
- Backend startup script asserts `alembic current == alembic head`; halts
  with error if mismatch.

---

## Job Queue Entry

Redis is the job queue broker. Jobs are serialised as JSON and pushed to a
named list. The worker pops and processes jobs.

| Field | Type | Notes |
|-------|------|-------|
| `job_id` | UUID | Unique identifier; used for idempotency check |
| `job_type` | string | e.g., `generate_avatar`, `compute_stats` |
| `payload` | object | Job-specific data; no secrets |
| `created_at` | ISO8601 | Enqueue timestamp |
| `attempts` | integer | Retry count; used for dead-letter routing |

**Idempotency**: Before processing, the worker checks whether `job_id` has
already been completed (via PostgreSQL audit record). If so, it logs a skip
event and marks the job as `succeeded` without re-executing.

**Recovery**: On Redis restart, pending jobs are re-queued from a PostgreSQL
`job_audit` table that records all enqueued job IDs and their last known
status. This table is created by the initial migration.

---

## Backup Manifest

Not a database table — a file-system artefact stored alongside each backup.

| Field | Type | Notes |
|-------|------|-------|
| `backup_id` | UUID | Unique per backup run |
| `created_at` | ISO8601 | Backup timestamp |
| `type` | string | `full_dump`, `wal_segment` |
| `source_host` | string | Hostname of the database server |
| `pg_version` | string | PostgreSQL version at backup time |
| `file_path` | string | Relative path within backup storage |
| `checksum_sha256` | string | SHA-256 of the backup file |

Used during restore verification to confirm integrity before data is applied.
