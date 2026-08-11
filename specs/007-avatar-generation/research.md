# Research: Avatar Generation

**Feature**: 007-avatar-generation
**Date**: 2026-08-10
**Status**: Complete — no NEEDS CLARIFICATION markers remain

---

## Decision 1: LLM Provider for Character Metadata

**Decision**: OpenAI Chat Completions API (`gpt-4o-mini`) via the existing `OpenAILLMAdapter` documented in `docs/ai/ai-architecture.md`.

**Rationale**: The project already defines a `LLMProvider` Protocol and an `OpenAILLMAdapter`. Using the existing adapter requires no new dependency and no architectural change. The adapter accepts a `system` prompt, `user` prompt, and JSON schema for structured output.

**Alternatives considered**:
- Anthropic Messages API — not the documented adapter; would require a new `AnthropicLLMAdapter` and a dependency change.
- Local/self-hosted LLM — noted as a future option in `docs/ai/ai-architecture.md` but not in scope for v1.

---

## Decision 2: Image Generation Provider

**Decision**: GPT Image API via `OpenAIImageAdapter` (1024×1024 px, PNG, transparent background, quality=high).

**Rationale**: Mandated by `docs/ai/asset-pipeline.md` §Step 3 and `docs/content/feature-avatar-creation.md` §GPT Image Generation. Parameters are specified and non-negotiable. The `ImageGenerationProvider` Protocol in `docs/ai/ai-architecture.md` means the provider can be swapped in future without code changes.

**Alternatives considered**: DALL-E 3 (same provider, different endpoint), Stability AI — both are valid adapter targets but out of scope; the documented adapter is OpenAI GPT Image.

---

## Decision 3: Async Job Pattern

**Decision**: Redis queue via the existing `app/worker.py` background worker. Job type key: `"avatar_generation"`. The worker's `process_job()` function gains a new dispatch branch for this job type, implemented in `app/avatars/generation_service.py`.

**Rationale**: The worker is already running in production, consuming from `QUEUE_KEY = "job_queue"`. The `job_audit` table (already referenced in `infrastructure/queue/recovery.py`) provides restart recovery. Adding a new job type is a one-branch change to the worker's dispatch function.

**Alternatives considered**: Celery, ARQ, Dramatiq — all would introduce a new dependency and duplicate the existing queue infrastructure. Rejected per Constitution §XIX (dependencies only where they provide clear long-term value).

---

## Decision 4: Object Storage

**Decision**: S3-compatible object storage (existing project infrastructure). Binary path: `characters/{account_id}/{avatar_id}/v{n}/portrait.png`. Thumbnails: `v{n}/portrait_512.png`, `v{n}/portrait_256.png`, `v{n}/portrait_128.png`.

**Rationale**: `docs/ai/asset-pipeline.md` §Step 6 specifies S3-compatible storage with this path hierarchy. The project already has S3 configuration (inferred from `infrastructure/config.py`). Binary assets must never be stored in PostgreSQL.

**Alternatives considered**: Local filesystem — not suitable for production; no CDN integration. PostgreSQL bytea — explicitly rejected by the pipeline spec and Constitution §XIV.

---

## Decision 5: Portrait Version Selection

**Decision**: `Avatar.active_portrait_id` FK → `avatar_portraits.id` (nullable until first generation completes). All previous portrait versions are retained.

**Rationale**: `docs/ai/asset-pipeline.md` §Portrait Versioning: "All versions are stored permanently. The player selects their preferred active version." The FK on `Avatar` gives O(1) lookup of the current portrait without a JOIN on version ordering.

**Alternatives considered**: `is_active` boolean on `avatar_portraits` — requires ensuring only one row per avatar has `is_active=true`, which is harder to enforce atomically than a FK on the parent. Rejected.

---

## Decision 6: Frontend Polling vs. WebSocket

**Decision**: v1 uses HTTP polling via `GET /api/v1/avatars/{avatar_id}/jobs/{job_id}`. The client polls every 2 s until `status` is `complete` or `failed`.

**Rationale**: Generation takes up to 30 s. Polling every 2 s costs ~15 requests per successful generation — trivial load. The frontend has no existing WebSocket infrastructure. WebSocket push is noted in the asset pipeline doc as a future option (`docs/ai/asset-pipeline.md` §Step 3: "polls for completion (or receives a push notification via WebSocket)").

**Alternatives considered**: Server-Sent Events — simpler than WebSocket but still requires a persistent HTTP connection and new server-side infrastructure. Deferred to a future spec.

---

## Decision 7: Thumbnail Generation

**Decision**: Thumbnails (512, 256, 128 px) are generated synchronously inside the background worker immediately after primary portrait validation passes, using Pillow. All four URLs are stored in `avatar_portraits` before the job transitions to `complete`.

**Rationale**: `docs/ai/asset-pipeline.md` §Step 7 specifies these three variants. Generating them in-worker keeps the job atomic: either all variants exist or the job is retried. Pillow is a lightweight, established library with no architectural footprint.

**Alternatives considered**: Separate thumbnail job — adds queue latency and a window where the portrait is published without thumbnails (race track rendering would fail). Rejected.

---

## Decision 8: Rate Limiting

**Decision**: Enforce rate limits in `AvatarDomainService` using SQL aggregate queries on `generation_jobs`:
- Concurrency: `COUNT(*) WHERE avatar.account_id = ? AND status NOT IN ('complete','failed')`
- Hourly: `COUNT(*) WHERE avatar.account_id = ? AND created_at >= now() - '1 hour'`

Constants: `MAX_CONCURRENT_JOBS = 2`, `MAX_JOBS_PER_HOUR = 10`, `MAX_AVATARS_PER_ACCOUNT = 50`.

**Rationale**: All limits are in single digits. SQL queries are cheap, consistent with the existing pattern (championships repository uses similar count patterns), and require no additional infrastructure.

**Alternatives considered**: Redis counters — appropriate for high-throughput rate limiting, but unnecessary for these limits. Token bucket in memory — would not survive worker restarts. Both rejected.

---

## Decision 9: Input Validation — Hex Colours

**Decision**: Validate hex colour fields in the Pydantic schema using a regex validator (`^#[0-9A-Fa-f]{6}$`). The Pydantic model rejects malformed values before they reach the domain service or PromptBuilder.

**Rationale**: Constitution §XV requires input validation; Constitution §XII requires all inputs to be sanitised before reaching the PromptBuilder. Pydantic validators run at the deserialization boundary (the correct place per Constitution §IX).

**Alternatives considered**: Validation in the PromptBuilder — would violate the single-responsibility principle and require the PromptBuilder to know about HTTP request semantics. Rejected.

---

## Open Questions (None)

All NEEDS CLARIFICATION items from the spec have been resolved by the above decisions. No open questions remain.
