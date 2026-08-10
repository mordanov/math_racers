# Quickstart: Game Modes Integration Scenarios

**Branch**: `006-game-modes` | **Date**: 2026-08-10

---

## Scenario 1 — Quick Race (happy path)

```
1. Player has an avatar configured (frontend guard passes)
2. Client generates race_id = uuidv4(), seed = random int
3. Player completes race; engine transitions to RESULTS
4. useRaceEngine calls postRaceSummary({ mode: "quick", race_id, seed, participants: [...], xp_earned per correct answer })
5. POST /api/v1/races → 201
6. Results screen displays position, XP, correct/incorrect count
```

**Retry / idempotency**: If step 5 fails, `postRaceSummary` retries once. On the second attempt the server returns 409 (duplicate `race_id`), which `raceApi.ts` treats as success (not an error worth surfacing).

---

## Scenario 2 — Training exit

```
1. mode = "training"; engine has no finish line
2. Player presses "Exit"; engine is forced to RESULTS state via explicit transition
3. Human participant summary built with position = null, xp_earned = 5 * correct_answers
4. POST /api/v1/races → 201
```

**Engine change needed**: `raceEngine.ts` must support a `forceComplete()` method (or equivalent) that transitions the engine from RACING → RESULTS without checking `OBSTACLE_COUNT`. Training has no obstacles to complete; it runs in a loop with the player answering problems until exit.

---

## Scenario 3 — Championship (full series)

```
1. POST /api/v1/championships { total_races: 3 } → { championship_id }
2. Race 1: client runs race, POST /api/v1/races → 201
3. PATCH /api/v1/championships/{id}/races/{race1_id} { race_index: 0, participants: [...] } → standings updated
4. Race 2: same flow → race_index: 1
5. Race 3 (final): PATCH → standings.status transitions to "completed"
6. Final standings screen rendered from response
```

**Resumability**: Championship is retrieved via `GET /api/v1/championships/{id}` when the player returns. `races_completed` tells the frontend which race to run next. The next `race_index = races_completed`.

---

## Scenario 4 — Duel

```
1. Frontend reads player's current difficulty tier from /api/v1/difficulty
2. Selects Balanced personality with tierOffset = 0 → same tier
3. Clamps to minimum tier 1
4. mode = "duel"; exactly 1 AI participant in RaceConfig
5. Race runs; result submitted as POST /api/v1/races with mode "duel"
```

No new backend endpoints needed for Duel.

---

## Scenario 5 — Avatar guard

```
1. Race Setup screen mounts
2. Frontend checks current avatar context (avatarId in user session/store)
3. If no avatar: render "Create Avatar" prompt / redirect; disable start button
4. If avatar present: enable start button
```

This is a purely frontend guard. No backend call required for this feature scope.
