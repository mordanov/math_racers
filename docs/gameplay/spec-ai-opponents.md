# AI Opponents — Implementation Specification

**Level:** Specification
**Status:** Authoritative
**Source:** FR-021, FR-023; feature-ai-opponents.md; ADR-004
**Parent:** [Epic E1 — Gameplay](epic.md)
**See also:** [feature-ai-opponents.md](feature-ai-opponents.md), [spec-race-engine.md](spec-race-engine.md)

---

## Data Models

### AIOpponent

```json
{
  "id": "uuid",
  "name": "string",
  "avatar_id": "uuid | null",
  "personality": "steady | speedster | slow_starter | unpredictable | balanced",
  "current_position": 0,
  "accumulated_distance": 0,
  "tier_offset": 0
}
```

`tier_offset` is applied to the player's current tier: `opponent_tier = clamp(player_tier + tier_offset, 1, 6)`.

---

## Personality Parameters

| Personality | `base_accuracy` | `speed_profile` | `variability` | `tier_offset` |
|-------------|-----------------|-----------------|----------------|---------------|
| Steady | 0.80 | uniform | 0.05 | 0 |
| Speedster | 0.70 | front_loaded | 0.10 | +1 |
| Slow Starter | 0.75 | back_loaded | 0.08 | 0 |
| Unpredictable | 0.65 | random | 0.25 | 0 |
| Balanced | 0.78 | uniform | 0.07 | 0 |

- **`base_accuracy`** — probability of answering correctly at any given checkpoint.
- **`speed_profile`** — determines how `speed_modifier` varies across checkpoints 1–8.
- **`variability`** — ±range applied to `base_accuracy` on each step.
- **`tier_offset`** — adjusts the mathematical difficulty tier for this opponent.

### Speed Profile Definitions

| Profile | Checkpoints 1–3 | Checkpoints 4–6 | Checkpoints 7–8 |
|---------|-----------------|-----------------|-----------------|
| `uniform` | 1.0× | 1.0× | 1.0× |
| `front_loaded` | 1.2× | 1.0× | 0.9× |
| `back_loaded` | 0.85× | 1.0× | 1.25× |
| `random` | rng(0.7–1.3)× | rng(0.7–1.3)× | rng(0.7–1.3)× |

The multiplier is applied to the base movement distance for the opponent's answer quality tier.

---

## Simulation Algorithm

All simulation runs in the browser. The backend is never called during a race.

```
function simulateStep(opponent, checkpoint_index, rng):
  accuracy = opponent.base_accuracy + variabilityOffset(opponent.variability, rng)
  accuracy = clamp(accuracy, 0.0, 1.0)

  answered_correctly = (rng.next() < accuracy)

  if not answered_correctly:
    return 0   # incorrect → no movement (FR-023)

  response_time = sampleResponseTime(opponent.speed_profile, checkpoint_index, rng)

  if response_time < 2.0:
    base_distance = 18
  elif response_time < 4.0:
    base_distance = 15
  elif response_time < 6.0:
    base_distance = 12
  else:
    base_distance = 9

  speed_multiplier = speedMultiplier(opponent.speed_profile, checkpoint_index, rng)
  return round(base_distance * speed_multiplier)


function sampleResponseTime(profile, index, rng):
  base = 3.5  # seconds, mid-range default
  if profile == front_loaded:
    base = lerp(1.5, 5.0, index / 7)
  elif profile == back_loaded:
    base = lerp(5.0, 1.5, index / 7)
  elif profile == random:
    base = rng.uniform(1.0, 7.0)
  return base + rng.uniform(-0.5, 0.5)
```

### Race Simulation Loop

```
function simulateRace(opponents, player_tier, seed):
  rng = seededRandom(seed)

  for checkpoint in 1..8:
    for opponent in opponents:
      distance = simulateStep(opponent, checkpoint, rng)
      opponent.accumulated_distance += distance
      opponent.current_position = checkpointFromDistance(opponent.accumulated_distance)
```

The loop progresses synchronously per checkpoint alongside player actions. Opponent results for checkpoint N are computed immediately after the player submits their answer for checkpoint N.

---

## Difficulty Calibration

```
function calibrateOpponents(opponents, player_tier):
  for opponent in opponents:
    opponent_tier = clamp(player_tier + opponent.tier_offset, 1, 6)
    // opponent.tier_offset is fixed per personality (see table above)
```

Calibration occurs once at race start and is not updated during the race.

---

## API Endpoints

No backend endpoints are required for AI opponent simulation. The entire simulation runs client-side.

The backend provides opponent configuration at race setup time:

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/v1/opponents/personalities` | Return the 5 personality definitions with display names |
| `POST` | `/api/v1/races` | Include `opponents` array in the race session config |

---

## Edge Cases

1. **All opponents finish checkpoint 8 simultaneously** — sort by cumulative distance at the time of the final checkpoint; if still tied, apply the opponent's `id` as a tiebreaker (deterministic).
2. **`opponent_tier` clamp produces tier 0** — `clamp(..., 1, 6)` prevents this; if somehow reached, default to tier 1.
3. **`variability` RNG produces accuracy > 1.0 or < 0.0** — clamp before use; never panic.
4. **Single-player race with zero AI opponents** — valid; the race proceeds with only the player. No opponent simulation loop runs.
5. **Race with 5 opponents of identical personality** — each opponent gets an independent RNG sequence derived from `seed + index`; their results diverge naturally.
6. **Seed-identical replay** — same `seed` + same `personality` + same `player_tier` always produces identical opponent movement sequence.

---

## Manual Verification Steps

1. Start a Quick Race with one Steady opponent. Watch all 8 checkpoints. Confirm the opponent advances at a consistent, uniform pace without large swings.
2. Start a Quick Race with one Speedster opponent. Confirm the Speedster leads in checkpoints 1–3 and slows slightly in checkpoints 7–8.
3. Start a Quick Race with one Slow Starter opponent. Confirm the Slow Starter lags in checkpoints 1–3 and catches up in checkpoints 7–8.
4. Open the browser's Network tab. Start a race with AI opponents. Confirm zero network requests are made during race simulation.
5. Complete a race. Note the results. Replay the same race with identical settings (same seed, same avatars, same tier). Confirm opponent positions at every checkpoint are identical.
6. Start a race with 4 AI opponents. Confirm all 4 are present in the race lane and all produce distinct movement patterns.

---

## Acceptance Criteria

- [ ] All 5 personality types produce visually distinct movement patterns observable in a single race.
- [ ] Opponent simulation makes no backend calls during an active race.
- [ ] Identical `(seed, personalities, player_tier)` always produces identical opponent positions.
- [ ] `opponent_tier` is always in [1, 6].
- [ ] Incorrect simulated answers produce zero movement (FR-023).
- [ ] A race with zero AI opponents (Training Mode) runs without error.
- [ ] Tied final positions are broken deterministically.
