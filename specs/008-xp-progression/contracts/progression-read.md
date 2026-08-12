# Contract: Get Player Progression

**Endpoint**: `GET /api/v1/progression`  
**Auth**: Bearer token required (approved account)  
**Purpose**: Return the authenticated player's current XP total, level, and next-level threshold.

## Response: 200 OK

```json
{
  "total_xp": 1450,
  "current_level": 3,
  "xp_to_next_level": 150
}
```

If the player has never submitted a race result, returns the zero-state:

```json
{
  "total_xp": 0,
  "current_level": 0,
  "xp_to_next_level": 100
}
```

## Field Definitions

| Field | Type | Formula |
|-------|------|---------|
| `total_xp` | Integer ≥ 0 | Sum of all XP events for this account |
| `current_level` | Integer ≥ 0 | `floor(sqrt(total_xp / 100))` |
| `xp_to_next_level` | Integer ≥ 1 | `(current_level + 1)² × 100 − total_xp` |

`xp_to_next_level` is always ≥ 1 (never 0 or negative — at the exact level boundary the player is already at the new level).

## Error Cases

| Condition | Status | error_code |
|-----------|--------|------------|
| Unauthenticated | 401 | `UNAUTHORIZED` |
| Account not approved | 403 | `ACCOUNT_PENDING` |
