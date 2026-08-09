# Tasks: Infrastructure Setup

**Input**: Design documents from `specs/001-infrastructure-setup/`
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/ ✅ quickstart.md ✅

**Organization**: Tasks are grouped by user story to enable independent
implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on sibling tasks in the same group)
- **[Story]**: US1 – US5 maps to the five user stories in spec.md
- All source paths follow the web-app layout defined in plan.md

---

## Phase 1: Setup

**Purpose**: Repository scaffold — the base that all subsequent phases write into.

- [x] T001 Create top-level directory structure: `backend/`, `frontend/`, `nginx/`, `scripts/backup/`, `.github/workflows/`
- [x] T002 [P] Create `Makefile` with targets: `up`, `down`, `ci`, `fmt-check`, `lint`, `type-check`, `test-unit`, `test-int`, `build`, `security-scan`, `migrate`
- [x] T003 [P] Create `.gitignore` covering `.env`, `__pycache__`, `*.pyc`, `.venv`, `node_modules`, `dist`, `*.egg-info`, `.mypy_cache`
- [x] T004 [P] Create `.env.example` documenting all required environment variables from data-model.md §Configuration Entity with placeholder values and inline descriptions

---

## Phase 2: Foundational

**Purpose**: Blocking prerequisites — Docker Compose, CI pipeline skeleton, and
Alembic bootstrap that all user stories depend on.

- [x] T005 Create `docker-compose.yml` defining all five services (`nginx`, `backend`, `worker`, `postgres`, `redis`) on `math_racers_net` network with health checks and named volumes per spec-infrastructure.md §Docker Compose Services
- [x] T006 Create `docker-compose.override.yml` for local development: expose `backend:8000` and `postgres:5432` on host, enable hot-reload volume mount for `backend/`
- [x] T007 [P] Create `backend/Dockerfile` (multi-stage): builder stage installs dependencies with `uv`; runtime stage copies app; sets `CMD` to `uvicorn app.main:app`; sets `VERSION` build-arg as env var
- [x] T008 [P] Create `frontend/Dockerfile` (multi-stage): build stage runs `pnpm build`; serve stage copies `dist/` into Nginx image
- [x] T009 Create `nginx/nginx.conf` and `nginx/conf.d/default.conf`: HTTP→HTTPS redirect, TLS 1.2+ only, HSTS header (`max-age=63072000; includeSubDomains`), proxy_pass to `backend:8000`, serve static assets directly
- [x] T010 Create `backend/pyproject.toml` with Python 3.12, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, asyncpg, redis-py, pytest, ruff, black, mypy dependencies
- [x] T011 [P] Create `frontend/package.json` with Node 20, Vite, pnpm workspace, ESLint, Prettier, vitest, TypeScript dependencies
- [x] T012 Create `backend/infrastructure/config.py`: Pydantic `BaseSettings` class with all fields from data-model.md §Configuration Entity; SecretStr for secret fields; validation for `ENVIRONMENT` enum and `DATABASE_URL` format
- [x] T013 Create `backend/infrastructure/logging.py`: JSON structured logger emitting all required fields (`timestamp`, `level`, `service`, `request_id`, `message`, `context`); redaction filter blocking fields matching `password|secret|token|key`
- [x] T014 Create `backend/alembic.ini` and `backend/alembic/env.py`: configure async engine from `DATABASE_URL`; auto-import all models for autogenerate
- [x] T015 Create initial Alembic migration in `backend/alembic/versions/0001_initial_schema.py`: creates `job_audit` table (fields: `job_id` UUID PK, `job_type`, `payload` JSONB, `created_at`, `attempts`, `status`); includes `downgrade()`
- [x] T016 Create `backend/app/main.py`: FastAPI app factory; registers `/health` router; adds correlation-ID middleware injecting UUID `request_id` per request; runs `alembic upgrade head` on startup and aborts if schema not current
- [x] T017 Create `.github/workflows/ci.yml`: nine-step pipeline per spec-infrastructure.md §CI/CD Pipeline — install (uv + pnpm), format-check (Black + Prettier), lint (Ruff + ESLint), type-check (mypy + tsc), unit-tests, integration-tests, build-images, security-scan (trivy + pip-audit + npm audit), deploy (default branch only); failing step blocks all subsequent steps

