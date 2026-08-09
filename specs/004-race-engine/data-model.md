# Data Model — Race Engine

**Branch**: `004-race-engine` | **Date**: 2026-08-10

---

## Frontend Types (TypeScript)

These types live in `frontend/src/engine/race/types.ts`.

### RaceState (state machine)

```typescript
export type RaceState =
  | 'IDLE'
  | 'LOBBY'
  | 'COUNTDOWN'
  | 'RACING'
  | 'FINISHING'
  | 'RESULTS';
```

### Legal Transitions

```typescript
// transition table: LEGAL_TRANSITIONS[from] = Set<to>
IDLE       → { LOBBY }
LOBBY      → { COUNTDOWN }
COUNTDOWN  → { RACING }
RACING     → { FINISHING }
FINISHING  → { RESULTS }
RESULTS    → { LOBBY }
```

Any transition not listed is illegal and must throw / return false.

---

### MovementTier

```typescript
export type MovementTier = 'perfect' | 'excellent' | 'good' | 'slow' | 'incorrect';

export interface TierResult {
  tier: MovementTier;
  distanceMetres: number;  // 18 | 15 | 12 | 9 | 0
}
```

Boundaries (from spec):
- `responseTimeMs < 2000` → perfect (18 m)
- `responseTimeMs < 4000` → excellent (15 m)
- `responseTimeMs < 6000` → good (12 m)
- `responseTimeMs >= 6000` → slow (9 m)
- `isCorrect === false` → incorrect (0 m)

---

### ObstacleResult

```typescript
export interface ObstacleResult {
  obstacleIndex: number;   // 0–7
  isCorrect: boolean;
  responseTimeMs: number;
  distanceMetres: number;  // 0 | 9 | 12 | 15 | 18
  tier: MovementTier;
}
```

---

### RunnerState

```typescript
export interface RunnerState {
  runnerId: string;           // UUID for human; deterministic id for AI
  isHuman: boolean;
  totalDistanceMetres: number; // 0–144, never decreases
  obstaclesCompleted: number;  // 0–8
  obstacleResults: ObstacleResult[];
  finishTime: number | null;  // game clock ms when obstacle 8 completed; null if not finished
}
```

---

### AiPersonality

```typescript
export interface AiPersonality {
  id: string;
  baseResponseTimeMs: number;    // mean response time for the tier
  responseTimeVarianceMs: number; // applied as Gaussian stddev
  accuracyRate: number;          // 0.0–1.0 probability of correct answer
}
```

---

### RaceConfig

```typescript
export interface RaceConfig {
  raceId: string;       // UUID, generated before race starts
  seed: number;
  tier: Tier;           // imported from engine/math/types
  mode: RaceMode;
  participants: ParticipantConfig[];
}

export type RaceMode = 'quick' | 'championship' | 'duel' | 'training';

export interface ParticipantConfig {
  runnerId: string;
  isHuman: boolean;
  avatarId: string;
  personality?: AiPersonality;  // undefined for human runner
}
```

---

### RaceEngineState

```typescript
export interface RaceEngineState {
  state: RaceState;
  config: RaceConfig | null;
  clockMs: number;          // monotonic game clock, ms since RACING start
  obstacleClockMs: number;  // ms since current problem became visible
  currentObstacle: number;  // 0–7 (index); -1 when not in RACING
  runners: RunnerState[];
  problemSet: ProblemSet | null;  // imported from engine/math
}
```

---

### RaceSummary (persisted after race)

```typescript
export interface RaceSummary {
  race_id: string;
  seed: string;
  difficulty_tier: Tier;
  mode: RaceMode;
  started_at: string;    // ISO 8601
  completed_at: string;  // ISO 8601
  participants: ParticipantSummary[];
}

export interface ParticipantSummary {
  avatar_id: string;     // UUID for human; 'ai' prefix for AI runners
  position: number;      // 1-based final position
  problems_correct: number;   // 0–8
  average_response_ms: number;
  total_distance: number;     // 0–144
  xp_earned: number;
}
```

---

## Backend Model (Python / SQLAlchemy)

These live in `backend/app/races/` (new bounded context, analogous to `app/mathematics/`).

### races table

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen |
| seed | TEXT | NOT NULL |
| difficulty_tier | INTEGER | NOT NULL, 1–6 |
| mode | TEXT | NOT NULL, enum |
| started_at | TIMESTAMPTZ | NOT NULL |
| completed_at | TIMESTAMPTZ | NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL, default now() |

### race_participants table

| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK, default gen |
| race_id | UUID | FK → races.id, NOT NULL |
| avatar_id | TEXT | NOT NULL (UUID or 'ai-{n}') |
| position | INTEGER | NOT NULL, 1–5 |
| problems_correct | INTEGER | NOT NULL, 0–8 |
| average_response_ms | INTEGER | NOT NULL, ≥ 0 |
| total_distance | INTEGER | NOT NULL, 0–144 |
| xp_earned | INTEGER | NOT NULL, ≥ 0 |

### State Transitions (validation rules)

- `difficulty_tier` MUST be in {1, 2, 3, 4, 5, 6}
- `mode` MUST be in {'quick', 'championship', 'duel', 'training'}
- `position` MUST be unique per race (no ties in persisted positions — tiebreak resolved before persistence)
- `total_distance` MUST be ≤ 144
- `problems_correct` MUST be ≤ 8
