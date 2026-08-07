# XP & Progression — Implementation Specification

**Level:** Specification
**Status:** Authoritative
**Source:** FR-060–062; feature-xp-progression.md; ADR-001; ADR-002; Game Economy
**Parent:** [Epic E3 — Progression](epic.md)
**See also:** [feature-xp-progression.md](feature-xp-progression.md), [spec-achievements.md](spec-achievements.md)

---

## Data Models

### PlayerProgression

```json
{
  "player_id": "uuid",
  "total_xp": 1450,
  "current_level": 3,
  "xp_to_next_level": 1600,
  "updated_at": "ISO8601"
}
```

### XPEvent

```json
{
  "id": "uuid",
  "player_id": "uuid",
  "source": "race_completion | correct_answer | perfect_streak | daily_challenge | championship",
  "amount": 100,
  "race_id": "uuid | null",
  "created_at": "ISO8601"
}
```

`XPEvent` records are append-only. They are never modified or deleted. `total_xp` is always derivable by summing all `XPEvent.amount` for a `player_id`.

---

## XP Award Table

| Source | XP Awarded |
|--------|-----------|
| Race completion | +100 |
| Correct answer | +20 |
| Perfect-answer streak (5 consecutive) | +10 bonus |
| Daily challenge completion | +200 |
| Championship race completion | +500 |

XP is never deducted (FR-062).

---

## Level Formula

```
level(total_xp) = floor(sqrt(total_xp / 100))
```

Inverse (XP required to reach a level):

```
xp_for_level(level) = 100 × level²
```

Example milestones:

| Level | XP Required |
|-------|------------|
| 1 | 100 |
| 2 | 400 |
| 3 | 900 |
| 5 | 2,500 |
| 10 | 10,000 |
| 20 | 40,000 |

`xp_to_next_level` in the response = `xp_for_level(current_level + 1) - total_xp`.

---

## XP Award Workflow

Triggered by `POST /api/v1/races/{id}/results`.

```
1. Receive RaceResult (validate idempotency_key)
2. If idempotency_key already processed → return cached result
3. Calculate XP components:
     race_xp     = 100 (always on completion)
     answer_xp   = result.correct_answers × 20
     streak_xp   = floor(result.longest_streak / 5) × 10
     mode_bonus  = 500 if mode == championship else 0
     total       = race_xp + answer_xp + streak_xp + mode_bonus
4. Credit XP: INSERT XPEvent(source=race_completion, amount=total, race_id=...)
   (or split into individual events per source — implementation choice)
5. Recompute current_level = floor(sqrt(new_total_xp / 100))
6. If current_level > previous_level → emit LevelUpEvent(player_id, new_level)
7. Persist: UPDATE PlayerProgression SET total_xp, current_level, updated_at
8. Return updated PlayerProgression in response
```

Steps 4–7 execute within a single database transaction.

---

## Level-Up Event

`LevelUpEvent` is a domain event consumed by:
- Achievement system (checks for level-based achievements)
- Frontend (triggers level-up animation and notification)

```json
{
  "type": "LevelUpEvent",
  "player_id": "uuid",
  "new_level": 4,
  "previous_level": 3,
  "total_xp": 1600,
  "occurred_at": "ISO8601"
}
```

---

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/v1/players/{id}/progression` | Return current PlayerProgression |
| `POST` | `/api/v1/races/{id}/results` | Submit race result; triggers XP award |

---

## Edge Cases

1. **XP overflow / level cap** — no enforced cap in v1.0. The formula handles arbitrarily large XP values. If a cap is introduced in a future version, it requires a documented ADR update.
2. **Duplicate result submission** — `idempotency_key` from `RaceResult` is stored on first processing. A second call with the same key returns the original `PlayerProgression` without writing a new `XPEvent`.
3. **Race result arrives after session timeout** — accept it; there is no expiry on result submission. The race was played legitimately.
4. **Level-up and achievement unlock in same event cycle** — both events are emitted within the same transaction. The frontend queues them and presents level-up first, then achievement (consistent ordering).
5. **`correct_answers` count exceeds `problems_solved`** — reject with HTTP 422 (`correct_answers` cannot be greater than `problems_solved`).
6. **Daily challenge XP** — daily challenges are a separate award path; they do not go through the race result endpoint. A dedicated `POST /api/v1/players/{id}/daily-challenge` endpoint handles this.

---

## Manual Verification Steps

1. Complete a Quick Race with 7 correct answers out of 8. Confirm XP awarded = 100 (race) + 140 (answers) = 240. Confirm `PlayerProgression.total_xp` increases by 240.
2. Check the level formula: if total XP was 360 before (level 1), after +240 it is 600. `floor(sqrt(600/100))` = `floor(2.449)` = 2. Confirm the player is now level 2.
3. Submit the same race result again (same `idempotency_key`). Confirm XP is not re-awarded and the progression response is identical.
4. Complete enough races to trigger a level-up during the race results screen. Confirm the level-up animation plays on the results screen.
5. Open the Parent Dashboard. Confirm XP and level shown matches `GET /api/v1/players/{id}/progression`.
6. Verify `xp_to_next_level` is always `xp_for_level(current_level + 1) - total_xp` and is never negative.

---

## Acceptance Criteria

- [ ] XP formula matches `floor(sqrt(total_xp / 100))` exactly.
- [ ] XP is never deducted from a player.
- [ ] Race result submission is idempotent; XP is awarded at most once per race.
- [ ] `LevelUpEvent` is emitted whenever a player crosses a level boundary.
- [ ] XP events are append-only and never modified.
- [ ] `correct_answers > problems_solved` is rejected with HTTP 422.
- [ ] `total_xp` is always derivable by summing all `XPEvent` records for the player.
