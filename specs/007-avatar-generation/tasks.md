# Tasks: Avatar Generation

**Input**: Design documents from `specs/007-avatar-generation/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Note on tests**: Included per Constitution §XVIII (tests mandatory for every feature). Written alongside implementation.

**Organization**: 3 user stories (US1–US3) in priority order after a shared Foundational phase.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: User story this task belongs to

---

## Phase 1: Setup

No new tooling or project scaffolding required. Project structure is in place.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database schema, ORM models, Pydantic schemas, and repository layer that every user story depends on.

**⚠️ CRITICAL**: Complete before any user story phase begins.

- [x] T001 Write Alembic migration for `avatars`, `avatar_portraits`, and `generation_jobs` tables (three-step: create `avatars` without the `active_portrait_id` FK, create `avatar_portraits`, then ALTER `avatars` to add `active_portrait_id` FK) in `backend/alembic/versions/0007_avatars.py`
- [x] T002 [P] Create `backend/app/avatars/` package (`__init__.py`) and SQLAlchemy models (`Avatar`, `AvatarPortrait`, `GenerationJob`) with all columns, constraints, relationships, and cascade rules documented in `data-model.md` in `backend/app/avatars/models.py`
- [x] T003 [P] Create Pydantic schemas (`CreateAvatarRequest` with hex colour regex validators, `AvatarCreationResponse`, `JobStatusResponse`, `AvatarListItem`, `AvatarDetailResponse`, `PatchAvatarRequest`) in `backend/app/avatars/schemas.py`
- [x] T004 Implement `AvatarRepository` (Protocol + `SQLAlchemyAvatarRepository`) with methods: `create`, `get`, `list_by_account`, `update`, `delete`, `create_portrait`, `get_portrait`, `list_portraits`, `create_job`, `get_job`, `count_active_jobs_by_account`, `count_jobs_last_hour_by_account` in `backend/app/avatars/repository.py`

**Checkpoint**: Migration written; models and schemas compile; repository methods stubbed. All user stories can now begin.

---

## Phase 3: User Story 1 — Create a New Avatar (Priority: P1) 🎯 MVP

**Goal**: A child submits the creation form; the system generates a named, personalised portrait and delivers it to the gallery within 30 s.

**Independent Test**: POST `/api/v1/avatars` with species=fox → poll job until `status=complete` → GET avatar → confirm `name`, `biography`, `portrait.full_url`, `prompt_version`, and `model_version` are all non-null.

- [x] T005 [P] [US1] Implement `PromptBuilder` class: `build_character_prompt(metadata, attempt)` → deterministic `VersionedPrompt`; attempt 1 = full variables, attempt 2 = accessories removed, attempt 3 = stricter negative prompt appended; store `prompt_version` constant `"1.0.0"` in `backend/app/avatars/prompt_builder.py`
- [x] T006 [US1] Implement `GenerationService.run(job_id)`: load job → LLM call (character metadata schema) → `PromptBuilder.build_character_prompt` → GPT Image API (1024×1024 PNG transparent) → technical validation gates (dimensions, alpha, file size, non-empty) → on fail retry up to 3 attempts → on pass upload PNG + generate 512/256/128 thumbnails via Pillow + upload thumbnails to S3 → create `AvatarPortrait` row → update `Avatar.active_portrait_id` and `Avatar.status = "published"` → update `GenerationJob.status = "complete"` in `backend/app/avatars/generation_service.py`
- [x] T007 [US1] Register `"avatar_generation"` job type handler in `backend/app/worker.py` `process_job()` dispatch block; handler calls `GenerationService.run(job_id)`
- [x] T008 [US1] Implement `AvatarDomainService.create(account_id, request)`: apply defaults for missing fields → check avatar limit (≤50) → check concurrency limit (≤2 active jobs) → check hourly limit (≤10 per hour) → create `Avatar` row (status=pending) → create `GenerationJob` row (status=queued) → enqueue `{"job_type": "avatar_generation", "job_id": ..., "avatar_id": ...}` to Redis → return `AvatarCreationResponse` in `backend/app/avatars/domain_service.py`
- [x] T009 [US1] Implement `AvatarDomainService.get_job(account_id, avatar_id, job_id)` with ownership check; `AvatarDomainService.get(account_id, avatar_id)` with ownership check and portrait history; `AvatarDomainService.list(account_id)` in `backend/app/avatars/domain_service.py`
- [x] T010 [US1] Implement FastAPI router: `POST /api/v1/avatars`, `GET /api/v1/avatars/{avatar_id}/jobs/{job_id}`, `GET /api/v1/avatars`, `GET /api/v1/avatars/{avatar_id}` with auth dependency (`get_current_account`) in `backend/app/avatars/presentation/api/v1/avatars.py`
- [x] T011 [US1] Register avatars router in `backend/app/main.py` (import from `app.avatars.presentation.api.v1.avatars`)
- [x] T012 [P] [US1] Define TypeScript types: `AvatarCreationRequest`, `AvatarCreationResponse`, `JobStatus`, `JobStatusResponse`, `AvatarListItem`, `AvatarPortrait`, `AvatarDetail` in `frontend/src/engine/avatar/types.ts`
- [x] T013 [P] [US1] Implement frontend avatar API client functions: `createAvatar(request)`, `pollGenerationJob(avatarId, jobId)`, `listAvatars()`, `getAvatar(avatarId)` in `frontend/src/engine/avatar/avatarApi.ts`
- [x] T014 [P] [US1] Unit tests for `PromptBuilder`: same inputs produce identical output (deterministic); attempt 1/2/3 produce different prompts; `prompt_version` is set on every output in `backend/tests/unit/avatars/test_prompt_builder.py`
- [x] T015 [P] [US1] Unit tests for `GenerationService` (mocked LLM and image providers): validation pass → portrait created; dimension failure → retry; 3× failure → job status=failed; thumbnail URLs set after successful upload in `backend/tests/unit/avatars/test_generation_service.py`
- [x] T016 [P] [US1] Unit tests for `AvatarDomainService` create path (mocked repository): defaults applied for missing fields; avatar limit raises `ValidationError` with `AVATAR_LIMIT_REACHED`; concurrency limit raises `429`; hourly limit raises `429`; successful creation returns `AvatarCreationResponse` in `backend/tests/unit/avatars/test_domain_service.py`
- [x] T017 [US1] Integration tests for avatar creation (Quickstart Scenarios 1, 2, 4, 5, 6, 10): happy path create+poll+get, minimal creation with defaults, ownership guard (403/404), avatar limit (422), concurrency limit (429), invalid hex colour (422) in `backend/tests/integration/avatars/test_api_avatars.py`

**Checkpoint**: POST avatar → poll job → GET avatar returns published portrait with all metadata. US1 independently testable.

---

## Phase 4: User Story 2 — Regenerate a Portrait (Priority: P2)

**Goal**: A child triggers regeneration; a new portrait is produced while the original remains accessible in portrait history; character metadata is unchanged.

**Independent Test**: POST `/api/v1/avatars/{id}/regenerate` → poll new job until complete → GET avatar → `active_portrait_id` changed; `portrait_history` contains both versions; `name` and `biography` unchanged.

- [x] T018 [US2] Implement `AvatarDomainService.regenerate(account_id, avatar_id)`: ownership check → `status` must be `published` (not `pending`/`failed`) → check concurrency limit (≤2) → check hourly limit (≤10) → create new `GenerationJob` (status=queued) → enqueue job → return `AvatarCreationResponse` with new `job_id` in `backend/app/avatars/domain_service.py`
- [x] T019 [US2] Implement `POST /api/v1/avatars/{avatar_id}/regenerate` endpoint in `backend/app/avatars/presentation/api/v1/avatars.py`
- [x] T020 [P] [US2] Extend frontend avatar API client with `regeneratePortrait(avatarId)` in `frontend/src/engine/avatar/avatarApi.ts`
- [x] T021 [US2] Integration tests for regeneration (Quickstart Scenario 3): new portrait version created; all previous portrait URLs still accessible; `name`/`biography` unchanged after regeneration; rate limit respected in `backend/tests/integration/avatars/test_api_avatars.py`

**Checkpoint**: Regeneration produces a second portrait version; portrait history intact. US2 independently testable.

---

## Phase 5: User Story 3 — Manage Existing Avatars (Priority: P3)

**Goal**: A child can rename their avatar, mark it as favourite, switch active portrait version, and delete avatars; the gallery reflects all changes immediately.

**Independent Test**: PATCH avatar with `{name: "Zara", is_favourite: true}` → GET → name and favourite flag updated. DELETE → GET → 404.

- [x] T022 [US3] Implement `AvatarDomainService.update(account_id, avatar_id, request)`: ownership check → apply name, `is_favourite`, `active_portrait_id` (validate portrait belongs to this avatar) → return updated `AvatarDetailResponse`; implement `AvatarDomainService.delete(account_id, avatar_id)`: ownership check → hard delete (cascades to portraits and jobs) in `backend/app/avatars/domain_service.py`
- [x] T023 [US3] Implement `PATCH /api/v1/avatars/{avatar_id}` (200) and `DELETE /api/v1/avatars/{avatar_id}` (204) endpoints in `backend/app/avatars/presentation/api/v1/avatars.py`
- [x] T024 [P] [US3] Extend frontend avatar API client with `patchAvatar(avatarId, request)` and `deleteAvatar(avatarId)` in `frontend/src/engine/avatar/avatarApi.ts`
- [x] T025 [US3] Integration tests for avatar management (Quickstart Scenarios 7, 8): rename + set favourite; delete removes avatar from list; PATCH with invalid `active_portrait_id` returns 422; delete of non-existent avatar returns 404 in `backend/tests/integration/avatars/test_api_avatars.py`

**Checkpoint**: Full CRUD on avatar metadata; portrait version switching works. US3 independently testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T026 [P] Create `backend/tests/unit/avatars/__init__.py` and `backend/tests/integration/avatars/__init__.py` (package init files for test discovery — if not already created in T014–T017)
- [x] T027 [P] Mark acceptance criteria checkboxes in `docs/content/spec-avatar-generation.md` once all phases pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 2 (Foundational)**: No dependencies — start immediately
- **Phase 3 (US1)**: Depends on T001–T004 (Foundational); T005 and T012 can start once T002+T003 compile
- **Phase 4 (US2)**: Depends on T008 (AvatarDomainService exists) and T010 (router exists); T018–T021 require Phase 3 complete
- **Phase 5 (US3)**: Depends on T008 (AvatarDomainService exists) and T010 (router exists); T022–T025 require Phase 3 complete
- **Phase 6 (Polish)**: After all desired stories complete

### Within Phase 3 (US1)

- T002, T003, T005, T012 are parallel (different files)
- T004 depends on T002 (models must exist before repository)
- T006 depends on T004 and T005 (repository and PromptBuilder)
- T007 depends on T006 (GenerationService must exist before registering handler)
- T008 depends on T004 (repository needed by DomainService)
- T009 depends on T008 (DomainService class must exist)
- T010 depends on T008, T009 (DomainService methods needed by endpoints)
- T011 depends on T010 (router file must exist)
- T013 depends on T012 (types must exist for API client)
- T014 can run parallel with T006–T011 (different file)
- T015 can run parallel with T006–T011 (different file)
- T016 can run parallel with T006–T011 (different file)
- T017 depends on T011 (router must be registered)

### Parallel Opportunities

```
T002 [avatars/models.py]        ─┐
T003 [avatars/schemas.py]       ─┤→ T004 → T006 → T007
T005 [prompt_builder.py]        ─┘          │
T012 [avatar/types.ts]          ──→ T013    │
                                            ↓
                                T008 → T009 → T010 → T011 → T017
                                │
