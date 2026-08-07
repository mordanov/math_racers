# Feature F1.3 — AI Opponents

**Level:** Feature
**Status:** Authoritative
**Source:** GDD Chapter 7
**Parent:** [Epic E1 — Gameplay](epic.md)

---

## Purpose

AI opponents simulate a variety of racing personalities that create a compelling, fair, and educational race experience without requiring real-time multiplayer infrastructure.

---

## Design Principle

AI opponents are not cheating algorithms. They simulate plausible racers whose behaviour is governed by their personality and by the player's current difficulty tier.

---

## AI Personalities

| Personality | Behaviour |
|-------------|-----------|
| Steady | Consistent performance; small variance; reliable pace |
| Speedster | Fast early, slower later; front-loaded acceleration |
| Slow Starter | Builds speed over the race; strong at later obstacles |
| Unpredictable | High variance; occasionally very fast or very slow |
| Balanced | Average across all metrics; mirrors the expected player skill |

Each AI runner is assigned one personality on race creation.

---

## Performance Simulation

AI performance is computed from:

1. **Base speed** — set by difficulty tier (scales with the player's current tier).
2. **Personality modifier** — varies response time and accuracy according to the personality table.
3. **Noise** — small random variation per obstacle to prevent robotic uniformity.

AI opponents never have access to the player's answers or exact timing.

---

## Difficulty Calibration

AI opponents are calibrated so that:

- At tier 1 (easiest), a new player can win their first race.
- At tier 5/6 (hardest), even skilled players face a genuine challenge.
- The gap between AI and player shrinks gradually as the player improves.

---

## Avatar Assignment

Each AI opponent is displayed using a randomly selected avatar from the system's character library. AI avatars follow the same Art Bible rules as player avatars.

---

## Acceptance Criteria

- [ ] Each personality produces statistically different race outcomes over 10+ races.
- [ ] AI calibration allows a beginner to finish in the top 3 on tier 1 within the first 3 races.
- [ ] AI opponents never exhibit identical movements to each other on the same obstacle.
- [ ] AI movement is deterministic given the same seed and personality.
