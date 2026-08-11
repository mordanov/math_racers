# Implementation Plan: Avatar Generation

**Branch**: `007-avatar-generation` | **Date**: 2026-08-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/007-avatar-generation/spec.md`

## Summary

A child customises a character (species, colours, hairstyle, accessories) and the system generates a unique, AI-powered portrait with a generated name, personality, and biography. Generation runs asynchronously via the existing Redis background worker. The child polls (or receives a WebSocket push) for completion. The feature covers the full lifecycle: create → poll → manage (rename, set favourite, delete, regenerate portrait).

This feature is primarily backend-heavy (async pipeline, LLM + image generation, object storage, job tracking) with a thin frontend API client layer. The Prompt Builder pattern is mandatory per the Constitution and Architecture docs.

---

## Technical Context

**Language/Version**: Python 3.11 (backend) · TypeScript (frontend)
**Primary Dependencies**: FastAPI · SQLAlchemy 2 (async) · asyncpg · Redis (job queue) · OpenAI SDK (LLM + image) · Pillow (image validation) · boto3/aiobotocore (S3-compatible object storage)
**Storage**: PostgreSQL (metadata, job records, prompt records) · S3-compatible object storage (PNG binaries)
**Testing**: pytest + pytest-asyncio (backend unit + integration) · Vitest (frontend unit)
**Target Platform**: Linux server (backend) · Web browser (frontend)
**Project Type**: Web application (existing fullstack monorepo)
**Performance Goals**: Portrait generation completes within 30 s (P95)
**Constraints**: Max 2 concurrent generation jobs per account; max 10 generation attempts per account per hour; max 50 avatars per child profile
**Scale/Scope**: Per-account quota enforcement; multi-attempt retry with escalation

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| §IV Architecture (modular monolith, domain/infra separation) | ✅ PASS | New `app/avatars/` module follows the `app/championships/` pattern; business logic in domain service, not controller |
| §IX Backend Principles (backend owns AI orchestration, asset management) | ✅ PASS | All LLM/image calls in background worker; frontend never touches AI providers |
| §XII AI — Prompt Builder mandatory | ✅ PASS | PromptBuilder class required; hard-coded prompts in application code are prohibited |
| §XIII Image Generation — Art Bible / Prompt Bible compliance | ✅ PASS | Every generated asset must be reproducible from structured metadata; `prompt_version` + `model_version` + `timestamp` stored on every generation record |
| §XIV Data Ownership (backend is source of truth) | ✅ PASS | Avatar metadata and binaries live server-side; frontend has read-only views |
| §XV Security (input validation, auth, sanitisation) | ✅ PASS | Hex colours and user strings sanitised before reaching PromptBuilder; API keys server-side only |
| §XVII Accessibility | ✅ PASS | Must be addressed in frontend creation form (keyboard navigation, alt text) |
| §XVIII Testing (automated tests required) | ✅ PASS | Unit tests for domain logic; integration tests for endpoints and worker pipeline |
| §XXII Versioning (prompts, assets) | ✅ PASS | `prompt_version` and `model_version` on every generation record |
| Non-Negotiable: no prompts outside PromptBuilder | ✅ PASS | PromptBuilder is the single construction path |
| Definition of Done: prompt_version, model_version, generation_date on every portrait | ✅ PASS | Enforced in GenerationJob model and worker |

No gate violations.

---

## Project Structure

### Documentation (this feature)

```text
specs/007-avatar-generation/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/           ← Phase 1 output
│   ├── api-endpoints.md
│   └── job-lifecycle.md
└── tasks.md             ← Phase 2 output (/speckit-tasks)
```

### Source Code (new files in existing monorepo)

```text
backend/
├── app/
│   └── avatars/                        # new module (mirrors app/championships/ pattern)
│       ├── __init__.py
│       ├── models.py                   # Avatar, AvatarPortrait, GenerationJob ORM models
│       ├── schemas.py                  # Pydantic request/response schemas
│       ├── repository.py               # AvatarRepository Protocol + SQLAlchemy impl
│       ├── domain_service.py           # AvatarDomainService (create, get, delete, rename, favourite)
│       ├── generation_service.py       # GenerationService — LLM + PromptBuilder + image + validation
│       ├── prompt_builder.py           # PromptBuilder class (deterministic, versioned)
│       └── presentation/
│           └── api/
│               └── v1/
│                   └── avatars.py      # FastAPI router (7 endpoints)
├── alembic/
│   └── versions/
│       └── 0007_avatars.py             # migration: avatars, avatar_portraits, generation_jobs tables
├── tests/
│   ├── unit/
│   │   └── avatars/
│   │       ├── __init__.py
│   │       ├── test_domain_service.py
│   │       ├── test_generation_service.py
│   │       └── test_prompt_builder.py
│   └── integration/
│       └── avatars/
│           ├── __init__.py
│           └── test_api_avatars.py

