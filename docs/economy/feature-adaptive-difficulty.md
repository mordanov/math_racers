# Feature F3.2 — Adaptive Difficulty

**Level:** Feature
**Status:** Authoritative
**Source:** game_economy_specification.md §8–9; GDD Chapter 5
**Parent:** [Epic E3 — Progression](epic.md)

---

## Purpose

Keep the mathematical challenge within each child's zone of proximal development: hard enough to stimulate growth, easy enough to maintain confidence.

---

## Skill Score Formula

```
Skill Score = 0.70 × Accuracy + 0.30 × Speed Score
```

Where:
- `Accuracy = correct_answers / total_answers` (as a decimal 0.0–1.0, scaled ×100 for percent display)
- `Speed Score` = normalised answer speed (0–100); 100 = answers within the "Perfect" threshold, 0 = answers at or beyond the "Slow" threshold.
- Rolling window: **last 50 problems**.

---

## Adjustment Rules

### Increase Difficulty

All conditions must be true simultaneously:
- Accuracy ≥ 90%
- Average response time consistently below the tier target
- At least 50 recent answers have been analysed

### Decrease Difficulty

Either condition triggers a decrease:
- Accuracy < 60%
- Repeated frustration detected (e.g. 3 or more consecutive incorrect answers on the same obstacle)

---

## Hard Constraints

- Difficulty **never** changes during an active race.
- Difficulty changes are **recommendations**, not commands — parents can lock the tier.
- Difficulty never drops below Tier 1 or rises above Tier 6.
- A tier change is logged for the parent dashboard.

---

## Parent Override

Parents may manually set or lock the difficulty tier. A locked tier suppresses all automatic adjustments. The game still records skill scores; adjustments resume when the lock is removed.

---

## Acceptance Criteria

- [ ] Skill score is computed from exactly the last 50 problems.
- [ ] Tier does not increase before 50 problems have been answered.
- [ ] Tier does not change mid-race.
- [ ] Parent-locked tier cannot be overridden by the adaptive system.
- [ ] Tier-change events are written to the statistics log.
