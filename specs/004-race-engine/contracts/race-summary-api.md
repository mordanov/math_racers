# Contract — Race Summary API

**Branch**: `004-race-engine` | **Date**: 2026-08-10

This contract describes the REST endpoint the frontend calls once per completed race to persist the race summary.

---

## Endpoint

```
POST /api/v1/races/
Authorization: Bearer <JWT>
Content-Type: application/json
```

---

## Request Body

```json
{
  "race_id": "string (UUID)",
  "seed": "string",
  "difficulty_tier": 1,
  "mode": "quick | championship | duel | training",
  "started_at": "ISO 8601 datetime",
  "completed_at": "ISO 8601 datetime",
  "participants": [
    {
      "avatar_id": "string (UUID for human, 'ai-0'..'ai-3' for AI)",
      "position": 1,
      "problems_correct": 8,
      "average_response_ms": 1500,
      "total_distance": 144,
      "xp_earned": 100
    }
  ]
}
```

### Validation rules

| Field | Rule |
|-------|------|
| `race_id` | Valid UUID v4 |
| `difficulty_tier` | Integer 1–6 |
| `mode` | One of the four enum values |
| `participants` | 1–5 entries |
| `position` | Unique within the request; integer 1–5 |
| `problems_correct` | Integer 0–8 |
| `total_distance` | Integer 0–144 |
| `xp_earned` | Integer ≥ 0 |
| `average_response_ms` | Integer ≥ 0 |

---

## Success Response — 201 Created

```json
{
  "race_id": "string (UUID)",
  "created_at": "ISO 8601 datetime"
}
```

---

## Error Responses

| Status | Code | Scenario |
|--------|------|----------|
| 400 | `VALIDATION_ERROR` | Any field fails validation |
| 401 | `UNAUTHORIZED` | Missing or expired JWT |
| 409 | `RACE_ALREADY_EXISTS` | `race_id` already persisted |
| 422 | `UNPROCESSABLE_ENTITY` | Structurally invalid JSON |

Error body:
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Human-readable description",
  "detail": [{ "field": "participants[0].position", "message": "must be 1–5" }]
}
```

---

## Notes

- The frontend sends this request exactly once, after the FINISHING → RESULTS transition.
- No API calls are made during RACING state.
- Idempotency: a second POST with the same `race_id` returns 409; the client should not retry after 409.
- XP calculation is performed server-side; the value in the request is the value displayed to the player. The backend may override it based on authoritative progression rules (future feature).
