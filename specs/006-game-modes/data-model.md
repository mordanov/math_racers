# Data Model: Game Modes

**Branch**: `006-game-modes` | **Date**: 2026-08-10

---

## Existing models (unchanged)

### Race (existing — `backend/app/races/models.py`)

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | PK |
| `seed` | String | NOT NULL |
| `difficulty_tier` | Integer | NOT NULL, BETWEEN 1 AND 6 |
| `mode` | String | NOT NULL, IN ('quick', 'championship', 'duel', 'training') |
| `started_at` | DateTime(tz) | NOT NULL |
| `completed_at` | DateTime(tz) | NOT NULL |
| `created_at` | DateTime(tz) | NOT NULL, server default now() |

### RaceParticipant (existing — migration required)

| Column | Type | Current Constraints | New Constraints |
|--------|------|---------------------|-----------------|
| `id` | UUID | PK | — |
| `race_id` | UUID | FK races.id | — |
| `avatar_id` | String | NOT NULL | — |
| `position` | Integer | NOT NULL, BETWEEN 1 AND 5 | **NULLABLE**, CHECK (position IS NULL OR position BETWEEN 1 AND 5) |
| `problems_correct` | Integer | NOT NULL, BETWEEN 0 AND 8 | — |
| `average_response_ms` | Integer | NOT NULL, >= 0 | — |
| `total_distance` | Integer | NOT NULL, BETWEEN 0 AND 144 | — |
| `xp_earned` | Integer | NOT NULL, >= 0 | — |

**Migration**: Remove `CHECK BETWEEN 1 AND 5` constraint, make `position` nullable. Add new nullable-aware check constraint.

---

## New models

### Championship (`backend/app/championships/models.py`)

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | PK, default uuid4 |
| `account_id` | UUID | FK accounts.id, NOT NULL |
| `total_races` | Integer | NOT NULL, BETWEEN 3 AND 7 |
| `races_completed` | Integer | NOT NULL, DEFAULT 0 |
| `status` | String | NOT NULL, DEFAULT 'active', IN ('active', 'completed') |
| `created_at` | DateTime(tz) | NOT NULL, server default now() |
| `updated_at` | DateTime(tz) | NOT NULL, server default now(), onupdate now() |

Relationships:
- `championship_races`: one-to-many → `ChampionshipRace`

### ChampionshipRace (`backend/app/championships/models.py`)

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | UUID | PK, default uuid4 |
| `championship_id` | UUID | FK championships.id CASCADE, NOT NULL |
| `race_id` | UUID | FK races.id, NOT NULL, UNIQUE |
| `race_index` | Integer | NOT NULL — 0-based position in series |
| `avatar_id` | String | NOT NULL — identifies the runner |
| `is_player` | Boolean | NOT NULL — true for the human player row |
| `finishing_position` | Integer | NOT NULL, BETWEEN 1 AND 5 |
| `points_earned` | Integer | NOT NULL, BETWEEN 0 AND 10 |

**Note**: One row per participant per championship race. A 5-runner race creates 5 `ChampionshipRace` rows sharing the same `race_id` and `race_index`.

---

## State transitions

### Championship

```
created → active (on POST /api/v1/championships)
active  → completed (on PATCH when races_completed == total_races)
```

---

## Frontend type additions (`frontend/src/engine/race/types.ts`)

No new types needed for Quick Race or Duel — these use the existing `RaceSummary` shape.

### Training summary extension

`RaceSummary` already has `mode: RaceMode`. The `ParticipantSummary.position` needs to become optional for training:

```ts
// ParticipantSummary (updated)
export interface ParticipantSummary {
  avatar_id: string;
  position: number | null;   // null for training
  problems_correct: number;
  average_response_ms: number;
  total_distance: number;
  xp_earned: number;
}
```

The backend Pydantic schema also needs `position: Optional[int]` with the same validation.

---

## XP formula (client-side, `raceEngine.ts`)

| Mode | Rule |
|------|------|
| Quick Race | 10 XP per correct answer |
| Duel | 10 XP per correct answer |
| Championship | Points-table value (10/6/3/1/0) × 10 XP; plus 5 XP per correct answer |
| Training | 5 XP per correct answer; no completion bonus |

Formula is computed in `getSummary()` based on `mode` from `RaceConfig`.
