# Statistics — Implementation Specification

**Level:** Specification
**Status:** Authoritative
**Source:** FR-070–073, FR-080–083; feature-statistics.md; ADR-002
**Parent:** [Epic E3 — Progression](epic.md)
**See also:** [feature-statistics.md](feature-statistics.md), [spec-xp-progression.md](spec-xp-progression.md)

---

## Data Models

### PlayerStats

```json
{
  "player_id": "uuid",
  "total_races": 47,
  "total_problems_solved": 376,
  "correct_answers": 341,
  "accuracy_all_time": 0.906,
  "avg_response_ms": 3420,
  "favourite_operation": "multiplication",
  "best_streak": 23,
  "updated_at": "ISO8601"
}
```

`accuracy_all_time` = `correct_answers / total_problems_solved`. Recomputed on every race result submission. Never stored as a literal float — derived at read time.

`favourite_operation` = the operation with the highest correct-answer count in the player's history.

### AvatarStats

```json
{
  "avatar_id": "uuid",
  "player_id": "uuid",
  "total_races": 12,
  "wins": 4,
  "podiums": 8,
  "best_streak": 11,
  "last_race_at": "ISO8601"
}
```

A "podium" is a finishing position of 1st, 2nd, or 3rd. `wins` = 1st place only.

### RaceSession (History Record)

```json
{
  "id": "uuid",
  "player_id": "uuid",
  "avatar_id": "uuid",
  "mode": "quick_race | championship | training | duel",
  "finishing_position": 1,
  "problems_solved": 8,
  "correct_answers": 7,
  "mistakes": 1,
  "difficulty_tier": 3,
  "xp_earned": 240,
  "duration_seconds": 52,
  "started_at": "ISO8601",
  "finished_at": "ISO8601"
}
```

`RaceSession` records are append-only. They are never modified after creation. Historical records must remain permanently (FR-073).

---

## Aggregation Rules

### Accuracy

```
accuracy = correct_answers / total_problems_solved
```

Guard against division by zero: if `total_problems_solved == 0`, return `null`.

### Average Response Time

Running mean across all problems in all sessions:

```
avg_response_ms = sum(session.avg_response_ms * session.problems_solved
                      for session in all_sessions)
                  / total_problems_solved
```

### Favourite Operation

```
for operation in [addition, subtraction, multiplication, division]:
    score[operation] = count of correct answers for that operation

favourite_operation = argmax(score)
```

Ties broken by alphabetical order.

### Streak

`best_streak` = the longest sequence of consecutive correct answers without an incorrect answer, computed across all sessions. Streak resets on any incorrect answer.

---

## Statistics Update Workflow

Triggered by `POST /api/v1/races/{id}/results` (after XP award succeeds).

```
1. INSERT RaceSession from RaceResult
2. UPDATE PlayerStats:
     total_races += 1
     total_problems_solved += result.problems_solved
     correct_answers += result.correct_answers
     best_streak = max(best_streak, result.longest_streak)
     favourite_operation = recompute()
3. UPDATE AvatarStats for result.avatar_id:
     total_races += 1
     if finishing_position == 1: wins += 1
     if finishing_position <= 3: podiums += 1
     best_streak = max(best_streak, result.longest_streak)
     last_race_at = now()
```

Steps 1–3 execute within a single transaction.

---

## Weekly Summary Computation

`GET /api/v1/players/{id}/weekly-summary`

Computed from `RaceSession` records where `finished_at >= now() - 7 days`.

```json
{
  "period_start": "ISO8601",
  "period_end": "ISO8601",
  "problems_solved": 64,
  "correct_answers": 58,
  "accuracy": 0.906,
  "avg_response_ms": 3100,
  "strongest_operation": "addition",
  "weakest_operation": "division",
  "races_completed": 8,
  "xp_earned": 1920
}
```

`strongest_operation` = highest accuracy operation in the period.
`weakest_operation` = lowest accuracy operation with at least 5 attempts in the period. If fewer than 5 attempts for all operations, return `null`.

---

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/v1/players/{id}/statistics` | Player-level aggregated stats |
| `GET` | `/api/v1/players/{id}/avatars/{avatar_id}/statistics` | Per-avatar stats |
| `GET` | `/api/v1/players/{id}/history` | Paginated RaceSession history (20 per page) |
| `GET` | `/api/v1/players/{id}/history?page=N` | Page N of race history |
| `GET` | `/api/v1/players/{id}/weekly-summary` | 7-day parent dashboard summary |
| `GET` | `/api/v1/players/{id}/personal-records` | Best times, highest streak, best accuracy race |

---

## Edge Cases

1. **First race (no prior stats)** — `PlayerStats` row is created on first race result. `accuracy_all_time` and `avg_response_ms` are computed from that single session. No division-by-zero; guard is in place.
2. **Avatar deleted but stats remain** — `AvatarStats` and `RaceSession` records retain the original `avatar_id`. The avatar name/image is no longer available, so display `"(deleted avatar)"` in the UI. Do not cascade-delete statistics.
3. **History page beyond available records** — return an empty `results` array with `total_pages` and `total_records` correctly computed. Do not return HTTP 404.
4. **Weekly summary with zero races in 7 days** — return the structure with all numeric fields set to 0 and `strongest_operation` / `weakest_operation` set to `null`.
5. **Training mode sessions** — included in all statistics with `finishing_position: null`. They contribute to accuracy, response time, and streak statistics, but not to `wins` or `podiums`.
6. **Statistics export (FR-082)** — `GET /api/v1/players/{id}/export` returns all `RaceSession` records as CSV. The export is parent-only (requires parent authentication scope).

---

## Manual Verification Steps

1. Complete 3 races with the same player. Call `GET /api/v1/players/{id}/statistics`. Confirm `total_races == 3` and `accuracy_all_time` matches the calculation manually.
2. Win a race with a specific avatar. Call `GET /api/v1/players/{id}/avatars/{avatar_id}/statistics`. Confirm `wins == 1` and `podiums == 1`.
3. Complete races on 3 consecutive days. Call `GET /api/v1/players/{id}/weekly-summary`. Confirm `races_completed` and `problems_solved` match the actual races.
4. Call `GET /api/v1/players/{id}/history?page=1`. Confirm the most recent race appears first. Request page 2 and confirm it returns the next 20 (or empty if fewer than 21 races).
5. Delete an avatar. Call `GET /api/v1/players/{id}/history`. Confirm past sessions involving that avatar still appear with `"(deleted avatar)"` label.
6. Complete a Training session of 20 problems. Confirm the session appears in history with `finishing_position: null` and contributes to accuracy statistics.

---

## Acceptance Criteria

- [ ] `RaceSession` records are append-only; no modification after creation.
- [ ] `accuracy_all_time` is computed as `correct_answers / total_problems_solved`; never stored as a literal.
- [ ] Deleted avatars do not cause history records to disappear.
- [ ] Weekly summary covers exactly the last 7 calendar days.
- [ ] History pagination returns consistent ordering (newest first).
- [ ] Training sessions contribute to accuracy and streak statistics but not to wins or podiums.
- [ ] Statistics are updated atomically with race result submission (same transaction).
- [ ] Data export is available to parents and includes all `RaceSession` records.
