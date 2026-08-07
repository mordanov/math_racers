# Feature F1.1 — Race Engine

**Level:** Feature
**Status:** Authoritative
**Source:** GDD Chapter 6
**Parent:** [Epic E1 — Gameplay](epic.md)

---

## Purpose

The Race Engine governs all physical movement on the track. It translates mathematical answers into runner positions, manages the race state machine, and enforces the single authoritative game clock.

---

## Race Structure

A race consists of exactly **8 mathematical checkpoints** (obstacles).

```
Start → Obstacle 1 → Obstacle 2 → … → Obstacle 8 → Finish
```

Each checkpoint presents one mathematics problem. Answering it moves the runner forward.

---

## Movement Model

| Speed Tier | Condition | Movement |
|------------|-----------|----------|
| Perfect | Correct, < 2 s | +18 m |
| Excellent | Correct, < 4 s | +15 m |
| Good | Correct, < 6 s | +12 m |
| Slow | Correct, ≥ 6 s | +9 m |
| Incorrect | Any wrong answer | +0 m |

Formula: `Movement = Base Distance × Accuracy Modifier × Speed Modifier`

Accuracy modifier: Correct = 1.0, Incorrect = 0.3 (applied at base = 0 for incorrect, so result is 0)
Speed modifier: Fast = 1.2, Normal = 1.0, Slow = 0.8

---

## Race Parameters

- Participants: 1–5 runners.
- Runner types: one human player + up to 4 AI opponents.
- Track length: scaled to accommodate 8 obstacles.

---

## State Machine

```
IDLE → LOBBY → COUNTDOWN → RACING → FINISHING → RESULTS
```

| State | Description |
|-------|-------------|
| IDLE | No race loaded |
| LOBBY | Players/mode selected, avatars loaded |
| COUNTDOWN | 3-2-1-GO animation |
| RACING | Active gameplay, timer running |
| FINISHING | One runner has crossed finish; others complete their obstacle |
| RESULTS | All runners finished; scores displayed |

Illegal state transitions must be rejected.

---

## Game Clock

A single authoritative game clock governs all race timing.

- The clock starts at the COUNTDOWN→RACING transition.
- Per-obstacle timing uses the same clock source.
- No network time synchronisation during active play (all local).
- Clock must produce consistent results regardless of frame rate.

---

## Determinism

Identical inputs (seed, difficulty, player answers, timestamps) must produce identical race outcomes.

Race simulation runs entirely in the browser with no server round-trips during active gameplay.

---

## Specification

See [spec-race-engine.md](spec-race-engine.md) for implementation-level detail.

---

## Acceptance Criteria

- [ ] Race proceeds through exactly 8 obstacles.
- [ ] Movement distances match the table for all 5 speed tiers.
- [ ] Incorrect answer always results in 0 m movement.
- [ ] State machine rejects invalid transitions.
- [ ] Race result is deterministic given the same inputs.
- [ ] Rendering runs at ≥ 30 FPS without affecting timing correctness.
