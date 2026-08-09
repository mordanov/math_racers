# Contract: Mathematics API

**Feature**: 003-math-engine  
**Version**: v1  
**Date**: 2026-08-09  
**Base path**: `/api/v1`

---

## Purpose

The backend exposes a **reference-only** mathematics API. It is never called during active gameplay. Its two purposes are:

1. Seed verification — allow external tools and tests to confirm the frontend engine produces the same output as the backend reference generator for a given `(tier, seed, count)`.
2. Adaptive difficulty management — read and write the player's current tier and parent override.

---

## Endpoints

### `GET /api/v1/problems`

Generate a reference problem set from a seed.

#### Query Parameters

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| `tier` | integer | yes | 1–6 | Difficulty tier |
| `seed` | integer | yes | 0–4294967295 (32-bit uint) | Deterministic seed |
| `count` | integer | yes | 0–100 | Number of problems to generate |

#### Success Response — `200 OK`

```json
{
  "seed": 1234567890,
  "tier": 2,
  "count": 8,
  "problems": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "operation": "addition",
      "operand_a": 14,
      "operand_b": 7,
      "answer": 21,
      "tier": 2,
      "seed": 1234567890
    }
  ]
}
```

#### Error Responses

| Status | Condition | Body |
|--------|-----------|------|
| `422 Unprocessable Entity` | `tier` outside [1, 6] | `{"detail": [{"loc": ["query", "tier"], "msg": "Input should be greater than or equal to 1", ...}]}` (standard FastAPI validation error) |
| `422 Unprocessable Entity` | `count` outside [0, 100] | Standard FastAPI validation error |
| `422 Unprocessable Entity` | `seed` outside [0, 4294967295] | Standard FastAPI validation error |
| `422 Unprocessable Entity` | Missing required parameter | Standard FastAPI validation error |

---

### `GET /api/v1/players/{player_id}/difficulty`

Return a player's current adaptive tier and parent override.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `player_id` | UUID | Player identifier |

#### Success Response — `200 OK`

```json
{
  "player_id": "550e8400-e29b-41d4-a716-446655440000",
  "current_tier": 3,
  "parent_override": null,
  "effective_tier": 3
}
```

`effective_tier` is `parent_override` if set, otherwise `current_tier`. Both are always integers in [1, 6].

#### Error Responses

| Status | Condition |
|--------|-----------|
| `404 Not Found` | `player_id` does not exist |
| `401 Unauthorized` | Missing or invalid authentication |
| `403 Forbidden` | Caller lacks permission to read this player's data |

---

### `PATCH /api/v1/players/{player_id}/difficulty`

Set or clear the parent difficulty override for a player.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `player_id` | UUID | Player identifier |

#### Request Body

```json
{
  "parent_override": 4
}
```

`parent_override` may be an integer in [1, 6] or `null` to clear the override.

#### Success Response — `200 OK`

Same shape as `GET /api/v1/players/{player_id}/difficulty`.

#### Error Responses

| Status | Condition |
|--------|-----------|
| `422 Unprocessable Entity` | `parent_override` outside [1, 6] and not null |
| `404 Not Found` | `player_id` does not exist |
| `401 Unauthorized` | Missing or invalid authentication |
| `403 Forbidden` | Caller is not the parent of this player |

---

## Frontend Module Contract

The frontend engine exposes three pure functions. These are not HTTP endpoints — they are TypeScript module exports.

### `generateProblemSet(tier, seed, count): ProblemSet`

| Argument | Type | Constraints |
|----------|------|-------------|
| `tier` | `Tier` (1–6) | Must be a valid `Tier` value |
| `seed` | `number` | 32-bit unsigned integer |
| `count` | `number` | 0–100 |

Returns a `ProblemSet`. Never throws. Returns empty `problems` array when `count === 0`.

### `validateAnswer(problem, playerInput): ValidationResult`

| Argument | Type |
|----------|------|
| `problem` | `Problem` |
| `playerInput` | `string` |

Returns a `ValidationResult`. Never throws. Completes in < 1 ms.

### `selectTier(input): Tier`

| Argument | Type |
|----------|------|
| `input` | `TierSelectionInput` |

Returns a `Tier` in [1, 6]. Never throws. Clamps `parentOverride` silently to [1, 6] if provided.
