# Epic E1 — Gameplay

**Level:** Epic
**Status:** Authoritative
**Source:** GDD Chapters 2, 6, 7, 8
**Parent:** [PRD](../prd.md)

---

## Summary

Deliver the complete race experience: a deterministic race engine, a mathematics engine, adaptive AI opponents, and four game modes — all running client-side with no network round-trips during play.

---

## Features

| Feature | Description | Link |
|---------|-------------|------|
| F1.1 — Race Engine | Movement model, physics, state machine, game clock | [feature-race-engine.md](feature-race-engine.md) |
| F1.2 — Mathematics Engine | Problem generation, validation, difficulty tiers | [feature-math-engine.md](feature-math-engine.md) |
| F1.3 — AI Opponents | Personality traits, behaviour simulation | [feature-ai-opponents.md](feature-ai-opponents.md) |
| F1.4 — Game Modes | Quick Race, Championship, Training, Duel | [feature-game-modes.md](feature-game-modes.md) |

---

## Design Constraints

- Race simulation runs entirely in the browser. No server round-trips during active gameplay.
- A single authoritative game clock governs all timing.
- Determinism: identical seed + difficulty tier must produce identical race results.
- Incorrect answers slow the runner but never eliminate them from the race.
- Gameplay changes require a documentation update first.

---

## Acceptance Criteria

- [ ] A race of exactly 8 obstacles completes successfully with 1–5 runners.
- [ ] Movement distances match the spec for each speed tier.
- [ ] The same problem seed always generates the same problem sequence.
- [ ] An incorrect answer results in +0 m movement, not a negative distance.
- [ ] All four game modes are reachable from the main menu.
