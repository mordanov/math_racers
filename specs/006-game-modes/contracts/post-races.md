# Contract: POST /api/v1/races (updated)

**Existing endpoint** — updated to accept nullable `position` for training mode.

## Method & Path

`POST /api/v1/races`

## Authentication

Bearer token required (existing behaviour).

## Request Body

```json
{
  "race_id": "uuid",
  "seed": "string",
  "difficulty_tier": 1,
  "mode": "quick | championship | duel | training",
  "started_at": "ISO8601",
  "completed_at": "ISO8601",
  "participants": [
    {
      "avatar_id": "string",
      "position": 1,
      "problems_correct": 7,
      "average_response_ms": 1200,
      "total_distance": 126,
      "xp_earned": 70
    }
  ]
}
```

**Changes from current**:
- `participants[].position`: was `int BETWEEN 1 AND 5`, now `int BETWEEN 1 AND 5 | null`. `null` is only valid when `mode == "training"`.

## Validation

- `race_id`: valid UUID; must not already exist (idempotency via 409)
- `difficulty_tier`: 1–6
- `mode`: one of `quick`, `championship`, `duel`, `training`
- `participants`: 1–5 items; positions must be unique (among non-null values)
- `participants[].position`: null only when `mode == "training"`

## Responses

| Status | Condition |
|--------|-----------|
| 201 | Race persisted |
| 401 | No/invalid auth token |
| 409 | `race_id` already exists |
| 422 | Validation failure |

**201 body**:
```json
{ "race_id": "uuid", "created_at": "ISO8601" }
```
