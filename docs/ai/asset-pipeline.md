# Asset Pipeline Specification

**Level:** Specification
**Status:** Authoritative
**Source:** GDD Chapter 13; art_bible.md Part IV; prompt_bible.md Part I
**Parent:** [Epic E4 — Content Pipeline](../content/epic.md)

---

## Purpose

This document specifies the complete workflow for generating, validating, storing, and serving AI-generated visual assets in Math Racers. Every asset — from avatar portraits to achievement badges — follows this pipeline.

---

## Core Principle

> **Generate once. Reuse forever.**

An avatar is never regenerated unless the player explicitly requests it. Every generated asset becomes a permanent part of the player's collection.

---

## Pipeline Overview

```
Asset Request
      ↓
Validate Input
      ↓
Build Prompt  ← Prompt Builder (deterministic)
      ↓
Generate      ← GPT Image API (async)
      ↓
Validate Output
      ↓
Store         ← Object Storage + Database metadata
      ↓
Publish       ← CDN / cache invalidation
      ↓
Cache         ← Browser + edge
```

Failures at any stage are recoverable. The child never sees a technical error message.

---

## Asset Categories

| Category | Description | Template |
|----------|-------------|----------|
| Character Portrait | Full-body avatar in running-ready pose | Character Prompt Template |
| Character Portrait — Head | Head-and-shoulders for profile screens | Character Portrait Template |
| Victory Pose | Avatar celebrating after winning | Victory Pose Template |
| Thinking Pose | Avatar with hand on chin while solving | Thinking Pose Template |
| Stadium Background | Wide children's athletics stadium | Stadium Background Template |
| Achievement Badge | Circular enamel collectible badge | Achievement Badge Template |
| Trophy | Golden rounded trophy | Trophy Template |
| Medal | Sports medal with ribbon | Medal Template |
| Loading Screen | Runners practising or warming up | Loading Screen Template |
| Main Menu Illustration | Wide cinematic festival scene | Main Menu Illustration Template |
| UI Icon | Simple game icon | Icon Template |

Each category has its own prompt template defined in the Prompt Bible.

---

## Asset Identity

Every generated asset receives immutable metadata:

```
asset_id          UUID
generation_version integer
prompt_version    string
model_version     string
created_at        timestamp
created_by        user_id or "system"
status            requested | generating | validated | published | archived
```

Assets are **immutable**. Updates create new versions; existing versions are never modified.

---

## Step 1 — Input Validation

Before a prompt is built, validate:

- All required template variables are present.
- Variable values comply with the allowed character set (no injection characters).
- The requested asset type is in the approved category list.
- The requesting account has sufficient quota (rate limit check).

Validation failure returns a structured error; no generation is attempted.

---

## Step 2 — Prompt Builder

The Prompt Builder converts structured metadata into a GPT Image prompt.

**Rules:**
- Always starts with the Global Prompt Prefix (never omitted).
- Always ends with the Global Negative Prompt.
- Substitutes all template variables from character metadata.
- Produces the same prompt given the same inputs (deterministic).
- Stores the full prompt text in the generation record.
- Increments `prompt_version` whenever a template changes.

**Forbidden:**
- Free-form prompt editing from the frontend.
- Hard-coded prompts in application code.
- Prompt construction inside controllers or view layers.

---

## Step 3 — Generation

Request parameters sent to GPT Image:

| Parameter | Value |
|-----------|-------|
| Size | 1024×1024 |
| Format | PNG |
| Background | Transparent |
| Quality | High |
| Aspect ratio | 1:1 |

Generation is **asynchronous**. The client receives a job ID and polls for completion (or receives a push notification via WebSocket).

---

## Step 4 — Output Validation

Every generated image passes automated quality gates before being published:

**Technical checks:**
- [ ] HTTP 200 response from generation API
- [ ] Image dimensions exactly 1024×1024
- [ ] PNG format with alpha channel
- [ ] File size within acceptable bounds (< 5 MB)

**Content checks:**
- [ ] Transparent background detected
- [ ] Single character visible (for character assets)
- [ ] No visible text, watermark, or signature
- [ ] No cropped body parts
- [ ] No border or frame

**Artistic checks (human review in future versions):**
- Correct species/species features
- Colours match metadata
- Expression matches requested pose

Failed technical or content checks → automatic retry.

---

## Step 5 — Retry Strategy

```
Attempt 1 → Standard prompt
     ↓ (if failed)
Attempt 2 → Simplified prompt (reduced variables)
     ↓ (if failed)
Attempt 3 → Alternative seed / temperature
     ↓ (if all failed)
Escalate → Log failure, notify user with friendly message
```

Maximum 3 automatic retries per generation request. Retry state is logged with the job record.

---

## Step 6 — Storage

**Binary assets** → Object storage (S3-compatible)

