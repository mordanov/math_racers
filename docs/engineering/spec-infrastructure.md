# Infrastructure — Implementation Specification

**Level:** Specification
**Status:** Authoritative
**Source:** ADR-005; speckit_specification.md §21, §80–88; technical-requirements.md
**Parent:** [Epic E6 — Engineering](../prd.md)
**See also:** [spec-backend-foundation.md](spec-backend-foundation.md), [technical-requirements.md](technical-requirements.md), [../../../initial_spec/ADR/ADR-005.md](../../../initial_spec/ADR/ADR-005.md)

---

## Docker Compose Services

| Service | Image | Published Ports | Depends On | Health Check |
|---------|-------|-----------------|-----------|--------------|
| `nginx` | `nginx:1.27-alpine` | `80:80`, `443:443` | `backend` | `nginx -t` |
| `backend` | `math-racers/backend:${VERSION}` | _(internal only)_ | `postgres`, `redis` | `GET /health` → HTTP 200 |
| `worker` | `math-racers/backend:${VERSION}` | _(none)_ | `postgres`, `redis` | Queue connectivity probe |
| `postgres` | `postgres:16-alpine` | _(internal only)_ | — | `pg_isready -U $POSTGRES_USER` |
| `redis` | `redis:7-alpine` | _(internal only)_ | — | `redis-cli ping` |

All services reside on a private Docker network (`math_racers_net`). Only `nginx` is accessible from the host. Backend and worker share the same container image; the worker overrides the container command.

Volumes:
- `postgres_data` — PostgreSQL data directory (named volume, persisted).
- `redis_data` — Redis RDB snapshots (named volume, persisted; data loss is tolerable).
- `nginx_certs` — TLS certificates mounted into the nginx container.

---

## Build Phase Order

Implementation proceeds in the following order. Each phase produces a stable, independently testable artefact before the next begins.

```
Phase 1: Infrastructure
  Docker Compose, CI/CD pipeline, code quality tooling, project scaffold

Phase 2: Backend Foundation
  FastAPI bootstrap, config, DB connection, migrations, auth, health endpoint

Phase 3: Frontend Foundation
  Vite scaffold, design system, shared components, routing, API client

Phase 4: AI Integration
  Prompt Builder, provider adapter, job queue, asset pipeline

Phase 5: Gameplay
  Race engine (browser), math engine, AI opponents, all game modes

Phase 6: Integration
  Connect frontend → backend APIs; verify all end-to-end workflows

Phase 7: Quality
  Load testing, security review, accessibility audit, documentation verification
```

---

## CI/CD Pipeline

Every commit to any branch triggers:

```
1. Install dependencies        (Python: uv; Node: pnpm)
2. Format check                (Black; Prettier --check)
3. Lint                        (Ruff; ESLint)
4. Static analysis             (mypy --strict; tsc --noEmit)
5. Unit tests                  (pytest -m unit; vitest run)
6. Integration tests           (pytest -m integration; requires Docker)
7. Build container images      (docker build)
8. Security scan               (trivy image; pip-audit; npm audit)
9. Deploy                      (only on default branch, after all prior steps pass)
```

A failing step blocks merge. No step may be bypassed without updating this spec and an accompanying ADR.

---

## Secrets Management

- All secrets injected via environment variables at container runtime.
- `.env` files used for local development only; never committed (`!.env.example` is the only committed template).
- Production secrets managed via the deployment platform's secret store (e.g., Docker secrets, Hetzner environment variables).
- Rotation policy: JWT secret rotation immediately invalidates all active sessions (acceptable; see spec-backend-foundation.md §Edge Cases).
- Principle of least privilege: each service account has access only to the resources it directly uses.

---

## Database Migration Policy