---

## Phase 3: US1 — One-Command Deployment

**Story goal**: Operator runs one command from a clean checkout and all services
start with no manual intervention. Migrations apply automatically.

**Independent test**: `docker compose up` from clean checkout → all 5 services
healthy → `GET /health` returns `{"status":"ok"}`.

- [x] T018 [US1] Implement `GET /health` endpoint in `backend/app/presentation/api/v1/health.py` per contract `contracts/health-api.md`: probe database, redis, storage; return correct HTTP status and JSON schema; respond within 100 ms; no auth required
- [x] T019 [P] [US1] Add Docker Compose health checks for all five services using commands from spec-infrastructure.md §Docker Compose Services: `nginx -t`, `GET /health`, queue probe, `pg_isready`, `redis-cli ping`
- [x] T020 [P] [US1] Write startup guard in `backend/app/main.py` startup event: run `alembic current` → compare with `alembic head` → abort with structured error log if mismatch
- [x] T021 [US1] Write `scripts/docker-verify.sh`: starts stack, polls `/health` until `status=ok` or timeout (60 s), exits non-zero on timeout; used in manual verification step 1 of spec
- [x] T022 [US1] Add `make up` target to `Makefile` that runs `docker compose up -d` and then calls `scripts/docker-verify.sh`

---

## Phase 4: US2 — Automated Quality Gate on Every Commit

**Story goal**: Every commit triggers CI; a violation (lint, test, security)
blocks merge before any image is built.

**Independent test**: Push a branch with a deliberate Ruff error → CI fails at
lint step → no image build occurs.

- [x] T023 [US2] Configure `backend/.ruff.toml` (or `[tool.ruff]` in `pyproject.toml`): enable all standard rule sets; set `line-length = 100`; exclude `alembic/versions/`
- [x] T024 [P] [US2] Configure `backend/pyproject.toml` mypy section: `strict = true`; exclude `alembic/`; add plugin for SQLAlchemy and Pydantic
- [x] T025 [P] [US2] Create `frontend/.eslintrc.json` and `frontend/prettier.config.js` with project-standard rules; add `"typecheck": "tsc --noEmit"` to `package.json` scripts
- [x] T026 [US2] Update `.github/workflows/ci.yml` to enforce step ordering: format-check failure exits immediately; lint failure skips type-check, tests, build; test failure skips build; build failure skips security-scan; deploy runs only on `main` branch and only after security-scan passes
- [x] T027 [P] [US2] Add `git status --porcelain` guard to CI build step: abort image build if working tree is dirty (spec §Edge Case 4)
- [x] T028 [US2] Add `trivy.yaml` configuration in `.github/` specifying severity thresholds (CRITICAL blocks build, HIGH generates warning); configure `pip-audit` and `npm audit` to fail on critical findings

---

## Phase 5: US3 — Secure Secret and Credential Management

**Story goal**: No secret appears in VCS or in any client-facing response;
rotating a secret requires only an infrastructure-level change.

**Independent test**: `git log --all -p | grep -E "password|secret|api_key"` on
the repo produces no real values. Client response inspection reveals no secrets.

