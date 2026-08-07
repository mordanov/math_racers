# Specification — Race Engine

**Level:** Specification
**Status:** Authoritative
**Source:** GDD Chapter 6
**Parent:** [Feature F1.1 — Race Engine](feature-race-engine.md)

---

## State Machine Specification

### States

| State | Entry Condition | Exit Condition |
|-------|----------------|----------------|
| IDLE | Application load or race exit | Mode selected |
| LOBBY | Mode selected | Countdown starts |
| COUNTDOWN | All participants loaded | Countdown reaches 0 |
| RACING | Countdown = 0 | Any runner finishes obstacle 8 |
| FINISHING | First runner crosses finish | All runners complete obstacle 8 |
| RESULTS | All runners finished | User navigates away |

### Illegal Transitions

Any transition not listed above must be rejected. Examples of illegal transitions:
- IDLE → RACING (must go through LOBBY and COUNTDOWN)
- RESULTS → RACING (must return to LOBBY first)
- COUNTDOWN → IDLE (cannot abort during countdown)

---

## Movement Calculation

```
function calculateMovement(isCorrect, responseTimeMs, baseTier):
  if not isCorrect:
    return 0

  if responseTimeMs < 2000:
    return 18  # Perfect
  elif responseTimeMs < 4000:
    return 15  # Excellent
  elif responseTimeMs < 6000:
    return 12  # Good
  else:
    return 9   # Slow but correct
```

All distances are in metres. The track total length = sum of all 8 obstacle movements at the "Perfect" tier = 144 m maximum per runner.

---

## Game Clock

- Implemented as a monotonic counter, ticked by `requestAnimationFrame`.
- Start: COUNTDOWN state end (when "GO!" appears).
- Per-obstacle time starts when the problem card becomes visible.
- Per-obstacle time ends when the player submits an answer.
- The clock is not affected by tab visibility changes (pause logic handled separately).

---

## AI Runner Simulation

For each obstacle, each AI runner computes:

```
baseResponseTime = tierBaseTime[currentTier]
personalityModifier = personality.responseTimeVariance()
noise = randomGaussian(mean=0, stddev=tierStddev[currentTier])
aiResponseTime = baseResponseTime + personalityModifier + noise
aiMovement = calculateMovement(aiAccuracy(), aiResponseTime)
```

AI runners are updated sequentially, not simultaneously, to avoid visual stacking.

---

## Determinism Requirements

- The race seed determines: problem sequence, AI variance samples, initial positions.
- Given the same seed and difficulty tier, an AI-only race produces identical results.
- Human response times introduce non-determinism by design (they are real user actions).

---

## Race Summary Record

After each race, persist:

```json
{
  "race_id": "uuid",
  "seed": "string",
  "difficulty_tier": 1-6,
  "mode": "quick|championship|duel|training",
  "started_at": "ISO 8601",
  "completed_at": "ISO 8601",
  "participants": [
    {
      "avatar_id": "uuid|ai",
      "position": 1-5,
      "problems_correct": 0-8,
      "average_response_ms": 0,
      "total_distance": 0-144,
      "xp_earned": 0
    }
  ]
}
```

---

## Edge Cases

| Scenario | Behaviour |
|----------|-----------|
| Player submits after timer expires | Treat as "Slow" tier if correct; incorrect if wrong |
| Two runners finish simultaneously | Lower array index wins tiebreak (first in participant list) |
| Player disconnects mid-race | Race continues client-side; results synced on reconnect |
| Browser tab loses focus during race | Clock pauses; resume on tab focus |
| Race with 1 participant (Training) | No position indicator; no opponent columns |
| Incorrect answer at obstacle 8 (final) | 0 m movement; race ends after the problem is resolved |

---

## Manual Verification Steps

1. Start a Quick Race. Confirm exactly 8 obstacle problems appear.
2. Answer each problem correctly, rapidly. Verify movement matches "Perfect" (18 m) tier.
3. Answer one problem slowly (> 6 s). Verify movement is 9 m (Slow correct).
4. Answer one problem incorrectly. Verify 0 m movement and no negative distance.
5. Complete the race. Verify the Results screen shows correct positions.
6. Open DevTools → Network tab. Confirm no API calls fire during active race.
7. Run the same seed twice in Training mode. Confirm identical problem sequence.