T014 [test_prompt_builder.py]   ← write alongside T005
T015 [test_generation_service]  ← write alongside T006
T016 [test_domain_service]      ← write alongside T008
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Complete Phase 2 (Foundational)
2. Complete Phase 3 (US1: Create → Generate → Gallery)
3. **Validate**: POST avatar → poll job → GET avatar shows published portrait
4. Stop and demo

### Incremental Delivery

1. Phase 2 → Foundation ready
2. Phase 3 (US1) → Avatar creation complete ✓
3. Phase 4 (US2) → Regeneration complete ✓
4. Phase 5 (US3) → Gallery management complete ✓
5. Phase 6 → Polish ✓

### Parallel Team Strategy

After Phase 2:
- **Backend developer**: T005 → T006 → T007 → T008 → T009 → T010 → T011 → T017 (creation pipeline + API)
- **Frontend developer**: T012 → T013 (avatar types + API client)
- **Test engineer**: T014 → T015 → T016 (unit tests, parallel with implementation)

---

## Notes

- [P] tasks target different files and have no incomplete dependencies — safe to run in parallel
- [Story] label maps each task to its user story for traceability
- T001 (migration) has the circular FK constraint challenge — three-step pattern documented in data-model.md
- T006 (GenerationService) is the highest-complexity task: LLM call, image call, validation, retry, thumbnail generation, S3 upload — allocate extra time
- `prompt_version` and `model_version` must be stored on every `AvatarPortrait` row (Constitution §XXII, Definition of Done)
- Quickstart.md scenarios 1–10 serve as manual end-to-end verification after each phase
- The frontend API client does not call AI providers directly (Constitution §XII, §XIII)