- [x] T029 [US3] Add pre-commit hook in `scripts/hooks/pre-commit`: runs `git diff --cached` through a regex scanner blocking patterns matching `sk-[a-zA-Z0-9]{32,}`, `postgres://.*:.*@`, `redis://:.*@`; install hook via `make hooks`
- [x] T030 [P] [US3] Add `Makefile` target `hooks` that symlinks `scripts/hooks/pre-commit` to `.git/hooks/pre-commit` and sets executable bit
- [x] T031 [P] [US3] Verify `backend/infrastructure/logging.py` redaction filter covers all `SecretStr` fields: write unit test in `backend/tests/unit/infrastructure/test_logging.py` asserting no secret field values appear in serialised log output
- [x] T032 [US3] Verify no secret fields leak through FastAPI response serialisation: add `model_config = ConfigDict(json_encoders={SecretStr: lambda v: "***"})` to `Config` BaseSettings and add unit test in `backend/tests/unit/infrastructure/test_config.py`
- [x] T033 [US3] Add CI step in `.github/workflows/ci.yml` to run `grep -rE "(SECRET|PASSWORD|API_KEY)\s*=\s*['\"][^$]" .` and fail on matches (detects hardcoded secrets at CI level)

---

## Phase 6: US4 — Data Backup and Recovery

**Story goal**: Daily automated backup; verified monthly restore; pending jobs
survive a Redis restart.

**Independent test**: Run backup script, drop and recreate the database, run
restore script, confirm row counts match.

- [x] T034 [US4] Create `scripts/backup/pg-backup.sh`: dump database to timestamped gzip file; write backup manifest JSON (fields from data-model.md §Backup Manifest including SHA-256 checksum); upload to object storage; prune backups older than 30 days; exit non-zero on failure
- [x] T035 [P] [US4] Create `scripts/backup/pg-restore.sh`: accept backup file path and target database name; verify SHA-256 checksum; restore via `pg_restore`; print success/failure summary
- [x] T036 [P] [US4] Add `cron`-compatible schedule example to `quickstart.md` §Backup and Restore showing daily backup invocation (e.g., `0 2 * * * /path/to/pg-backup.sh >> /var/log/backup.log 2>&1`)
- [x] T037 [US4] Implement job recovery in `backend/infrastructure/queue/recovery.py`: on startup, query `job_audit` for rows with `status = 'pending'` and `created_at` older than 5 minutes; re-enqueue each to Redis; log count of re-queued jobs
- [x] T038 [US4] Call job recovery in `backend/app/main.py` startup event after migration guard and before accepting traffic

---

## Phase 7: US5 — Operational Visibility and Alerting

**Story goal**: Every log entry has all required fields; alert thresholds are
defined and observable; health endpoint reflects real dependency state.

**Independent test**: Trigger an error condition; inspect log output; confirm
all required fields present and no sensitive data visible.

- [x] T039 [US5] Implement correlation-ID middleware in `backend/app/presentation/api/middleware/correlation_id.py`: generate UUID per request; attach to request state; inject `request_id` into all log entries for the request lifetime
- [x] T040 [P] [US5] Update `backend/infrastructure/logging.py` to accept `request_id` from request context; fall back to a nil UUID for non-request-scoped log entries
- [x] T041 [P] [US5] Add alert threshold constants to `backend/infrastructure/config.py`: `ALERT_ERROR_RATE_THRESHOLD = 0.01`, `ALERT_AI_FAILURE_RATE_THRESHOLD = 0.10`, `ALERT_QUEUE_DEPTH_THRESHOLD = 500`, `ALERT_DB_P95_MS_THRESHOLD = 500`
- [x] T042 [US5] Document alert conditions in `quickstart.md` §Monitoring with the five thresholds from spec-infrastructure.md §Observability; include suggested monitoring setup (Prometheus/Grafana or equivalent pattern)
- [x] T043 [US5] Add integration test in `backend/tests/integration/test_health.py`: starts the full Docker Compose stack; calls `GET /health`; asserts `status=ok`, all checks pass, `version` matches `VERSION` env var, response time < 100 ms

---

## Phase 8: Polish and Cross-Cutting Concerns

**Purpose**: Release criteria, documentation alignment, and final verification.