frontend/
└── src/
    └── engine/
        └── avatar/                     # new module (mirrors engine/race/ pattern)
            ├── avatarApi.ts            # API client (create, poll job, list, get, patch, delete, regenerate)
            └── types.ts                # TypeScript types for avatars and jobs
```

**Structure Decision**: Single backend module `app/avatars/` following the established `app/championships/` pattern (models → repository → domain_service → presentation router). Background worker job handler registered in `app/worker.py`. Frontend API client module `engine/avatar/` mirrors `engine/race/`.

---

## Phase 0: Research

### Decisions

**Decision 1: LLM provider for character metadata**
- Decision: OpenAI Chat Completions API (`gpt-4o-mini` or equivalent) via `OpenAILLMAdapter`, the existing adapter documented in `docs/ai/ai-architecture.md`.
- Rationale: Already documented as the project adapter; no new dependency.
- Alternatives considered: Anthropic Messages API — rejected; not the documented adapter.

**Decision 2: Image generation provider**
- Decision: GPT Image API via `OpenAIImageAdapter` (1024×1024, PNG, transparent background, high quality).
- Rationale: Mandated by `docs/ai/asset-pipeline.md` and `docs/content/feature-avatar-creation.md`.
- Alternatives considered: DALL-E 3, Midjourney — out of scope; provider abstraction allows swap.

**Decision 3: Async job pattern**
- Decision: Redis queue (`QUEUE_KEY = "job_queue"`) via the existing background worker in `app/worker.py`. Job type: `"avatar_generation"`. The worker dispatches to a registered handler added in `app/avatars/generation_service.py`.
- Rationale: The queue and worker are already in production. Job status polling endpoint already planned in the spec API contract.
- Alternatives considered: Celery — rejected; over-engineering given the existing Redis worker.

**Decision 4: Object storage**
- Decision: S3-compatible storage (existing project infrastructure). Path pattern: `characters/{account_id}/{avatar_id}/v{n}/portrait.png`. Thumbnails: `v{n}/portrait_{size}.png` for 512, 256, 128 variants.
- Rationale: Documented in `docs/ai/asset-pipeline.md` §Step 6.
- Alternatives considered: Store in PostgreSQL as bytea — rejected; Constitution §XIV and pipeline doc both specify object storage for binary assets.

**Decision 5: Portrait version selection**
- Decision: A player selects their "active" portrait version via the `active_portrait_id` foreign key on the `Avatar` table. All previous portrait versions are retained in `avatar_portraits`.
- Rationale: `docs/ai/asset-pipeline.md` §Portrait Versioning: "All versions are stored permanently. The player selects their preferred active version."
- Alternatives considered: Store only one portrait per avatar — rejected by the spec (FR-007) and asset pipeline doc.

**Decision 6: Frontend polling vs. WebSocket**
- Decision: v1 uses polling via `GET /api/v1/avatars/{avatar_id}/jobs/{job_id}`. WebSocket push is noted as a future enhancement.
- Rationale: The existing frontend has no WebSocket infrastructure. Polling is sufficient for the 30 s SLA.
- Alternatives considered: WebSocket push — deferred to v1.5 per the asset pipeline doc.

**Decision 7: Thumbnail generation timing**
- Decision: Thumbnails are generated inside the background worker immediately after the primary portrait passes validation, using Pillow. URLs stored in `avatar_portraits`.
- Rationale: Thumbnail generation must be synchronous with portrait generation to ensure all variants are available before status is set to `published`.
- Alternatives considered: Separate thumbnail job — rejected; adds unnecessary complexity for 3 small resize operations.

**Decision 8: Rate limiting**
- Decision: Concurrency limit (2 simultaneous generation jobs) and hourly limit (10 per hour) are enforced in `AvatarDomainService` by querying `GenerationJob` counts before enqueuing. Hard limits stored as module-level constants.
- Rationale: These are documented in `docs/content/spec-avatar-generation.md`. The backend is the enforcement point per Constitution §XV and §IX.
- Alternatives considered: Redis-level rate limiting — overkill for these low limits; DB query is simple and consistent.

---

## Phase 1: Data Model

See [data-model.md](data-model.md).

### Entities

**Avatar**
- `id` UUID PK
- `account_id` UUID FK → accounts
- `child_profile_id` UUID (child within account — stored as string/UUID; no separate table yet)
- `species` STRING NOT NULL CHECK IN ('fox','rabbit','bear','cat','mouse','panda')
- `fur_color` STRING(7) NOT NULL  — validated hex `#RRGGBB`
- `eye_color` STRING(7) NOT NULL
- `hairstyle` STRING NOT NULL
- `accessories` JSONB default `[]`
- `clothes_top_color` STRING(7) NOT NULL
- `clothes_bottom_color` STRING(7) NOT NULL
- `name` STRING nullable (set after LLM generation)
- `personality` TEXT nullable
- `biography` TEXT nullable
- `appearance_summary` TEXT nullable
- `favorite_subject` STRING nullable
- `running_style` STRING nullable
- `status` STRING CHECK IN ('pending','published','failed') default 'pending'
- `is_favourite` BOOLEAN NOT NULL default false
- `active_portrait_id` UUID FK → avatar_portraits nullable
- `created_at` TIMESTAMP NOT NULL server_default now()
- State transitions: `pending` → `published` (on successful generation) | `failed` (on 3× retry exhaustion)

