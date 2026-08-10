# Contract: GET /api/v1/opponents/personalities

**Feature**: 005-ai-opponents
**Status**: Authoritative

---

## Endpoint

```
GET /api/v1/opponents/personalities
```

**Authentication**: None required (public endpoint).  
**Versioning**: Under `/api/v1/`.

---

## Request

No query parameters. No request body.

---

## Response 200 OK

```json
[
  {
    "id": "steady",
    "name": "Steady",
    "accuracyRate": 0.80,
    "baseResponseTimeMs": 3500,
    "responseTimeVarianceMs": 175,
    "speedProfile": "uniform",
    "tierOffset": 0
  },
  {
    "id": "speedster",
    "name": "Speedster",
    "accuracyRate": 0.70,
    "baseResponseTimeMs": 3500,
    "responseTimeVarianceMs": 350,
    "speedProfile": "front_loaded",
    "tierOffset": 1
  },
  {
    "id": "slow_starter",
    "name": "Slow Starter",
    "accuracyRate": 0.75,
    "baseResponseTimeMs": 3500,
    "responseTimeVarianceMs": 280,
    "speedProfile": "back_loaded",
    "tierOffset": 0
  },
  {
    "id": "unpredictable",
    "name": "Unpredictable",
    "accuracyRate": 0.65,
    "baseResponseTimeMs": 3500,
    "responseTimeVarianceMs": 875,
    "speedProfile": "random",
    "tierOffset": 0
  },
  {
    "id": "balanced",
    "name": "Balanced",
    "accuracyRate": 0.78,
    "baseResponseTimeMs": 3500,
    "responseTimeVarianceMs": 245,
    "speedProfile": "uniform",
    "tierOffset": 0
  }
]
```

**Array length**: Always exactly 5. Order is fixed (as above).

**Field types**:

| Field | Type | Constraints |
|-------|------|-------------|
| `id` | string | non-empty slug, unique |
| `name` | string | non-empty display label |
| `accuracyRate` | float | `[0.0, 1.0]` |
| `baseResponseTimeMs` | integer | > 0 |
| `responseTimeVarianceMs` | integer | ≥ 0 |
| `speedProfile` | string | one of: `"uniform"`, `"front_loaded"`, `"back_loaded"`, `"random"` |
| `tierOffset` | integer | typically in `[-1, +1]` |

---

## Error Responses

This endpoint has no query parameters and returns static data. The only expected error is a server-side crash (`500`), which is handled by the global FastAPI exception handler.

---

## Notes

- Personality definitions are static game configuration. They will only change when the spec is updated (which requires a code deploy).
- The frontend uses this endpoint at race setup time to retrieve the authoritative personality list. Local TypeScript constants exist for testing but are not used in production race setup.
- The `tierOffset` is applied by the frontend simulation engine as `clamp(playerTier + tierOffset, 1, 6)`.
