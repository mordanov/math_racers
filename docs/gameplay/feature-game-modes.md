# Feature F1.4 — Game Modes

**Level:** Feature
**Status:** Authoritative
**Source:** GDD Chapter 8
**Parent:** [Epic E1 — Gameplay](epic.md)

---

## Overview

Four modes are available in v1.0, each serving a different educational and engagement purpose.

---

## Quick Race

**Purpose:** Flexible pick-up-and-play session.

- Player selects: operation(s), difficulty tier, number of AI opponents (1–4).
- Single race of 8 obstacles.
- Awards full XP.
- Fastest mode to reach gameplay.

**Flow:** Main Menu → Mode Select → Quick Race Setup → Race → Results → Play Again / Menu

---

## Championship

**Purpose:** Multi-race tournament with cumulative scoring.

- A championship consists of a series of races (e.g. 3–5 races).
- Each race awards points based on finishing position.
- Cumulative standings shown between races.
- Final ceremony on championship completion.

**Scoring example:**

| Position | Points |
|----------|--------|
| 1st | 10 |
| 2nd | 7 |
| 3rd | 5 |
| 4th | 3 |
| 5th | 1 |

**Flow:** Championship Select → Race 1 → Standings → Race 2 → … → Championship Ceremony

---

## Training

**Purpose:** Solo practice with no time pressure.

- No AI opponents.
- No timer.
- Player answers problems at their own pace.
- No XP awarded (to avoid grinding incentive).
- Adaptive difficulty still active.
- Ideal for parents setting focused practice.

**Flow:** Mode Select → Training Setup (operation, tier) → Race → Summary

---

## Duel

**Purpose:** Player vs one AI opponent at matched difficulty.

- Single AI opponent of Balanced personality.
- AI calibrated to player's current skill score.
- Closest race format; designed for direct competition.
- Awards full XP.

**Flow:** Mode Select → Duel → Race → Results

---

## Acceptance Criteria

- [ ] All four modes are reachable from the main menu in ≤ 3 taps.
- [ ] Championship correctly accumulates points across all races in the series.
- [ ] Training mode never awards XP.
- [ ] Duel always spawns exactly one AI opponent with Balanced personality.
- [ ] Mode selection screen clearly describes each mode.