**AvatarPortrait**
- `id` UUID PK
- `avatar_id` UUID FK → avatars CASCADE DELETE
- `version` INTEGER NOT NULL  — monotonically increasing per avatar
- `prompt_version` STRING NOT NULL
- `model_version` STRING NOT NULL
- `full_url` STRING NOT NULL  — S3 path to 1024×1024 PNG
- `medium_url` STRING NOT NULL  — 512×512
- `small_url` STRING NOT NULL  — 256×256
- `thumb_url` STRING NOT NULL  — 128×128
- `created_at` TIMESTAMP NOT NULL server_default now()
- UNIQUE(`avatar_id`, `version`)

**GenerationJob**
- `id` UUID PK
- `avatar_id` UUID FK → avatars CASCADE DELETE
- `portrait_id` UUID FK → avatar_portraits nullable (set on completion)
- `status` STRING CHECK IN ('queued','llm_running','prompt_building','generating','validating','storing','complete','failed') NOT NULL default 'queued'
- `attempt` INTEGER NOT NULL default 1
- `prompt_version` STRING nullable
- `model_version` STRING nullable
- `error` TEXT nullable
- `created_at` TIMESTAMP NOT NULL server_default now()
- `completed_at` TIMESTAMP nullable

### Constraints
- Max 50 avatars per `account_id`: enforced in `AvatarDomainService.create()` before insert.
- Max 2 concurrent jobs per `account_id`: enforced by querying `GenerationJob` WHERE status NOT IN ('complete', 'failed').
- Max 10 jobs per `account_id` per hour: enforced by querying `GenerationJob` WHERE created_at >= now() - interval '1 hour'.

---

## Phase 1: API Contracts

See [contracts/api-endpoints.md](contracts/api-endpoints.md).

### Endpoints

| Method | Path | Auth | Status Codes | Purpose |
|--------|------|------|--------------|---------|
| POST | `/api/v1/avatars` | Required | 201, 422, 429 | Create avatar, enqueue generation job |
| GET | `/api/v1/avatars/{avatar_id}/jobs/{job_id}` | Required | 200, 404 | Poll job status |
| GET | `/api/v1/avatars` | Required | 200 | List avatars for current account |
| GET | `/api/v1/avatars/{avatar_id}` | Required | 200, 404 | Get single avatar |
| PATCH | `/api/v1/avatars/{avatar_id}` | Required | 200, 404, 422 | Rename or set favourite |
| POST | `/api/v1/avatars/{avatar_id}/regenerate` | Required | 201, 404, 429 | Trigger portrait regeneration |
| DELETE | `/api/v1/avatars/{avatar_id}` | Required | 204, 404 | Delete avatar |

Error codes: `AVATAR_NOT_FOUND`, `JOB_NOT_FOUND`, `AVATAR_LIMIT_REACHED` (50), `CONCURRENCY_LIMIT_REACHED` (2 in-progress jobs), `RATE_LIMIT_EXCEEDED` (10/hr).

---

## Phase 1: Quickstart Scenarios

See [quickstart.md](quickstart.md).

1. **Happy path — create and poll**: POST `/api/v1/avatars` with species=fox → receive `avatar_id + job_id` → poll `GET /jobs/{job_id}` until `status=complete` → GET avatar → confirm name, portrait URLs, prompt_version set.
2. **Minimal creation**: POST with only `species` (all other fields use defaults) → generation completes → avatar published.
3. **Regenerate portrait**: POST `/api/v1/avatars/{id}/regenerate` → second job → GET avatar → `active_portrait_id` updated; old portrait still in portrait history.
4. **Ownership guard**: Account A creates avatar; Account B attempts GET → 403.
5. **Avatar limit**: POST 50 avatars → 51st attempt → 422 `AVATAR_LIMIT_REACHED`.
6. **Concurrency limit**: Enqueue 2 jobs → 3rd creation while both in progress → 429 `CONCURRENCY_LIMIT_REACHED`.
7. **Rename and set favourite**: PATCH `{name: "Zara", is_favourite: true}` → GET → name and favourite flag updated.
8. **Delete**: DELETE `/{avatar_id}` → 204 → GET → 404.

---

## Agent Context Update

The CLAUDE.md plan reference will be updated to point to this plan file.

