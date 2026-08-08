# Research: Infrastructure Setup

**Phase**: 0 — Pre-design research
**Date**: 2026-08-08
**Feature**: Infrastructure Setup (`specs/001-infrastructure-setup`)

All decisions are constrained by `docs/engineering/spec-infrastructure.md`
(authoritative). This document records rationale and alternatives considered
for the choices that required disambiguation.

---

## Docker Compose Service Layout

**Decision**: Use Docker Compose v2 plugin (`docker compose`) with five services:
`nginx`, `backend`, `worker`, `postgres`, `redis` on a private network
(`math_racers_net`). Only `nginx` publishes host ports (80, 443).

**Rationale**: Exactly specified in spec-infrastructure.md §Docker Compose
Services. Docker Compose v2 is the current standard (v1 deprecated upstream).
The five-service topology gives independent health-check and restart policies
per service, and a shared image between `backend` and `worker` minimises build
artefacts while allowing different entrypoints.

**Alternatives considered**:
- Docker Swarm / Kubernetes: rejected — over-engineered for single-region v1
  scope; constitution §VI (Simplicity) requires the simplest viable approach.
- Separate images for backend vs worker: rejected — identical code base; the
  worker only overrides the container command.

---

## CI/CD Pipeline

**Decision**: GitHub Actions nine-step pipeline (install → format → lint →
static analysis → unit tests → integration tests → build images → security
scan → deploy on default branch).

**Rationale**: The step order and tooling (uv, pnpm, Black, Prettier, Ruff,
ESLint, mypy --strict, tsc --noEmit, pytest, vitest, docker build, trivy,
pip-audit, npm audit) are exactly specified in spec-infrastructure.md §CI/CD
Pipeline. GitHub Actions requires no additional infrastructure given the
existing GitHub remote.

**Alternatives considered**:
- GitLab CI / CircleCI: rejected — no evidence of non-GitHub remote; switching
  CI platform introduces unnecessary complexity.
- Running integration tests without Docker: rejected — spec explicitly requires
  Docker for integration test step.

---

## Secrets Management

**Decision**: Inject all secrets as environment variables at container runtime.
Commit only `.env.example` with placeholder names. Never commit `.env`.
Production secrets via the deployment platform's secret store.

**Rationale**: Directly specified in spec-infrastructure.md §Secrets Management.
Environment variable injection is the lowest-overhead approach compatible with
all containerised deployment platforms and satisfies constitution §XV (Security
— least privilege, no secrets to client).

**Alternatives considered**:
- HashiCorp Vault: more powerful but introduces an additional managed service
  dependency with no spec requirement for it in v1.
- Build-time ARGs: rejected — bakes secrets into image layers; violates the
  immutability and security principles.

---

## Database Migrations

**Decision**: Alembic with `upgrade()` and `downgrade()` functions per
migration. Migrations run automatically via `alembic upgrade head` before the
backend starts. Backend refuses to start if schema is not current.

**Rationale**: Directly specified in spec-infrastructure.md §Database Migration
Policy and spec-backend-foundation.md. Alembic is the standard migration tool
for SQLAlchemy projects; it integrates with the Pydantic BaseSettings config
pattern used by the backend.

**Alternatives considered**:
- Flyway / Liquibase: JVM-based; incompatible with the Python-first backend
  toolchain.
- Manual SQL scripts: rejected — spec explicitly prohibits manual schema
  modifications on production.

---

## TLS and Nginx Configuration

**Decision**: Nginx handles TLS termination (TLS 1.2 minimum, TLS 1.3
preferred). HTTP → HTTPS redirect enforced. HSTS with `max-age=63072000;
includeSubDomains`. Certificate renewal automated (Let's Encrypt / certbot or
equivalent). Certbot alerts ≥ 30 days before expiry.

**Rationale**: Directly specified in spec-infrastructure.md §TLS Requirements.
Nginx is the only service with public ports. HSTS is required by spec; the
30-day alert threshold is explicitly required in edge case 6 of the spec.

**Alternatives considered**:
- Caddy (automatic HTTPS): simpler certificate management but replaces Nginx
  which is specified; constitution §V (Documentation First) prohibits replacing
  documented choices without ADR update.
- Terminating TLS at application level: rejected — Nginx is the documented
  reverse proxy and TLS terminator.

---

## Observability and Structured Logging

**Decision**: All services emit JSON log entries with fields: `timestamp`
(ISO8601), `level`, `service`, `request_id` (UUID), `message`, `context`.
Sensitive data excluded. Alert thresholds specified in spec.

**Rationale**: Field names and format are exactly specified in
spec-infrastructure.md §Observability. Constitution §XXI requires structured,
meaningful logs with no sensitive data.

**Alert thresholds** (from spec):
- API error rate > 1% over 5 minutes
- AI generation failure rate > 10% over 15 minutes
- Health endpoint non-200
- Worker queue depth > 500 jobs
- Database p95 response time > 500 ms

---

## Backup Strategy

**Decision**: Daily full PostgreSQL dump (retained 30 days); continuous WAL
incremental (retained 7 days); object storage versioning (indefinite). Weekly
restore test for full dumps; monthly restore procedure validation.

**Rationale**: Directly specified in spec-infrastructure.md §Backup
Requirements. The spec states "an untested backup is considered unreliable."

**Alternatives considered**:
- Point-in-time recovery only (no full dumps): rejected — spec requires full
  dumps with explicit retention and restore verification.

---

## Image Tagging

**Decision**: Production images tagged with git SHA. `latest` tag never used
in production. CI enforces `git status --porcelain` is clean before building
release images.

**Rationale**: Directly specified in spec-infrastructure.md §Edge Case 4.
Immutable tags are required by constitution §XXII (Versioning) and
spec-infrastructure.md §Acceptance Criteria.