- [x] T044 [P] Verify `docker-compose.yml` mounts `nginx_certs` volume into nginx container and documents the TLS certificate path expected by `nginx.conf`
- [x] T045 [P] Add `HSTS` header assertion to CI smoke test: after build, start stack and assert `Strict-Transport-Security: max-age=63072000; includeSubDomains` is present in response headers
- [x] T046 [P] Create `scripts/cert-expiry-check.sh`: reads certificate from nginx certs volume; outputs days until expiry; exits non-zero if < 30 days (satisfies spec §Edge Case 6 alert requirement)
- [x] T047 [P] Update `quickstart.md` to add §TLS Certificate Renewal section explaining automated certbot/ACME setup and the 30-day alert
- [x] T048 [P] Add `Makefile` target `release-check` that runs through all items in spec-infrastructure.md §Release Criteria Checklist programmatically where automatable (tests pass, no lint errors, security scan clean, health endpoint ok)
- [x] T049 Update `docs/engineering/spec-infrastructure.md` — mark `## Acceptance Criteria` checkboxes as verified after manual verification steps pass (per constitution §XX Documentation Maintenance)

---

## Dependencies

```
T001 → T005, T007, T008, T009, T010, T011
T005 → T006 → T018, T019, T020, T021
T010 → T012 → T013 → T016
T014 → T015 → T016 → T020
T016 → T017
T017 → T023, T024, T025, T026, T027, T028
T013 → T031 (logging unit test)
T034 → T035
T037 → T038
T016 → T039 → T040
T043 requires T018, T019, T020 (integration test needs full stack)
T049 requires T043 and all manual verification steps
```

**User story independence**:
- US1 (T018–T022) requires Phase 2 foundation.
- US2 (T023–T028) requires Phase 2 foundation; runs independently of US1–US5.
- US3 (T029–T033) requires T013 (logging); independent of US1, US2, US4, US5.
- US4 (T034–T038) requires T015 (job_audit migration) and T016 (app startup); independent of US2, US3, US5.
- US5 (T039–T043) requires T013, T016, T018; integration test T043 depends on US1 stack.

---

## Parallel Execution Examples

**Phase 2 parallelisable group** (after T001):
```
T007 (backend Dockerfile) ║ T008 (frontend Dockerfile) ║ T009 (nginx config)
T012 (config.py)          ║ T013 (logging.py)          ║ T011 (package.json)
T014 (alembic setup)      ║ T004 (.env.example)        ║ T002 (Makefile)
```

**US2 parallelisable group** (after T017):
```
T023 (ruff config) ║ T024 (mypy config) ║ T025 (eslint + prettier)
T027 (dirty-tree guard) ║ T028 (trivy config)
```

**US3 parallelisable group** (after T029):
```
T030 (hooks target) ║ T031 (logging unit test) ║ T032 (config serialisation test)
```

**Phase 8 all parallelisable** (after US1–US5 complete):
```
T044 ║ T045 ║ T046 ║ T047 ║ T048 → T049
```

---

## Implementation Strategy

**MVP scope (deliver US1 first)**:
Complete Phase 1 + Phase 2 + Phase 3 (T001–T022). This produces a running,
health-checked, migration-aware stack — sufficient to validate the deployment
foundation before building the quality gate (US2) and security hardening (US3–US5).

**Incremental delivery order**:
1. Phase 1 + Phase 2 → stack boots (T001–T017)
2. Phase 3 US1 → verified one-command deployment (T018–T022)
3. Phase 4 US2 → CI quality gate enforced (T023–T028)
4. Phase 5 US3 → secrets hardened (T029–T033)
5. Phase 6 US4 → backup and recovery operational (T034–T038)
6. Phase 7 US5 → observability and alerting complete (T039–T043)
7. Phase 8 → polish, release checklist, docs updated (T044–T049)

**Total task count**: 49 tasks
**Tasks per user story**:
- US1: 5 tasks (T018–T022)
- US2: 6 tasks (T023–T028)
- US3: 5 tasks (T029–T033)
- US4: 5 tasks (T034–T038)
- US5: 5 tasks (T039–T043)
- Setup + Foundation: 17 tasks (T001–T017)
- Polish: 6 tasks (T044–T049)
