# Contract: Generation Job Lifecycle

**Feature**: 007-avatar-generation
**Date**: 2026-08-10
**Scope**: Background worker pipeline for avatar portrait generation

---

## Job Payload (Redis queue entry)

```json
{
  "job_id": "uuid",
  "job_type": "avatar_generation",
  "avatar_id": "uuid"
}
```

The worker looks up the full job context from the database using `job_id`. The payload is minimal by design — the database is the source of truth.

---

## Job Status Transitions

```
queued
  │
  ▼
llm_running          ← LLM request in flight
  │
  ▼
prompt_building      ← PromptBuilder constructing image prompt
  │
  ▼
generating           ← GPT Image API request in flight
  │
  ▼
validating           ← Technical validation gates running
  │
  ├─ PASS ──▶ storing    ← Uploading PNG + thumbnails to object storage
  │                │
  │                ▼
  │            complete  ← avatar.status set to 'published'; active_portrait_id updated
  │
  └─ FAIL (attempt < 3) ──▶ generating (retry with modified prompt)
  │
  └─ FAIL (attempt == 3) ──▶ failed     ← avatar.status set to 'failed' if no prior published portrait
```

---

## Retry Prompt Modifications

| Attempt | Modification |
|---------|-------------|
| 1 | Standard prompt (all variables from AvatarMetadata) |
| 2 | Simplified prompt (accessories removed from variables) |
| 3 | Stricter negative prompt (additional content safety terms appended) |

The PromptBuilder accepts an `attempt` parameter and applies the appropriate modification.

---

## Validation Gates

All gates must pass before the job transitions to `storing`.

| Gate | Check | Blocking |
|------|-------|---------|
| HTTP status | Generation API returned 200 | Yes |
| Dimensions | Image is exactly 1024×1024 px | Yes |
| Format | PNG with alpha channel (RGBA) | Yes |
| File size | Binary < 5 MB | Yes |
| Non-empty | Image bounding box is not None (not blank) | Yes |
| Content check (text) | No visible text/watermark — v1: logged, not blocking | No (logged only) |
| Content check (single character) | Single character visible — v1: logged, not blocking | No (logged only) |

---

## Worker Error Handling

| Scenario | Behaviour |
|----------|-----------|
| LLM returns invalid JSON | Retry with stricter system prompt; count as attempt |
| GPT Image API 429 | Exponential backoff (1 s, 2 s, 4 s) within attempt; does not consume a retry slot |
| GPT Image API 5xx | Treat as generation failure; consume retry slot |
| Storage write fails | Retry write up to 3 times; job stays in `storing` state |
| Worker crashes mid-job | `infrastructure/queue/recovery.py` re-enqueues on next startup using job `status NOT IN ('complete','failed')` |

---

## Observability Logs (per job)

The worker must log the following structured fields for every job:

```json
{
  "job_id": "uuid",
  "job_type": "avatar_generation",
  "avatar_id": "uuid",
  "account_id": "uuid",
  "attempt": 1,
  "prompt_version": "1.0.0",
  "model_version": "gpt-image-1",
  "status_final": "complete | failed",
  "validation_result": "pass | fail",
  "validation_failures": ["dimensions"],
  "duration_ms": 12430
}
```
