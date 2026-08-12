# API Contracts: Player Achievements

## GET /api/v1/achievements

Returns the achievement catalogue. Hidden achievements are excluded for unauthenticated callers and for authenticated callers who have not unlocked them.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | UUID | No | When provided, unlocked hidden achievements for this account are included |

### Response 200

```json
{
  "achievements": [
    {
      "key": "first_race",
      "category": "racing",
      "title": "Off to the Races!",
      "description": "Complete your first race.",
      "hidden": false,
      "icon_path": "assets/achievements/first_race.png",
      "unlocked_at": null
    },
    {
      "key": "perfect_race",
      "category": "mathematics",
      "title": "Perfect Score",
      "description": "Answer all 8 problems correctly in a single race.",
      "hidden": false,
      "icon_path": "assets/achievements/perfect_race.png",
      "unlocked_at": "2026-08-12T10:30:00Z"
    }
  ]
}
```

`unlocked_at` is `null` for locked achievements and an ISO 8601 timestamp when unlocked. Hidden achievements that the account has not unlocked are absent from the list entirely.

---

## GET /api/v1/players/{account_id}/achievements

Returns all achievements unlocked by a specific player. Requires authentication. A player may only request their own list (returns 403 for other accounts, unless admin).

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | UUID | Yes | The player's account ID |

### Response 200

```json
{
  "account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "achievements": [
    {
      "key": "first_race",
      "category": "racing",
      "title": "Off to the Races!",
      "description": "Complete your first race.",
      "hidden": false,
      "icon_path": "assets/achievements/first_race.png",
      "unlocked_at": "2026-08-12T09:00:00Z",
      "avatar_id": null
    }
  ]
}
```

### Response 403

```json
{
  "error_code": "FORBIDDEN",
  "message": "You may only view your own achievements.",
  "request_id": "..."
}
```

### Response 404

```json
{
  "error_code": "NOT_FOUND",
  "message": "Account not found.",
  "request_id": "..."
}
```

---

## POST /api/v1/races — Response Extension

The existing race completion endpoint response is extended with a `new_achievements` field.

### Response 201 (extended)

```json
{
  "race_id": "...",
  "participants": [...],
  "progression": { ... },
  "new_achievements": [
    {
      "key": "first_race",
      "category": "racing",
      "title": "Off to the Races!",
      "description": "Complete your first race.",
      "hidden": false,
      "icon_path": "assets/achievements/first_race.png",
      "unlocked_at": "2026-08-12T09:00:00Z"
    }
  ]
}
```

`new_achievements` is an empty list `[]` when no achievements were unlocked in this race. It is omitted (or null) when the request is unauthenticated.

---

## Notes

- No endpoint exists for directly granting achievements; unlock is exclusively triggered by domain events.
- The catalogue never changes at runtime; GET /api/v1/achievements may be cached aggressively by the client.
