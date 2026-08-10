# Contract: Championship Endpoints

## POST /api/v1/championships

Create a new championship series.

### Authentication

Bearer token required.

### Request Body

```json
{
  "total_races": 5
}
```

- `total_races`: integer, 3–7 inclusive

### Responses

| Status | Condition |
|--------|-----------|
| 201 | Championship created |
| 401 | No/invalid auth token |
| 422 | Validation failure |

**201 body**:
```json
{
  "championship_id": "uuid",
  "total_races": 5,
  "races_completed": 0,
  "status": "active",
  "standings": [],
  "created_at": "ISO8601"
}
```

---

## GET /api/v1/championships/{id}

Retrieve current championship state and standings.

### Authentication

Bearer token required. Only the owning account may retrieve their championship.

### Path Parameters

- `id`: UUID of the championship

### Responses

| Status | Condition |
|--------|-----------|
| 200 | Championship found |
| 401 | No/invalid auth token |
| 403 | Requestor does not own this championship |
| 404 | Championship not found |

**200 body**:
```json
{
  "championship_id": "uuid",
  "total_races": 5,
  "races_completed": 2,
  "status": "active | completed",
  "standings": [
    {
      "avatar_id": "string",
      "is_player": true,
      "points": 16,
      "podiums": 2,
      "position": 1
    }
  ]
}
```

`standings` is sorted ascending by `position` (1st place first). `podiums` is the count of top-3 finishes.

---

## PATCH /api/v1/championships/{id}/races/{race_id}

Record a race result within a championship.

### Authentication

Bearer token required. Only the owning account may update their championship.

### Path Parameters

- `id`: UUID of the championship
- `race_id`: UUID of the completed race (must match a `POST /api/v1/races` submission)

### Request Body

```json
{
  "race_index": 0,
  "participants": [
    {
      "avatar_id": "string",
      "is_player": true,
      "finishing_position": 1
    }
  ]
}
```

- `race_index`: 0-based position of this race in the series (0 to `total_races - 1`)
- `participants`: 1–5 entries matching the race runners
- `finishing_position`: 1–5; server derives `points_earned` from the points table

### Validation

- `race_id` must not already be recorded for this championship
- `race_index` must not already be recorded for this championship
- `participants` must include exactly one entry where `is_player: true`

### Responses

| Status | Condition |
|--------|-----------|
| 200 | Race recorded; returns updated standings |
| 401 | No/invalid auth token |
| 403 | Requestor does not own this championship |
| 404 | Championship not found |
| 409 | `race_id` or `race_index` already recorded |
| 422 | Validation failure |

**200 body**: Same as `GET /api/v1/championships/{id}` (200 body above), reflecting updated standings. If this was the final race, `status` will be `"completed"`.
