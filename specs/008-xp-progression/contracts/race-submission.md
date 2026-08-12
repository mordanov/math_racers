# Contract: Race Submission with XP Award

**Endpoint**: `POST /api/v1/races`  
**Auth**: Bearer token required (approved account)  
**Change**: Existing endpoint — response body extended with `progression` field

## Request Body

```json
{
  "race_id": "uuid",
  "seed": "string",
  "difficulty_tier": 2,
  "mode": "quick | championship | duel | training",
  "started_at": "ISO8601",
  "completed_at": "ISO8601",
  "participants": [
    {
      "avatar_id": "string",
      "position": 1,
      "problems_correct": 7,
      "longest_streak": 5,
      "average_response_ms": 1200,
      "total_distance": 126,
      "xp_earned": 70
    }
  ]
}
```

**New field**: `participants[].longest_streak` — integer ≥ 0, required.

## Response: 201 Created

```json
{
  "race_id": "uuid",
  "created_at": "ISO8601",
  "progression": {
    "total_xp": 840,
    "current_level": 2,
    "xp_to_next_level": 660,
    "xp_earned_this_race": 240,
    "level_up": {
      "previous_level": 1,
      "new_level": 2,
      "total_xp": 840
    }
  }
}
```

`progression.level_up` is `null` (or absent) when no level boundary was crossed.

## Response: 409 Conflict

```json
{
  "error_code": "RACE_ALREADY_EXISTS",
  "message": "Race <uuid> already exists."
}
```

Returned when the same `race_id` is submitted twice. XP is not re-awarded.

## Error Cases

| Condition | Status | error_code |
|-----------|--------|------------|
| `race_id` already submitted | 409 | `RACE_ALREADY_EXISTS` |
| Invalid field values | 422 | (Pydantic validation) |
| Unauthenticated | 401 | `UNAUTHORIZED` |
| Account not approved | 403 | `ACCOUNT_PENDING` |
