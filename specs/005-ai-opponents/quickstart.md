# Quickstart: AI Opponents

**Branch**: `005-ai-opponents` | **Date**: 2026-08-10

---

## Scenario 1: Race with a single Speedster opponent (determinism check)

**Goal**: Verify that the Speedster leads checkpoints 1–3 and a replay with the same seed produces identical results.

**Steps**:

1. Call `createRng(42)` to produce `rng`.
2. Construct a `RaceConfig` with `seed: 42`, one human runner, one AI runner with `personality = PERSONALITIES.speedster`, `tier: 3`.
3. Call `createRaceEngine(config)`.
4. Transition to `RACING`.
5. For each of 8 checkpoints, call `submitAnswer({ isCorrect: true })` with a 1500ms stub response time (perfect tier).
6. At each checkpoint, log the AI runner's `totalDistanceMetres` from `getState().runners`.
7. Observe that the AI runner's per-checkpoint distance gain is higher in checkpoints 1–3 than in checkpoints 7–8.
8. Repeat steps 2–7 with a fresh engine (same seed). Confirm all 8 AI `totalDistanceMetres` values are identical to the first run.

**Expected outcome**: Identical checkpoint-by-checkpoint distances across both runs. Checkpoint 1–3 distances larger than checkpoint 7–8 distances for the Speedster.

---

## Scenario 2: Five-opponent race, unique movement per opponent

**Goal**: Verify that 5 opponents of the same personality produce distinct movement sequences.

**Steps**:

1. Construct a `RaceConfig` with `seed: 99`, one human runner, and 5 AI runners all using `personality = PERSONALITIES.balanced`, `tier: 3`.
2. Create the race engine and run all 8 checkpoints.
3. Compare each AI runner's `obstacleResults[i].distanceMetres` for `i = 0..7` across all 5 AI runners.
4. Assert that at least one checkpoint exists where not all 5 runners produced the same distance.

**Expected outcome**: At least one checkpoint where distances differ across the 5 runners (per-opponent RNG independence).

---

## Scenario 3: Zero-opponent race completes without error

**Goal**: Verify that training mode (no AI) runs cleanly.

**Steps**:

1. Construct a `RaceConfig` with `seed: 1`, one human runner, no AI participants, `tier: 2`, `mode: 'training'`.
2. Create the race engine, transition to `RACING`.
3. Submit 8 correct answers.
4. Confirm `getState().state` is `'RESULTS'` and `getSummary()` returns a summary with 1 participant.

**Expected outcome**: No errors, 1-participant summary returned.

---

## Scenario 4: GET /api/v1/opponents/personalities returns 5 entries

**Goal**: Verify the backend personalities endpoint.

**Steps**:

1. Start the backend with `uvicorn app.main:app`.
2. `curl http://localhost:8000/api/v1/opponents/personalities`
3. Parse the JSON array.
4. Assert `array.length === 5`.
5. Assert each entry has `id`, `name`, `accuracyRate`, `baseResponseTimeMs`, `responseTimeVarianceMs`, `speedProfile`, `tierOffset`.
6. Assert `speedProfile` values are one of: `uniform`, `front_loaded`, `back_loaded`, `random`.
7. Call the endpoint without any `Authorization` header. Assert `200 OK`.

**Expected outcome**: 200 OK, array of 5 personality objects matching the contract, no auth required.

---

## Scenario 5: Slow Starter visibly catches up in later checkpoints

**Goal**: Confirm the back_loaded speed profile produces stronger late-race performance.

**Steps**:

1. Construct a race with `seed: 7`, one human, one AI with `personality = PERSONALITIES.slowStarter`, `tier: 3`.
2. Run all 8 checkpoints with correct human answers.
3. For the AI runner, collect `distanceMetres` per checkpoint from `obstacleResults`.
4. Compute average distance for checkpoints 0–2 ("early") and checkpoints 5–7 ("late").
5. Assert late average ≥ early average.

**Expected outcome**: Slow Starter's per-checkpoint distances are higher in the last three checkpoints than the first three.

---

## Scenario 6: Tied distance tiebreaker is deterministic

**Goal**: Confirm that tied runners always resolve to the same rank on replay.

**Steps**:

1. Construct two AI runners with `personality = PERSONALITIES.steady`, same seed, same tier.
2. Force identical movement by seeding both with the same per-opponent RNG (verify by running the race with a fresh engine twice).
3. Call `getSummary()` both times.
4. Assert `participants[0].avatar_id` is the same value in both runs.

**Expected outcome**: Same runner is ranked 1st on both replays (lexicographic `runnerId` tiebreaking).
