# Data Model: Avatar Generation

**Feature**: 007-avatar-generation
**Date**: 2026-08-10
**Source**: spec.md, research.md, docs/ai/asset-pipeline.md, docs/content/spec-avatar-generation.md

---

## Entity Relationship Overview

```
Account (existing)
    │ 1
    │ owns many
    │ *
  Avatar ──────── active_portrait ──── AvatarPortrait (current active)
    │                                       ↑
    │ 1                                     │ many (version history)
    │ has many                              │
    │ *                                     │
  GenerationJob ──── on complete ──────────┘
```

---

## Entity: Avatar

The top-level character entity. One `Avatar` per creation request. Starts as `pending`; transitions to `published` once the first portrait generation completes successfully, or `failed` if all retries are exhausted.

### Table: `avatars`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK, default uuid4 | |
| `account_id` | UUID | FK → accounts.id NOT NULL | Owner account |
| `species` | VARCHAR | NOT NULL, CHECK IN ('fox','rabbit','bear','cat','mouse','panda') | |
| `fur_color` | VARCHAR(7) | NOT NULL | Validated hex `#RRGGBB` |
| `eye_color` | VARCHAR(7) | NOT NULL | Validated hex `#RRGGBB` |
| `hairstyle` | VARCHAR | NOT NULL | e.g. 'short', 'long', 'curly', 'braided' |
| `accessories` | JSONB | NOT NULL, default '[]' | e.g. `["headband","glasses"]` |
| `clothes_top_color` | VARCHAR(7) | NOT NULL | Validated hex `#RRGGBB` |
| `clothes_bottom_color` | VARCHAR(7) | NOT NULL | Validated hex `#RRGGBB` |
| `name` | VARCHAR | nullable | Set by LLM after generation |
| `personality` | TEXT | nullable | LLM-generated |
| `biography` | TEXT | nullable | LLM-generated, max 50 words |
| `appearance_summary` | TEXT | nullable | LLM-generated |
| `favorite_subject` | VARCHAR | nullable | LLM-generated |
| `running_style` | VARCHAR | nullable | LLM-generated |
| `status` | VARCHAR | NOT NULL, default 'pending', CHECK IN ('pending','published','failed') | |
| `is_favourite` | BOOLEAN | NOT NULL, default false | |
| `active_portrait_id` | UUID | FK → avatar_portraits.id nullable | Current displayed portrait |
| `created_at` | TIMESTAMPTZ | NOT NULL, server_default now() | |

### State Transitions

```
pending → published  (GenerationJob reaches 'complete')
pending → failed     (all retry attempts exhausted)
published → published (regeneration: active_portrait_id updated; status stays published)
```

### Indexes
- `idx_avatars_account_id` on (`account_id`) — list/count queries

### Business Rules
- Max 50 avatars per `account_id` — enforced in `AvatarDomainService` before insert.
- `is_favourite` is per-account; setting one avatar as favourite does NOT automatically unset others (multi-favourite allowed; UI may choose to display one prominently).

---

## Entity: AvatarPortrait

An immutable snapshot of one generation attempt for an avatar. Multiple portrait versions can exist per avatar. The `active_portrait_id` on `Avatar` points to the child's selected version.

### Table: `avatar_portraits`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK, default uuid4 | |
| `avatar_id` | UUID | FK → avatars.id ON DELETE CASCADE NOT NULL | |
| `version` | INTEGER | NOT NULL | Monotonically increasing per avatar (1, 2, 3…) |
| `prompt_version` | VARCHAR | NOT NULL | Template version, e.g. '1.0.0' |
| `model_version` | VARCHAR | NOT NULL | Provider model ID |
| `full_url` | VARCHAR | NOT NULL | S3 path — 1024×1024 |
| `medium_url` | VARCHAR | NOT NULL | S3 path — 512×512 |
| `small_url` | VARCHAR | NOT NULL | S3 path — 256×256 |
| `thumb_url` | VARCHAR | NOT NULL | S3 path — 128×128 |
| `created_at` | TIMESTAMPTZ | NOT NULL, server_default now() | |

### Indexes
- `idx_avatar_portraits_avatar_id` on (`avatar_id`)
- UNIQUE(`avatar_id`, `version`)

---

## Entity: GenerationJob

Tracks the lifecycle of a single portrait generation or regeneration attempt. Multiple attempts per avatar are possible (one per retry sequence, and one per explicit regeneration request).

### Table: `generation_jobs`

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK, default uuid4 | Also used as the Redis job payload key |
| `avatar_id` | UUID | FK → avatars.id ON DELETE CASCADE NOT NULL | |
| `portrait_id` | UUID | FK → avatar_portraits.id nullable | Set on successful completion |
| `status` | VARCHAR | NOT NULL, default 'queued', CHECK IN ('queued','llm_running','prompt_building','generating','validating','storing','complete','failed') | |
| `attempt` | INTEGER | NOT NULL, default 1 | 1–3 within a retry sequence |
| `prompt_version` | VARCHAR | nullable | Set once prompt is built |
| `model_version` | VARCHAR | nullable | Set once generation starts |
| `error` | TEXT | nullable | Final error message on failure |
| `created_at` | TIMESTAMPTZ | NOT NULL, server_default now() | |
| `completed_at` | TIMESTAMPTZ | nullable | Set on complete or failed |

### Indexes
- `idx_generation_jobs_avatar_id` on (`avatar_id`)
- `idx_generation_jobs_status` on (`status`) — for rate-limit queries
- `idx_generation_jobs_account_created` on (`avatar_id, created_at`) — join through avatars for hourly rate limit

### Business Rules
- Max 2 jobs per account with `status NOT IN ('complete','failed')` — checked before enqueuing.
- Max 10 jobs per account in the past hour — checked by joining through `avatars.account_id`.
- Job recovery: `infrastructure/queue/recovery.py` already re-enqueues `pending` jobs on worker startup; `queued` status aligns with its `status = 'pending'` filter (migration must align the status value or the recovery query must be updated to include `queued`).

---

## Validation Rules Summary

| Field | Rule |
|-------|------|
| `species` | Enum: fox, rabbit, bear, cat, mouse, panda |
| `fur_color`, `eye_color`, `clothes_top_color`, `clothes_bottom_color` | Regex `^#[0-9A-Fa-f]{6}$` |
| `hairstyle` | Non-empty string, max 50 chars |
| `accessories` | Array of strings, each max 50 chars, max 10 items |
| `biography` (LLM output) | Max 50 words — truncated if LLM over-generates |
| Portrait dimensions | 1024×1024 px |
| Portrait format | PNG with alpha channel |
| Portrait file size | < 5 MB |

---

## Migration

New file: `backend/alembic/versions/0007_avatars.py`

Creates three tables in order: `avatars` (no FK to portraits yet) → `avatar_portraits` → then alters `avatars` to add `active_portrait_id` FK → `avatar_portraits.id`. This ordering avoids circular FK during CREATE TABLE.
