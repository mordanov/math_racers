# Implementation Plan: Infrastructure Setup

**Branch**: `001-infrastructure-setup` | **Date**: 2026-08-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-infrastructure-setup/spec.md`

## Summary

Establish the complete deployment, CI/CD, secrets, networking, TLS, database
migration, backup, and observability infrastructure for Math Racers. This is
Phase 1 of the build order — every subsequent phase depends on this foundation
being stable and reproducible. The approach uses Docker Compose for local and
production deployment, GitHub Actions for the CI/CD pipeline, Alembic for
schema migrations, and structured JSON logging throughout.

## Technical Context

**Language/Version**: Python 3.12 (backend); Node 20 LTS (frontend); Bash (scripts)
**Primary Dependencies**: Docker Compose v2; FastAPI; Alembic; PostgreSQL 16; Redis 7; Nginx 1.27; uv (Python); pnpm (Node); GitHub Actions
**Storage**: PostgreSQL 16 (primary); Redis 7 (job queue + cache); S3-compatible object storage (assets)
**Testing**: pytest (Python unit + integration); vitest (Node unit); Docker Compose for integration test environment
**Target Platform**: Linux container (production); macOS/Linux developer workstation (local)
**Project Type**: web-service (backend API + frontend SPA, containerised)
**Performance Goals**: Backend startup < 3 s; health endpoint < 100 ms; CI pipeline < 10 min end-to-end
**Constraints**: No service has a publicly accessible port except Nginx; secrets never in VCS; `latest` tag never in production
**Scale/Scope**: Single-region deployment; typical consumer-grade server hardware; v1.0 user base

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| IV. Architecture — modular monolith, clear boundaries | ✅ Pass | Docker Compose services map to backend / worker / postgres / redis / nginx; no new architectural layers introduced |
| V. Documentation First | ✅ Pass | spec-infrastructure.md and spec-backend-foundation.md are authoritative; plan follows documented decisions |
| VI. Simplicity | ✅ Pass | No abstractions beyond what the spec requires; Docker Compose is the simplest viable deployment unit |
| IX. Backend Principles — business logic not in controllers | ✅ Pass | Infrastructure layer contains no business logic |
| XIV. Data Ownership — migrations via Alembic | ✅ Pass | All schema changes through Alembic; no manual DDL |
| XV. Security — secrets via env, least privilege | ✅ Pass | Secrets injected at runtime; each service account is scoped to its own resources |
| XVIII. Testing — every feature has automated tests | ✅ Pass | CI pipeline enforces unit + integration tests before any merge |
| XXI. Logging — structured, no sensitive data | ✅ Pass | Structured JSON logging with required fields; PII/secrets excluded |
| XXII. Versioning — immutable image tags | ✅ Pass | Git SHA used as image tag; `latest` excluded from production |

**Post-Phase-0 re-check**: No violations found after research phase. Proceed.

## Project Structure

### Documentation (this feature)

```text
specs/001-infrastructure-setup/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── health-api.md    # Health endpoint contract
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
docker-compose.yml                  # Service definitions (all 5 services)
docker-compose.override.yml         # Local dev overrides (published ports, hot-reload)
.env.example                        # Secret template (committed); .env (not committed)
Makefile                            # Developer shortcuts: make up, make ci, make migrate

backend/
├── Dockerfile
├── pyproject.toml
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/
├── app/
│   └── ...                         # Domain modules (spec-backend-foundation.md)
└── infrastructure/
    ├── config.py                   # Pydantic BaseSettings
    └── logging.py                  # Structured JSON logging

frontend/
├── Dockerfile
├── package.json
└── src/
    └── ...

nginx/
├── nginx.conf
└── conf.d/
    └── default.conf

.github/
└── workflows/
    └── ci.yml                      # 9-step CI/CD pipeline

scripts/
└── backup/
    └── pg-backup.sh                # Daily PostgreSQL backup script
```

## Complexity Tracking

No constitution violations requiring justification.

## Design Decisions

All decisions derived from spec-infrastructure.md (authoritative) and confirmed
by research.md. Recorded here for traceability.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Compose version | Docker Compose v2 (`docker compose`) | Plugin-based v2 is the current standard; v1 (`docker-compose`) is deprecated |
| Python package manager | uv | Specified in CI pipeline (spec §CI step 1); significantly faster than pip |
| Node package manager | pnpm | Specified in CI pipeline; disk-efficient, fast |
| Migration runner | Alembic | Specified in spec-backend-foundation.md and spec-infrastructure.md §Migration Policy |
| TLS termination | Nginx | Specified in spec-infrastructure.md §TLS; Nginx is the only externally exposed service |
| Secret injection | Runtime env vars | Specified in spec-infrastructure.md §Secrets Management |
| Image tag | Git SHA | Specified in spec-infrastructure.md §Edge Case 4; `latest` prohibited in production |
| CI platform | GitHub Actions | Consistent with existing repo hosting; no additional tooling required |
| Log format | JSON (structured) | Specified in spec-infrastructure.md §Observability |