Storage hierarchy:
```
characters/
  {user_id}/{avatar_id}/v{n}/portrait.png
backgrounds/
  stadium-default.png
badges/
  {achievement_id}.png
ui/
  trophy.png
  medal-gold.png
loading/
  warm-up-1.png
```

**Metadata** → PostgreSQL

The database stores all metadata, prompt records, version history, and status. Binary files are referenced by URL, not embedded.

---

## Step 7 — Thumbnail Generation

After storage, generate smaller variants automatically:

| Variant | Size | Use |
|---------|------|-----|
| full | 1024×1024 | Detail view, download |
| medium | 512×512 | Race track |
| small | 256×256 | Avatar gallery card |
| thumb | 128×128 | Leaderboard / results |

---

## Step 8 — Caching

**Priority assets to preload before a race:**
- Favourite avatar (all variants)
- Opponent avatars for current race
- Current race background

**Cache invalidation:**
Only when a new asset version becomes the active version. Previously published versions remain accessible.

---

## Portrait Versioning

When a player regenerates their avatar portrait:

```
Version 1 (original)
      ↓
Version 2 (regenerated)
      ↓
Version 3 (regenerated again)
```

- All versions are stored permanently.
- The player selects their preferred active version.
- Race history is associated with the avatar entity, not a specific version.

---

## Asset Lifecycle States

```
requested → generating → validated → published → cached
                                              ↓
                                          archived
```

Assets are **never silently replaced or deleted**. Archival requires an explicit action.

---

## Prompt Versioning

Every generation record stores:

| Field | Value |
|-------|-------|
| prompt_version | Template version string (e.g. `1.0.3`) |
| prompt_template | Full prompt text as sent |
| model_version | GPT Image model ID |
| generation_date | ISO 8601 timestamp |
| seed | If supported by the model |

This ensures future prompt improvements remain reproducible and auditable.

---

## Safety Requirements

Generated content must never include:

- Violence, weapons, or realistic injuries
- Frightening or horror imagery
- Offensive symbols or gestures
- Inappropriate clothing
- Political or religious messaging
- Text, numbers, or logos

Every generated asset must be suitable for children aged 6–12.

---

## Observability

Log for every generation job:

- `job_id`, `asset_type`, `user_id`, `avatar_id`
- `prompt_version`, `model_version`
- `start_time`, `end_time`, `duration_ms`
- `attempt_count`, `final_status`
- `validation_result` (pass / fail + reason)

Metrics to track:

- Generation success rate
- Average generation duration
- Retry rate
- Validation failure breakdown by check type

---

## Integration Boundaries

| Component | Responsibility |
|-----------|----------------|
| Frontend | Displays creation form, shows progress, renders portraits |
| Backend API | Receives creation request, enqueues job, returns job ID |
| Background Worker | Runs the pipeline: validate → build prompt → generate → validate → store |
| Prompt Builder | Constructs deterministic prompts from metadata |
| GPT Image API | Generates images (infrastructure, not business logic) |
| Object Storage | Stores binary assets |
| PostgreSQL | Stores all metadata, prompt records, asset versions |

The frontend never calls the GPT Image API directly. The frontend never constructs prompts.

---

## Acceptance Criteria

- [ ] Avatar portrait generation completes within 30 s (P95) under normal load.
- [ ] Failed validation triggers retry without user intervention.
- [ ] All retry attempts are logged with their validation failure reason.
- [ ] Every prompt record stores prompt_version, model_version, and timestamp.
- [ ] Portrait regeneration creates a new version; all previous versions remain accessible.
- [ ] Thumbnail variants are generated automatically after each successful portrait.
- [ ] No prompt is ever constructed outside the Prompt Builder.
- [ ] Frontend never receives API keys or prompt templates.

---

## Edge Cases

| Scenario | Behaviour |
|----------|-----------|
| GPT Image API timeout | Retry up to 3 times; escalate on 3rd failure |
| Invalid character in metadata | Sanitise before Prompt Builder; reject if unsalvageable |
| Image passes validation but looks wrong | Manual review (future v1.5 parental approval) |
| Storage write fails | Job stays in `validated` state; retry write; escalate after 3 failures |
| Player regenerates while a job is in progress | Queue the new request; cancel the in-progress job |
| 50-avatar limit reached | Show friendly message; prompt to delete an existing avatar |

---

## Manual Verification Steps

1. Create a new avatar with all fields filled. Confirm portrait appears within 30 s.
2. Create an avatar with minimal fields. Confirm defaults are applied and portrait is valid.
3. Attempt regeneration. Confirm the previous version remains selectable.
4. Check the generation log for prompt_version and model_version records.
5. Resize the browser to 768px width. Confirm the creation form is fully usable.
6. Disconnect network mid-generation. Confirm a friendly error appears (no crash).
7. Open the avatar gallery with 50 avatars. Confirm performance is acceptable.