- All schema changes via Alembic.
- Every migration has an `upgrade()` and (where practical) a `downgrade()` function.
- Migrations are version-controlled alongside application code.
- Automated on deploy: `alembic upgrade head` runs before the backend starts accepting traffic.
- If `alembic current` does not match `alembic head`, the backend refuses to start (see spec-backend-foundation.md §Edge Cases #3).
- Manual schema modifications on production are prohibited.

---

## Networking Rules

```
Internet → Nginx (80/443) → Backend (internal) → PostgreSQL (internal)
                                               → Redis (internal)
                          → Static assets (served directly by Nginx)

Backend → Worker (via Redis queue, not direct HTTP)
Backend → OpenAI API (egress only)
Backend → Object Storage (egress only)
```

PostgreSQL, Redis, backend, and worker have no publicly accessible ports. All external traffic goes through Nginx.

---

## TLS Requirements

- TLS 1.2 minimum; TLS 1.3 preferred.
- HTTP → HTTPS redirect enforced by Nginx.
- HSTS header: `Strict-Transport-Security: max-age=63072000; includeSubDomains`.
- Certificate renewal: automated (e.g., Let's Encrypt via certbot or Caddy-compatible integration).
- Plain HTTP permitted only for local development (`localhost`).

---

## Backup Requirements

| Target | Frequency | Retention | Verification |
|--------|-----------|-----------|-------------|
| PostgreSQL full dump | Daily | 30 days | Weekly restore test |
| PostgreSQL WAL / incremental | Continuous (where supported) | 7 days | — |
| Object storage | Versioning enabled | Indefinite | Quarterly audit |
| Application configuration | Git repository | Indefinite | CI build |

An untested backup is considered unreliable. Restore procedures must be documented and tested at least monthly.

---

## Observability

Structured log fields on every entry:

```json
{
  "timestamp": "ISO8601",
  "level": "INFO",
  "service": "backend | worker | nginx",
  "request_id": "uuid",
  "message": "...",
  "context": {}
}
```

Sensitive information (passwords, tokens, API keys, PII) must never appear in logs.

Critical alert conditions:
- API error rate > 1% over 5 minutes
- AI generation failure rate > 10% over 15 minutes
- Health endpoint returns non-200
- Worker queue depth > 500 jobs
- Database response time > 500 ms (p95)

---

## Release Criteria Checklist

A release candidate may be created when all of the following are true:

- [ ] All v1.0 features implemented and manually verified.
- [ ] All critical and high defects resolved.
- [ ] Unit, integration, and E2E tests pass in CI.
- [ ] No failing mypy, ESLint, or Ruff checks.
- [ ] Security scan (trivy + pip-audit + npm audit) produces no critical vulnerabilities.
- [ ] Accessibility audit passed (keyboard navigation, contrast, reduced motion).
- [ ] Performance verified: startup < 3 s, race loading < 2 s, 60 FPS on target hardware.
- [ ] Documentation aligned with implementation (Constitution §20, §24.3).
- [ ] Deployment tested on a staging environment identical to production.
- [ ] Backup and restore procedure tested.
- [ ] Runbook documented: deploy, rollback, incident response.

---

## Edge Cases

1. **Deploy with pending migrations + live traffic** — use a rolling deploy pattern: run migrations first on a separate job, then bring up the new backend container. Ensure migrations are backward-compatible with the previous application version.
2. **Redis data loss** — Redis holds the job queue and temporary caches only. On Redis restart, pending jobs are re-queued from PostgreSQL audit records. No application state is permanently lost.
3. **Object storage unreachable at startup** — the backend starts normally; features that require object storage return HTTP 503 with `STORAGE_UNAVAILABLE` code. Avatar generation is queued and retried when storage recovers.
4. **Container image built from dirty working tree** — CI enforces `git status --porcelain` is clean before building release images. Development images may be dirty. Image tag includes git SHA; `latest` is never used for production.
5. **Worker consumes a job that was already completed** — jobs are idempotent. If the job's target state is already achieved (e.g., avatar already generated), the worker logs the skip and marks the job as `succeeded`.
6. **Certificate expiry** — HSTS preloading means an expired certificate causes complete inaccessibility (no HTTP fallback). Certificate renewal must be automated with alerts ≥ 30 days before expiry.

---

## Manual Verification Steps

1. Run `docker compose up` from a clean checkout. Confirm all 5 services start and `GET /health` returns `{"status": "ok"}`.
2. Run `docker compose up` after modifying a database migration. Confirm the migration applies automatically and the backend starts.
3. Set an incorrect `OPENAI_API_KEY`. Start the stack. Confirm the health endpoint reports the backend as `ok` (storage/key issues should not block startup). Attempt avatar generation. Confirm a user-friendly error is returned (not a stack trace).
4. Run the full CI pipeline locally (`make ci`). Confirm all 8 steps pass on a clean branch.
5. Disable the Redis container. Confirm the backend starts and basic API calls succeed. Confirm that avatar generation attempts return HTTP 503 with `QUEUE_UNAVAILABLE`.
6. Simulate a backup restore: dump the PostgreSQL database, drop and recreate it, restore from the dump. Confirm data integrity.
7. Push a commit with a Ruff lint error. Confirm CI fails at the lint step and does not proceed to build images.
8. Deploy the stack with a breaking migration and a compatible migration on the same deploy. Confirm the upgrade applies both migrations in order.

---

## Acceptance Criteria

> **Implementation status**: All items below have been implemented in branch
> `001-infrastructure-setup`. Checkboxes are marked once manual verification
> steps (see §Manual Verification Steps above) have been completed on the
> running stack.

- [x] `docker compose up` starts all services with no manual intervention.
- [x] Database migrations are applied automatically on container start.
- [x] Backend refuses to start if migrations are not current.
- [x] Redis data loss does not corrupt application state or lose race results.
- [x] CI pipeline enforces format, lint, type checking, and tests before any merge.
- [x] Container images use immutable version tags (git SHA or semver); never `latest` in production.
- [x] TLS is enforced in production; HTTP is redirected.
- [ ] Daily database backups are verified via monthly restore tests.
- [x] Structured logs include `request_id` on every entry.
