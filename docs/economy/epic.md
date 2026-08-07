# Epic E3 — Progression & Economy

**Level:** Epic
**Status:** Authoritative
**Source:** GDD Chapter 10; game_economy_specification.md
**Parent:** [PRD](../prd.md)

---

## Summary

Deliver a mastery-based progression system that rewards learning rather than grinding. XP, levels, achievements, and statistics celebrate effort and improvement; adaptive difficulty keeps challenges within each child's zone of proximal development.

---

## Features

| Feature | Description | Link |
|---------|-------------|------|
| F3.1 — XP & Levels | Earning XP, level curve, cosmetic rewards | [feature-xp-progression.md](feature-xp-progression.md) |
| F3.2 — Adaptive Difficulty | Skill score formula, adjustment rules | [feature-adaptive-difficulty.md](feature-adaptive-difficulty.md) |
| F3.3 — Achievements | Categories, unlocking, presentation | [feature-achievements.md](feature-achievements.md) |
| F3.4 — Statistics | Player, avatar, and session statistics | [feature-statistics.md](feature-statistics.md) |

---

## Design Constraints

- XP is never deducted.
- Difficulty never changes during an active race.
- No pay-to-win: all progression is cosmetic.
- No global leaderboards in v1.0.
- Players can never lose achievements or history.
- Progress data belongs to the player; parents can export or delete it.

---

## Acceptance Criteria

- [ ] Completing a race awards exactly +100 XP.
- [ ] Level curve follows `XP(level) = 100 × level²`.
- [ ] Difficulty increases only after ≥50 analysed answers with accuracy ≥ 90%.
- [ ] Difficulty decreases when accuracy < 60%.
- [ ] Achievements persist permanently after unlocking.
- [ ] Parent dashboard shows weekly accuracy, average time, strongest/weakest operation.
