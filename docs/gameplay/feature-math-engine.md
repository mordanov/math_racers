# Feature F1.2 — Mathematics Engine

**Level:** Feature
**Status:** Authoritative
**Source:** GDD Chapter 5; game_economy_specification.md §7–9
**Parent:** [Epic E1 — Gameplay](epic.md)

---

## Purpose

The Mathematics Engine generates arithmetic problems, validates answers, and manages adaptive difficulty. It is the core educational subsystem of the game.

---

## Supported Operations

| Symbol | Operation |
|--------|-----------|
| + | Addition |
| − | Subtraction |
| × | Multiplication |
| ÷ | Division |

---

## Difficulty Tiers

| Tier | Operations | Description |
|------|------------|-------------|
| 1 | Addition | Single operation, small numbers |
| 2 | Addition + Subtraction | Two operations mixed |
| 3 | Multiplication | Times tables |
| 4 | Division | Division with whole-number results |
| 5 | Mixed Operations | All four operations |
| 6 | Custom Sets | Parent-defined operation set |

Parents or players may manually select a tier. Adaptive difficulty may recommend a change but never force one.

---

## Problem Generation Rules

- Problems are generated deterministically from a seed.
- No two consecutive problems are identical.
- Numbers stay within the appropriate range for the selected tier.
- Division problems always produce whole-number results.
- Problems are age-appropriate (no negatives at low tiers, no remainders).

---

## Answer Validation

- Answer validation is instantaneous from the player's perspective.
- Validation occurs client-side using exact integer comparison.
- No partial credit.

---

## Adaptive Difficulty

```
Skill Score = 0.70 × Accuracy + 0.30 × Speed Score
```

Where:
- `Accuracy = correct_answers / total_answers`
- `Speed Score = normalised answer speed (0–100)` — 100 meaning perfectly within time target.
- Rolling window: last **50 problems**.

**Increase difficulty if:**
- Accuracy ≥ 90%
- Average response time is consistently below the tier target
- At least 50 recent answers have been analysed

**Decrease difficulty if:**
- Accuracy < 60%
- Repeated frustration detected (e.g. 3 consecutive incorrect answers at same obstacle)

**Never change difficulty during an active race.**

---

## Acceptance Criteria

- [ ] All four operations generate valid problems at each tier.
- [ ] Problem generation produces the same sequence given the same seed.
- [ ] No two consecutive identical problems appear.
- [ ] Division results are always whole numbers.
- [ ] Difficulty upgrade only fires after ≥ 50 analysed answers with accuracy ≥ 90%.
- [ ] Difficulty downgrade fires when accuracy drops below 60%.
- [ ] Difficulty never changes mid-race.
