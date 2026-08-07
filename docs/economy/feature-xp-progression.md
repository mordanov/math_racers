# Feature F3.1 — XP & Levels

**Level:** Feature
**Status:** Authoritative
**Source:** game_economy_specification.md §4–6, 13, 16
**Parent:** [Epic E3 — Progression](epic.md)

---

## XP Awards

| Event | XP |
|-------|----|
| Race completed | +100 |
| Correct answer | +20 |
| Perfect answer streak | +10 |
| Daily challenge | +200 |
| Championship completed | +500 |

XP is **never** deducted.

---

## Level Curve

```
XP(level) = 100 × level²
```

| Level | Total XP Required |
|-------|------------------:|
| 1 | 0 |
| 2 | 400 |
| 3 | 900 |
| 5 | 2,500 |
| 10 | 10,000 |
| 20 | 40,000 |

The quadratic curve slows naturally without becoming excessively grindy.

---

## Cosmetic Rewards

Level-ups unlock cosmetic items only:

- medals;
- profile frames;
- celebration animations;
- avatar accessories (hats, shoes, scarves);
- stadium decorations.

**No gameplay advantages are granted.** Learning outcomes never depend on level.

---

## Avatar Statistics

Each avatar independently tracks:

- races;
- wins;
- podium finishes;
- correct answers;
- average response time;
- favourite operation;
- longest streak.

Avatar statistics are cosmetic and motivational; they do not affect race performance.

---

## Daily Streak

One completed race per day extends the streak.

Streak milestones: 3 days, 7 days, 14 days, 30 days, 100 days.

Missing a day resets only the streak counter. No other progress is lost.

---

## Acceptance Criteria

- [ ] Race completion always awards exactly +100 XP.
- [ ] Level-up occurs when cumulative XP crosses `100 × level²`.
- [ ] XP counter never decrements.
- [ ] Level-up triggers a congratulatory animation.
- [ ] No gameplay stat changes on level-up.
