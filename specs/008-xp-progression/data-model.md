# Data Model: XP & Player Progression

**Branch**: `008-xp-progression` | **Date**: 2026-08-11

## New Entities

### PlayerProgression

Tracks the running XP total and computed level for one account (player).

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `account_id` | UUID | PK, FK → accounts.id ON DELETE CASCADE | One row per player |
| `total_xp` | Integer | NOT NULL, ≥ 0, DEFAULT 0 | Always derivable from sum of XPEvent.amount |
| `current_level` | Integer | NOT NULL, ≥ 0, DEFAULT 0 | `floor(sqrt(total_xp / 100))` |
| `updated_at` | DateTime(tz) | NOT NULL, DEFAULT now() | Updated on every XP award |

**Indexes**:
- PK on `account_id` (one record per player — upsert pattern)

**Invariants**:
- `current_level` is always `floor(sqrt(total_xp / 100))`
- `total_xp` is always equal to the sum of all `XPEvent.amount` for this `account_id`
- `total_xp` is monotonically non-decreasing

---

### XPEvent

Immutable ledger of every XP credit. Never updated, never deleted.

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | |
| `account_id` | UUID | NOT NULL, FK → accounts.id ON DELETE CASCADE | |
| `source` | Varchar | NOT NULL | One of: `race_completion`, `correct_answer`, `streak_bonus`, `championship_bonus` |
| `amount` | Integer | NOT NULL, > 0 | XP credited |
| `race_id` | UUID | NULL, FK → races.id ON DELETE SET NULL | NULL for non-race sources |
| `created_at` | DateTime(tz) | NOT NULL, DEFAULT now() | |

**Indexes**:
- `idx_xp_events_account_id` on `account_id`
- `idx_xp_events_race_id` on `race_id`

**Constraints**:
- `CHECK source IN ('race_completion', 'correct_answer', 'streak_bonus', 'championship_bonus')`
- `CHECK amount > 0`

**Invariants**:
- Rows are append-only — no UPDATE or DELETE ever issued
- One or more rows are inserted per race result submission (implementation may insert one consolidated row or multiple source rows; the sum must equal the calculated total)

---

## Modified Entities

### RaceParticipant (existing — migration required)

Add `longest_streak` column to support streak bonus calculation.

| New Column | Type | Constraints | Notes |
|------------|------|-------------|-------|
| `longest_streak` | Integer | NOT NULL, DEFAULT 0, ≥ 0 | Longest consecutive correct-answer streak in this race |

**Migration**: `0008_add_progression.py` — adds `longest_streak` to `race_participants`, creates `player_progressions` and `xp_events` tables.

---

## Relationships

```
accounts (1) ──────────── (0..1) player_progressions
    │
    └─── (0..*) xp_events
                    │
                    └─── (0..1) races  [race_id nullable]

races (1) ──────── (1..*) race_participants
                              [+ longest_streak column]
```

---

## XP Calculation Logic (domain, not stored)

These are computation rules executed in the domain service, not stored schema:

```
race_xp          = 100
correct_xp       = problems_correct × 20
streak_xp        = floor(longest_streak / 5) × 10
championship_xp  = 500 if mode == 'championship' else 0
total_xp_delta   = race_xp + correct_xp + streak_xp + championship_xp
```

```
new_total_xp     = old_total_xp + total_xp_delta
new_level        = floor(sqrt(new_total_xp / 100))
level_up         = new_level > old_level
xp_to_next_level = (new_level + 1)² × 100 − new_total_xp
```

---

## LevelUpEvent (in-memory / response only, not persisted)

Produced by the domain service when `new_level > old_level`. Returned in the race submission response. Not stored in a DB table.

```json
{
  "type": "LevelUpEvent",
  "previous_level": 1,
  "new_level": 2,
  "total_xp": 600
}
```
