# Specification — Avatar Generation

**Level:** Specification
**Status:** Authoritative
**Source:** GDD Chapter 13; prompt_bible.md Parts I–II; art_bible.md Part IV
**Parent:** [Feature F2.1 — Avatar Creation](feature-avatar-creation.md)
**See also:** [../ai/asset-pipeline.md](../ai/asset-pipeline.md)

---

## Data Model

### AvatarCreationRequest

```json
{
  "child_profile_id": "uuid",
  "species": "fox|rabbit|bear|cat|mouse|panda",
  "fur_color": "#RRGGBB",
  "eye_color": "#RRGGBB",
  "hairstyle": "short|long|curly|braided|...",
  "accessories": ["headband", "glasses"],
  "clothes_top_color": "#RRGGBB",
  "clothes_bottom_color": "#RRGGBB"
}
```

### AvatarMetadata (LLM output)

```json
{
  "name": "string",
  "personality": "string",
  "biography": "string (max 50 words)",
  "appearance_summary": "string",
  "species": "string",
  "favorite_color": "string",
  "favorite_subject": "string",
  "running_style": "string"
}
```

### GenerationJob

```json
{
  "job_id": "uuid",
  "avatar_id": "uuid",
  "status": "queued|llm_running|prompt_building|generating|validating|storing|complete|failed",
  "attempt": 1,
  "prompt_version": "1.0.0",
  "model_version": "string",
  "created_at": "ISO 8601",
  "completed_at": "ISO 8601 | null",
  "error": "string | null"
}
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/avatars` | Create avatar (returns job_id) |
| GET | `/api/v1/avatars/{avatar_id}/jobs/{job_id}` | Poll job status |
| GET | `/api/v1/avatars` | List all avatars for current child |
| GET | `/api/v1/avatars/{avatar_id}` | Get single avatar |
| PATCH | `/api/v1/avatars/{avatar_id}` | Rename or set favourite |
| POST | `/api/v1/avatars/{avatar_id}/regenerate` | Trigger portrait regeneration |
| DELETE | `/api/v1/avatars/{avatar_id}` | Delete avatar |

---

## Backend Workflow (Background Worker)

```
1. Receive AvatarCreationRequest
2. Validate input (species in allowed list, colours are valid hex)
3. Create avatar record (status=pending) in database
4. Enqueue generation job
5. Return avatar_id + job_id to client

--- Background Worker ---
6. Load job record
7. Call LLM: generate metadata (AvatarMetadata schema)
8. Store metadata in avatar record
9. Build image prompt via Prompt Builder
10. Store prompt record (prompt_version, full_text, model_version)
11. Call GPT Image API
12. Receive image binary
13. Run technical validation gates
14. Run content validation gates
15. If any gate fails → retry (max 3 attempts)
16. On pass: store PNG to object storage
17. Generate thumbnails (512, 256, 128)
18. Store thumbnail URLs in avatar record
19. Update avatar status = published
20. Notify client (WebSocket push or polling endpoint)
```

---

## Validation Gate Implementation

```python
def validate_image(image_bytes: bytes) -> ValidationResult:
    img = Image.open(BytesIO(image_bytes))

    checks = {
        "dimensions": img.size == (1024, 1024),
        "has_alpha": img.mode == "RGBA",
        "file_size": len(image_bytes) < 5 * 1024 * 1024,
        "not_empty": img.getbbox() is not None,
    }
    return ValidationResult(passed=all(checks.values()), checks=checks)
```

Content-level checks (no text, single character) require either a secondary vision-model call or heuristic analysis. In v1.0, these are logged but not blocking (flag for future manual review).

---

## Retry Strategy

| Attempt | Prompt Modification |
|---------|---------------------|
| 1 | Standard prompt (all variables) |
| 2 | Simplified prompt (remove optional accessories) |
| 3 | Stricter negative prompt (add additional content safety terms) |

After 3 failures: job status = `failed`, child sees friendly error, manual retry offered.

---

## Rate Limits

| Limit | Value |
|-------|-------|
| Concurrent generation jobs per account | 2 |
| Generations per hour per account | 10 |
| Total avatars per child profile | 50 |
| Portrait versions per avatar | Unlimited |

---

## Edge Cases

| Scenario | Behaviour |
|----------|-----------|
| LLM returns invalid JSON | Retry with stricter system prompt; escalate after 3 failures |
| GPT Image API returns 429 | Exponential backoff (1s, 2s, 4s); escalate after 3 retries |
| Storage write fails | Retry write up to 3 times; job stays in `storing` state |
| Child closes browser during generation | Job continues server-side; result available on next session |
| Colour hex code contains script injection | Sanitise to valid hex; reject if unsalvageable |
| Child profile at 50 avatar limit | Return 422 with `AVATAR_LIMIT_REACHED` code; frontend shows friendly message |

---

## Manual Verification Steps

1. Complete the avatar creation form with all fields. Confirm portrait appears within 30 s.
2. Complete the form with only species selected. Confirm defaults fill remaining fields.
3. While generation is in progress, close and reopen the browser. Confirm the portrait eventually appears.
4. Generate a portrait, then click Regenerate. Confirm a second version is created and the first remains accessible.
5. Delete an avatar. Confirm the gallery slot is freed and the avatar is gone.
6. Create 50 avatars. Confirm the 51st creation attempt shows a friendly limit message.
7. Inspect database: confirm prompt_version, model_version, and generation_date are stored for each portrait.
