# API Contracts: Avatar Generation Endpoints

**Feature**: 007-avatar-generation
**Date**: 2026-08-10
**Base path**: `/api/v1/avatars`
**Auth**: All endpoints require a valid session cookie (same as existing `/api/v1/championships` pattern).

---

## POST `/api/v1/avatars`

Create a new avatar and enqueue a generation job.

### Request Body

```json
{
  "species": "fox",
  "fur_color": "#FF8C00",
  "eye_color": "#228B22",
  "hairstyle": "curly",
  "accessories": ["headband"],
  "clothes_top_color": "#4169E1",
  "clothes_bottom_color": "#FFFFFF"
}
```

All fields except `species` are optional. Missing fields receive creative defaults (applied in `AvatarDomainService` before passing to the LLM).

### Responses

**201 Created**
```json
{
  "avatar_id": "uuid",
  "job_id": "uuid",
  "status": "pending"
}
```

**422 Unprocessable Entity** — validation error (invalid hex, unknown species)
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "fur_color must be a valid hex colour (#RRGGBB)"
}
```

**422 Unprocessable Entity** — avatar limit
```json
{
  "error_code": "AVATAR_LIMIT_REACHED",
  "message": "Maximum of 50 avatars per account reached."
}
```

**429 Too Many Requests** — concurrency or hourly limit
```json
{
  "error_code": "CONCURRENCY_LIMIT_REACHED",
  "message": "Maximum of 2 concurrent generation jobs active."
}
```
or
```json
{
  "error_code": "RATE_LIMIT_EXCEEDED",
  "message": "Maximum of 10 generation attempts per hour reached."
}
```

---

## GET `/api/v1/avatars/{avatar_id}/jobs/{job_id}`

Poll the status of a generation job.

### Path Parameters
- `avatar_id` — UUID of the avatar
- `job_id` — UUID of the job (returned by POST or POST regenerate)

### Responses

**200 OK**
```json
{
  "job_id": "uuid",
  "avatar_id": "uuid",
  "status": "queued | llm_running | prompt_building | generating | validating | storing | complete | failed",
  "attempt": 1,
  "error": null,
  "created_at": "ISO8601",
  "completed_at": "ISO8601 | null"
}
```

**404 Not Found**
```json
{
  "error_code": "JOB_NOT_FOUND",
  "message": "Job {job_id} not found."
}
```

Ownership enforced: the `avatar_id` must belong to the authenticated account.

---

## GET `/api/v1/avatars`

List all avatars for the authenticated account.

### Responses

**200 OK**
```json
[
  {
    "avatar_id": "uuid",
    "name": "Zara",
    "species": "fox",
    "status": "published",
    "is_favourite": false,
    "portrait": {
      "id": "uuid",
      "thumb_url": "https://...",
      "small_url": "https://...",
      "medium_url": "https://...",
      "full_url": "https://..."
    },
    "created_at": "ISO8601"
  }
]
```

Avatars with `status = "pending"` or `"failed"` are included with `portrait: null`.

---

## GET `/api/v1/avatars/{avatar_id}`

Get a single avatar with full metadata.

### Responses

**200 OK**
```json
{
  "avatar_id": "uuid",
  "species": "fox",
  "fur_color": "#FF8C00",
  "eye_color": "#228B22",
  "hairstyle": "curly",
  "accessories": ["headband"],
  "clothes_top_color": "#4169E1",
  "clothes_bottom_color": "#FFFFFF",
  "name": "Zara",
  "personality": "Curious and fearless",
  "biography": "Zara loves puzzles...",
  "appearance_summary": "A bright orange fox with curly hair",
  "favorite_subject": "Geometry",
  "running_style": "Sprinter",
  "status": "published",
  "is_favourite": false,
  "active_portrait_id": "uuid",
  "portrait": {
    "id": "uuid",
    "version": 1,
    "prompt_version": "1.0.0",
    "model_version": "gpt-image-1",
    "thumb_url": "https://...",
    "small_url": "https://...",
    "medium_url": "https://...",
    "full_url": "https://...",
    "created_at": "ISO8601"
  },
  "portrait_history": [
    { "id": "uuid", "version": 1, "thumb_url": "https://...", "created_at": "ISO8601" }
  ],
  "created_at": "ISO8601"
}
```

**404 Not Found**
```json
{
  "error_code": "AVATAR_NOT_FOUND",
  "message": "Avatar {avatar_id} not found."
}
```

---

## PATCH `/api/v1/avatars/{avatar_id}`

Rename an avatar or set/unset as favourite. Partial update — only supplied fields are changed.

### Request Body

```json
{
  "name": "Zara",
  "is_favourite": true,
  "active_portrait_id": "uuid"
}
```

All fields optional. `active_portrait_id` must be an existing portrait belonging to this avatar.

### Responses

**200 OK** — returns the updated avatar (same schema as GET single avatar)

**404 Not Found** — avatar or portrait not found
**422 Unprocessable Entity** — `active_portrait_id` does not belong to this avatar

---

## POST `/api/v1/avatars/{avatar_id}/regenerate`

Trigger a new portrait generation for an existing avatar. Uses the same input fields already stored; only the portrait changes.

### Request Body

None required (avatar customisation fields are already stored).

### Responses

**201 Created**
```json
{
  "avatar_id": "uuid",
  "job_id": "uuid",
  "status": "queued"
}
```

**404 Not Found** — avatar not found
**429 Too Many Requests** — concurrency or hourly limit (same error codes as POST create)

---

## DELETE `/api/v1/avatars/{avatar_id}`

Delete an avatar and all its portraits. Cascades to `generation_jobs` and `avatar_portraits`.

### Responses

**204 No Content** — deleted

**404 Not Found**
```json
{
  "error_code": "AVATAR_NOT_FOUND",
  "message": "Avatar {avatar_id} not found."
}
```
