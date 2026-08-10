# Data Model: AI Opponents

**Branch**: `005-ai-opponents` | **Date**: 2026-08-10

---

## Entities

### AiPersonality (frontend TypeScript type, backend Pydantic schema)

Represents a named AI opponent configuration used during race simulation.

**Fields**:

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | string | non-empty, unique across 5 personalities | e.g. `"steady"` |
| `name` | string | non-empty display label | e.g. `"Steady"` |
| `accuracyRate` | float | `[0.0, 1.0]` | probability of a correct answer at any checkpoint |
| `baseResponseTimeMs` | number | > 0 | Gaussian noise centre for response time (ms) |
| `responseTimeVarianceMs` | number | ≥ 0 | Gaussian noise σ for response time (ms) |
| `speedProfile` | enum | `"uniform" \| "front_loaded" \| "back_loaded" \| "random"` | Controls checkpoint-index lerp for base response time |
| `tierOffset` | integer | `[-1, +1]` in practice | Adjustment to player's tier for this opponent |

**Validation rules**:
- `accuracyRate` clamped to `[0.0, 1.0]` after variability offset is applied at simulation time.
- `tierOffset` produces an `opponentTier = clamp(playerTier + tierOffset, 1, 6)`; clamped value used, never raw offset.

**State transitions**: None — personalities are static constants; they are never modified during a race.

---

### AIOpponentRunner (frontend runtime state, no persistence)

Tracks the live state of a single AI opponent during a race. Extends the existing `RunnerState` — no separate type needed; the personality is accessed via `ParticipantConfig.personality`.

**Fields already on RunnerState**:

| Field | Type | Notes |
|-------|------|-------|
| `runnerId` | string | stable unique ID within a race |
| `isHuman` | false | always false for AI runners |
| `totalDistanceMetres` | number | accumulated movement |
| `obstaclesCompleted` | number | 0–8 |
| `obstacleResults` | ObstacleResult[] | per-checkpoint results |
| `finishTime` | number \| null | clock ms at completion |

**No new persisted entity**: AI runner state is transient (browser memory only). The `RaceSummary` already includes AI participants in the `participants` array via `getSummary()`.

---

### PersonalityDefinition (backend response schema)

Served by `GET /api/v1/opponents/personalities`. Carries all fields the frontend needs to construct an `AiPersonality` for race setup.

**Fields** (Pydantic schema, serialised as camelCase via alias):

| Field | JSON key | Type | Notes |
|-------|----------|------|-------|
| `id` | `id` | str | personality slug |
| `name` | `name` | str | display name |
| `accuracy_rate` | `accuracyRate` | float | |
| `base_response_time_ms` | `baseResponseTimeMs` | int | |
| `response_time_variance_ms` | `responseTimeVarianceMs` | int | |
| `speed_profile` | `speedProfile` | str | one of four values |
| `tier_offset` | `tierOffset` | int | |

**No database table**. Values are module-level constants in `app/opponents/personalities.py`.

---

## Entity Relationships

```
PlayerTier (integer, 1–6)
    │
    ▼ (used at race start, clamped)
AiPersonality.tierOffset
    │
    ▼
opponentTier = clamp(playerTier + tierOffset, 1, 6)  [computed, not stored]

RaceConfig.participants[]
    │ (each non-human participant has)
    ▼
ParticipantConfig.personality: AiPersonality
    │
    ▼ (consumed per checkpoint)
simulateAiObstacle(personality, checkpointIndex, rng) → AiObstacleResult
    │
    ▼
calculateMovement(isCorrect, responseTimeMs) → TierResult.distanceMetres
    │
    ▼
RunnerState.totalDistanceMetres  [transient, browser only]
    │
    ▼ (race end, sorted by distance)
ParticipantSummary  [included in RaceSummary → POST /api/v1/races]
```

---

## Constants (5 Personality Definitions)

Matches the spec table exactly:

| id | name | accuracyRate | baseResponseTimeMs | responseTimeVarianceMs | speedProfile | tierOffset |
|----|----|---|---|---|---|---|
| `steady` | Steady | 0.80 | 3500 | 175 | `uniform` | 0 |
| `speedster` | Speedster | 0.70 | 3500 | 350 | `front_loaded` | +1 |
| `slow_starter` | Slow Starter | 0.75 | 3500 | 280 | `back_loaded` | 0 |
| `unpredictable` | Unpredictable | 0.65 | 3500 | 875 | `random` | 0 |
| `balanced` | Balanced | 0.78 | 3500 | 245 | `uniform` | 0 |

`responseTimeVarianceMs` is derived as `baseResponseTime(3.5s) * spec.variability` to translate the spec's relative variability values into millisecond standard deviations.

---

## No New Database Migrations

This feature introduces no new database tables. `AiPersonality` is a client-side type and a backend constant; neither requires persistence.
