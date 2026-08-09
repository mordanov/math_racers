# Tasks: Backend Foundation

**Input**: Design documents from `specs/002-backend-foundation/`
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/ ✅ quickstart.md ✅

**Organization**: Tasks grouped by user story for independent implementation and delivery.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add new dependencies and extend configuration so all downstream tasks can proceed.

- [ ] T001 Add `PyJWT[crypto]>=2.13.0` and `bcrypt>=4.2.0` to `[project].dependencies` in `backend/pyproject.toml` and run `uv pip install --system -e ".[dev]"` to update the installed environment
- [ ] T002 Add `ADMIN_EMAIL: SecretStr`, `ADMIN_PASSWORD: SecretStr`, `JWT_ACCESS_TTL_MINUTES: int = 15`, `JWT_REFRESH_TTL_DAYS: int = 30` fields to the `Config` class in `backend/infrastructure/config.py`; both `ADMIN_EMAIL` and `ADMIN_PASSWORD` MUST have no default (startup fails if absent)
- [ ] T003 Create `backend/infrastructure/database/` package: `__init__.py`, `base.py` (SQLAlchemy `DeclarativeBase`), `engine.py` (async engine factory using `Config.DATABASE_URL`), `session.py` (async session FastAPI dependency via `AsyncSession`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared domain error hierarchy and ORM models used by all user stories.

**⚠️ CRITICAL**: No user story can begin until T004–T007 are complete.

- [ ] T004 Create `backend/app/shared/exceptions.py` with the domain error hierarchy: `DomainError` (base), `ValidationError`, `NotFoundError`, `ConflictError`, `PermissionError`, `LastAdministratorError`; register exception handlers in `backend/app/main.py` mapping each subtype to its HTTP status (`ValidationError→422`, `NotFoundError→404`, `ConflictError→409`, `PermissionError→403`, `LastAdministratorError→400`) using the structured body `{"error_code": "...", "message": "...", "request_id": "..."}`
- [ ] T005 [P] Create `backend/app/accounts/models.py` with SQLAlchemy ORM models `Account` (id UUID PK, email VARCHAR(255) unique, password_hash VARCHAR(72), role VARCHAR(20) CHECK IN ('parent','administrator'), approval_status VARCHAR(20) CHECK IN ('pending','approved','rejected'), created_at TIMESTAMPTZ, approved_at TIMESTAMPTZ nullable, approved_by UUID FK nullable) and `RefreshToken` (id UUID PK, account_id UUID FK→accounts ON DELETE CASCADE, token_hash VARCHAR(64) unique, issued_at TIMESTAMPTZ, expires_at TIMESTAMPTZ, revoked_at TIMESTAMPTZ nullable, replaced_by UUID FK self-referential nullable); both extend `Base` from `backend/infrastructure/database/base.py`
- [ ] T006 [P] Create Alembic migration `backend/alembic/versions/0002_accounts_table.py` that creates the `accounts` table with all columns, UNIQUE index on `email`, and INDEX on `(role, approval_status)` and INDEX on `approval_status`
- [ ] T007 Create Alembic migration `backend/alembic/versions/0003_refresh_tokens_table.py` that creates the `refresh_tokens` table with FK to `accounts`, UNIQUE index on `token_hash`, INDEX on `(account_id, revoked_at)`, and INDEX on `expires_at`; set `down_revision = "0002"`

---

## Phase 3: User Story 1 — Account Registration and Administrator Approval (Priority: P1) 🎯 MVP

**Goal**: Complete registration → approval → login → session → refresh → logout cycle. Includes the seeded default administrator so the flow is end-to-end testable from a clean database.

**Independent Test**: Run quickstart.md Scenarios 1 and 2 against a clean stack: seed admin logs in, registers a parent, confirms parent is blocked, approves parent, parent logs in, refresh works, logout invalidates session.

### Implementation for User Story 1

- [ ] T008 [US1] Create `backend/app/accounts/schemas.py` with Pydantic models: `RegisterRequest` (email EmailStr, password str 8–128), `LoginRequest` (email EmailStr, password str), `TokenResponse` (access_token str, token_type str = "bearer"), `AccountResponse` (id UUID, email str, role str, approval_status str, created_at datetime, approved_at datetime|None, approved_by UUID|None)
- [ ] T009 [US1] Create `backend/app/accounts/repository.py` with `AccountRepository` Protocol (get_by_id, get_by_email, save, list_by_status, count_approved_administrators) and `SQLAlchemyAccountRepository` implementing it using `AsyncSession` from `backend/infrastructure/database/session.py`; similarly add `RefreshTokenRepository` Protocol (get_by_hash, save, revoke, revoke_all_for_account) with `SQLAlchemyRefreshTokenRepository`
- [ ] T010 [US1] Create `backend/app/accounts/domain_service.py` with `AccountDomainService`: `hash_password(plain: str) -> str` (bcrypt work factor 12), `verify_password(plain: str, hashed: str) -> bool`, `create_access_token(account_id: UUID, role: str, settings: Config) -> str` (PyJWT HS256, claims: sub, role, iat, exp), `decode_access_token(token: str, settings: Config) -> dict` (raises `PermissionError` on invalid/expired), `generate_refresh_token() -> tuple[str, str]` (returns raw UUID and its SHA-256 hash)
- [ ] T011 [US1] Create `backend/application/register_account.py` with `RegisterAccountUseCase.execute(email, password) -> None`: normalise email to lowercase, check for duplicate via `AccountRepository.get_by_email` (raise `ConflictError` on duplicate), hash password, insert `Account(role='parent', approval_status='pending')`, return no token
- [ ] T012 [US1] Create `backend/application/login.py` with `LoginUseCase.execute(email, password, settings) -> tuple[str, str]` (access_token, raw_refresh_token): fetch account by email (raise generic `PermissionError("INVALID_CREDENTIALS")` if not found — do NOT reveal existence), verify password (same generic error on mismatch), check approval_status and raise `PermissionError("ACCOUNT_PENDING")` or `PermissionError("ACCOUNT_REJECTED")` as appropriate, issue JWT access token and opaque refresh token, persist `RefreshToken` row with hash
- [ ] T013 [US1] Create `backend/application/refresh_token.py` with `RefreshTokenUseCase.execute(raw_token, settings) -> tuple[str, str]`: compute SHA-256 of raw_token, fetch `RefreshToken` by hash (raise `PermissionError("INVALID_REFRESH_TOKEN")` if not found, expired, or revoked), mark old token revoked, insert new `RefreshToken`, issue new JWT access token, return (new_access_token, new_raw_refresh_token)
- [ ] T014 [US1] Create `backend/application/logout.py` with `LogoutUseCase.execute(account_id: UUID) -> None`: call `RefreshTokenRepository.revoke_all_for_account(account_id)`
- [ ] T015 [US1] Create `backend/presentation/api/middleware/auth.py` with `get_current_account(request: Request, settings: Config = Depends(get_config)) -> Account` dependency: extract Bearer token from `Authorization` header (raise `PermissionError("UNAUTHORIZED")` if absent), decode JWT, fetch account by sub UUID (raise `PermissionError` if not found or not approved), inject into request; add `require_administrator(account: Account) -> None` helper that raises `PermissionError("FORBIDDEN")` if role != 'administrator'
- [ ] T016 [US1] Create `backend/presentation/api/v1/auth.py` router (`prefix="/api/v1/auth"`): `POST /register` → `RegisterAccountUseCase`, returns 201; `POST /login` → `LoginUseCase`, returns 200 `TokenResponse` + `Set-Cookie: refresh_token=<raw>; HttpOnly; Secure; SameSite=Lax; Path=/api/v1/auth/refresh; Max-Age=<ttl_seconds>`; `POST /refresh` → reads cookie, `RefreshTokenUseCase`, returns 200 + new Set-Cookie; `POST /logout` → `get_current_account`, `LogoutUseCase`, returns 204 + `Set-Cookie: refresh_token=; Max-Age=0`
- [ ] T017 [US1] Implement `_seed_default_admin()` in `backend/app/main.py`: called in the `startup` lifespan event after `_run_migrations()`; checks `AccountRepository.count_approved_administrators()`, if 0 creates `Account(email=cfg.ADMIN_EMAIL, role='administrator', approval_status='approved')` with hashed `cfg.ADMIN_PASSWORD`; if `ADMIN_EMAIL`/`ADMIN_PASSWORD` absent from config, `sys.exit(1)` with a clear error message
- [ ] T018 [US1] Register the `auth` router in `backend/app/main.py` (`app.include_router(auth_router)`) and register error handlers from T004
- [ ] T019 [US1] Write unit tests in `backend/tests/unit/accounts/test_domain_service.py`: password hash/verify round-trip, JWT encode/decode round-trip, expired token raises PermissionError, invalid signature raises PermissionError
- [ ] T020 [US1] Write unit tests in `backend/tests/unit/application/test_register_account.py`: happy path creates pending account, duplicate email raises ConflictError, email is lowercased
- [ ] T021 [US1] Write unit tests in `backend/tests/unit/application/test_login.py`: approved account returns tokens, pending account raises ACCOUNT_PENDING, rejected account raises ACCOUNT_REJECTED, wrong password raises INVALID_CREDENTIALS, unknown email raises INVALID_CREDENTIALS (same error — no enumeration)
- [ ] T022 [US1] Write integration tests in `backend/tests/integration/test_auth_api.py` covering: `POST /register` → 201, `POST /login` before approval → 403 ACCOUNT_PENDING, approve account (direct DB insert for isolation), `POST /login` → 200 with access_token + Set-Cookie, `POST /refresh` → 200 new tokens, reuse old refresh cookie → 401, `POST /logout` → 204, `POST /refresh` after logout → 401

**Checkpoint**: With T008–T022 complete, quickstart.md Scenarios 1 and 2 pass end-to-end.

---

## Phase 4: User Story 1a — Administrator Account Review (Priority: P1)

**Goal**: Administrator can list accounts by status and approve/reject pending registrations.

**Independent Test**: Seed pending account, list it as admin (returns it), approve it (returns approved status), attempt to approve again (returns 400 INVALID_ACCOUNT_STATE), reject a different pending account, verify rejected login returns ACCOUNT_REJECTED.

- [ ] T023 [US1] Create `backend/application/approve_account.py` with `ApproveAccountUseCase.execute(account_id: UUID, approving_admin_id: UUID) -> Account`: fetch account (raise `NotFoundError` if absent), raise `ValidationError("INVALID_ACCOUNT_STATE")` if not pending, set `approval_status='approved'`, `approved_at=now()`, `approved_by=approving_admin_id`, save and return
- [ ] T024 [US1] Create `backend/application/reject_account.py` with `RejectAccountUseCase.execute(account_id: UUID) -> Account`: fetch account (raise `NotFoundError` if absent), raise `ValidationError("INVALID_ACCOUNT_STATE")` if not pending, set `approval_status='rejected'`, save and return
- [ ] T025 [US1] Create `backend/application/list_accounts.py` with `ListAccountsUseCase.execute(status: str|None, role: str|None, limit: int, offset: int) -> tuple[list[Account], int]` returning matching accounts and total count via `AccountRepository.list_by_status`
- [ ] T026 [US1] Create `backend/presentation/api/v1/admin.py` router (`prefix="/api/v1/admin"`): `GET /accounts` (query params: status, role, limit, offset) → `ListAccountsUseCase`, requires administrator; `POST /accounts/{account_id}/approve` → `ApproveAccountUseCase`, requires administrator; `POST /accounts/{account_id}/reject` → `RejectAccountUseCase`, requires administrator
- [ ] T027 [US1] Register the `admin` router in `backend/app/main.py`
- [ ] T028 [US1] Write unit tests in `backend/tests/unit/application/test_approve_account.py`: happy path sets approved fields, already-approved account raises INVALID_ACCOUNT_STATE, not-found raises NotFoundError
- [ ] T029 [US1] Write integration tests in `backend/tests/integration/test_admin_api.py`: list pending accounts (admin only), non-admin gets 403, unauthenticated gets 401, approve pending → 200, approve again → 400, reject pending → 200, rejected login → 403 ACCOUNT_REJECTED

**Checkpoint**: quickstart.md Scenarios 2 and 3 pass end-to-end.

---

## Phase 5: User Story 2 — Child Profile Access (Priority: P2)

**Goal**: Any protected endpoint validates that a child profile ID in the request belongs to the authenticated parent. Non-parents (administrators) are not subject to child-profile ownership checks.

**Independent Test**: Authenticated parent requests action on own child profile ID → passes validation. Same parent requests action on another account's child profile ID → 403. Unauthenticated request → 401.

*Note*: Child profile creation/management is out of scope for this feature. This story implements the ownership-validation guard only, as a reusable dependency function that downstream domain modules will call.

- [ ] T030 [US2] Create `backend/presentation/api/middleware/child_profile.py` with `require_child_ownership(child_profile_id: UUID, account: Account = Depends(get_current_account)) -> None`: if account.role == 'administrator', allow unconditionally; otherwise query `child_profiles` table (or a stub that always returns False until child profiles are implemented — raise `NotFoundError("child_profile_not_found")` in the stub so the guard is safe by default); document clearly that this guard must be updated when the child profile domain module is built
- [ ] T031 [US2] Write unit tests in `backend/tests/unit/accounts/test_child_profile_guard.py`: administrator passes without ownership check, parent with matching child_profile_id passes, parent with non-matching ID raises PermissionError, unauthenticated raises PermissionError

**Checkpoint**: Child ownership guard exists and is tested; downstream domain tasks can import it.

---

## Phase 6: User Story 3 — Background Job Processing (Priority: P3)

**Goal**: Jobs retry up to 3 times with exponential backoff; permanent failures are persisted; idempotency is enforced. The existing worker loop (sprint 001) is extended with retry logic.

**Independent Test**: Submit a job configured to always fail; confirm `job_audit.attempts` increments; confirm status transitions pending→running→failed→retrying→permanent_failure; confirm resubmitting the same job_id does not re-process.

- [ ] T032 [US3] Create Alembic migration `backend/alembic/versions/0004_job_audit_status_values.py` adding `'retrying'` and `'permanent_failure'` as documented valid values for `job_audit.status` (via a CHECK constraint replacement or comment — PostgreSQL VARCHAR CHECK only; update the constraint in place)
- [ ] T033 [US3] Create `backend/app/shared/job_queue.py` with `enqueue_job(job_id: UUID, job_type: str, payload: dict, session: AsyncSession, redis_client) -> None`: INSERT `job_audit` row with status='pending' (raise `ConflictError` if job_id already exists — idempotency); RPUSH to Redis `job_queue`
- [ ] T034 [US3] Extend `backend/app/worker.py` `process_job()` to: (1) UPDATE `job_audit.status='running'`, `attempts+=1`; (2) call the handler; (3) on success UPDATE `status='succeeded'`; (4) on failure: if attempts < 3 UPDATE `status='retrying'` and re-enqueue with delay (30s/120s/480s via `asyncio.sleep` before RPUSH); if attempts >= 3 UPDATE `status='permanent_failure'`; wrap all DB access in `AsyncSession`
- [ ] T035 [US3] Write unit tests in `backend/tests/unit/application/test_job_queue.py`: enqueue inserts row and pushes to Redis, duplicate job_id raises ConflictError; write retry-logic tests (mock DB + Redis) confirming status transitions and correct retry counts

**Checkpoint**: quickstart.md Scenario (background job) verifiable; job retries observable in `job_audit` table.

---

## Phase 7: User Story 4 — System Health Visibility (Priority: P4)

*The health endpoint already exists (`backend/app/presentation/api/v1/health.py`) and passes CI. This story adds the administrator guard for the detailed internal health view and confirms the startup-failure behaviour is tested.*

**Goal**: Health endpoint accurately reflects real component state; startup fails cleanly on DB unavailability.

**Independent Test**: Call `/health` with DB up → ok; stop DB container → call `/health` → unavailable; confirm HTTP 503; restart DB → degraded/ok restores within 30s.

- [ ] T036 [US4] Write integration tests in `backend/tests/integration/test_health.py` (extending existing): degraded state when only Redis is down (HTTP 200), unavailable state when DB is down (HTTP 503), X-Request-ID present in all health responses; confirm `backend/app/main.py` `_run_migrations()` calls `sys.exit(1)` when DB unreachable at startup (unit test with mocked subprocess)

**Checkpoint**: quickstart.md Scenario 6 passes; health endpoint behaviour fully tested.

---

## Phase 8: User Story 5 — Request Traceability (Priority: P5)

*Correlation ID middleware already exists (`backend/app/presentation/api/middleware/correlation_id.py`) and is registered. This story verifies it propagates to background jobs and adds the missing test coverage.*

**Goal**: Every request has a unique ID in all logs, all background jobs spawned from it, and all error responses.

**Independent Test**: Send request with custom X-Request-ID; verify same ID in response header; verify all log entries for that request carry the same ID.

- [ ] T037 [US5] Extend `backend/app/shared/job_queue.py` `enqueue_job()` to capture `request_id_var.get()` from `backend/infrastructure/logging.py` and include it in the job payload as `"request_id"`; extend `backend/app/worker.py` to call `set_request_id(job["request_id"])` before processing each job so worker logs carry the originating request ID
- [ ] T038 [US5] Write integration tests in `backend/tests/integration/test_correlation_id.py`: request with no X-Request-ID header receives a UUID in the response; request with a valid X-Request-ID receives the same value back; error responses include request_id in body matching the header value

**Checkpoint**: quickstart.md Scenario 7 passes; correlation IDs traceable end-to-end into background jobs.

---

## Phase 9: Polish & Cross-Cutting Concerns

- [ ] T039 [P] Add `ADMIN_EMAIL` and `ADMIN_PASSWORD` with placeholder values to `.env.example` (or equivalent sample env file) so new developers know these variables are required
- [ ] T040 [P] Update `backend/alembic/env.py` to import `Base.metadata` from `backend/infrastructure/database/base.py` and set `target_metadata = Base.metadata` so future `alembic revision --autogenerate` works correctly
- [ ] T041 [P] Run `mypy .` in `backend/` and fix all strict-mode type errors introduced by new modules; ensure `pyproject.toml` `[tool.mypy]` still passes with `strict = true`
- [ ] T042 [P] Run `ruff check .` and `black --check .` in `backend/`; fix any formatting or lint violations in new files
- [ ] T043 Run all tests (`pytest -m unit` and `pytest -m integration`) and confirm all pass; confirm no regressions in existing health and config tests
- [ ] T044 Update `docs/engineering/spec-backend-foundation.md` manual verification steps 1–4 to reference the new auth endpoints and the administrator seeding behaviour now that the implementation is complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Requires Phase 1 complete — BLOCKS all user stories
- **US1 (Phases 3–4)**: Requires Phase 2 complete
- **US2 (Phase 5)**: Requires `get_current_account` from T015 (Phase 3) — start after T015
- **US3 (Phase 6)**: Requires `job_audit` table (migration 0001, Phase 2) and `AsyncSession` (T003); can start after Phase 2
- **US4 (Phase 7)**: Requires health endpoint exists (already done) and `_run_migrations()` (T017 area) — can start after Phase 2
- **US5 (Phase 8)**: Requires `enqueue_job` from T033 (Phase 6) and correlation ID middleware (existing) — start after T033
- **Polish (Phase 9)**: After all user story phases complete

### User Story Dependencies

- **US1 (P1)**: Core blocker — must complete before US2 (auth middleware) and partially before US5 (request tracing through jobs)
- **US1a (P1)**: Depends on US1's `AccountRepository` and auth middleware
- **US2 (P2)**: Depends on `get_current_account` (T015); independently testable
- **US3 (P3)**: Depends on DB session (T003) and job_audit migration (Phase 2); independently testable
- **US4 (P4)**: Depends only on Phase 2; the health endpoint is already functional
- **US5 (P5)**: Depends on T033 (`enqueue_job`); independently testable

### Parallel Opportunities Within User Story 1

```text
After T005 (Account model) and T006/T007 (migrations):
  T008 (schemas)      — parallel
  T009 (repository)   — parallel
  T010 (domain_svc)   — parallel

After T009 and T010:
  T011 (register use case)   — parallel
  T012 (login use case)      — parallel
  T013 (refresh use case)    — parallel
  T014 (logout use case)     — parallel

After T011–T014:
  T015 (auth middleware) → T016 (auth router) → T017 (seeding) → T018 (register router)

Tests T019–T022 can be written in parallel with their corresponding implementation tasks.
```

---

## Parallel Example: User Story 1 (T008–T010)

```text
# After ORM models (T005) are done, launch simultaneously:
Task T008: "Create Pydantic schemas in backend/app/accounts/schemas.py"
Task T009: "Create repository protocol + SQLAlchemy implementation in backend/app/accounts/repository.py"
Task T010: "Create AccountDomainService in backend/app/accounts/domain_service.py"
```

---

## Implementation Strategy

### MVP: User Story 1 + 1a Only

1. Complete Phase 1: Setup (T001–T003)
2. Complete Phase 2: Foundational (T004–T007)
3. Complete Phase 3: US1 registration/login (T008–T022)
4. Complete Phase 4: US1a admin review (T023–T029)
5. **STOP and VALIDATE**: Run quickstart.md Scenarios 1–5; run full test suite
6. Deploy — the platform has working accounts, auth, and admin approval

### Incremental Delivery After MVP

- Add US2 (child profile guard) — one task, independently testable
- Add US3 (job retry logic) — extends existing worker
- Add US4 (health test coverage) — verification only, endpoint already exists
- Add US5 (correlation ID in jobs) — two tasks, no breaking changes

---

## Notes

- `[P]` tasks operate on different files and have no incomplete predecessors — safe to run in parallel
- Each phase ends with a verifiable checkpoint matching a quickstart.md scenario
- Migrations 0002 and 0003 must be applied before any account integration test runs — the CI `Start backend for integration tests` step handles this via `_run_migrations()` at startup
- The child profile guard (T030) is intentionally a safe stub — it raises `NotFoundError` by default until the child profile domain module is built in a later feature
- bcrypt work factor 12 ≈ 250ms per hash on typical CI hardware — integration tests that call `/register` and `/login` will be slow; this is expected and acceptable
