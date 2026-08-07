# Feature F3.3 — Achievements

**Level:** Feature
**Status:** Authoritative
**Source:** GDD Chapter 10 §7–17; game_economy_specification.md §12
**Parent:** [Epic E3 — Progression](epic.md)

---

## Philosophy

Achievements exist to encourage exploration, not to create obligation.

**Good achievement:** "Solve 50 multiplication problems."  
**Bad achievement:** "Play every day for 30 days."

Achievements reward learning — not grinding.

---

## Categories

| Category | Examples |
|----------|---------|
| Racing | First Finish, First Victory, 5 Wins, 20 Wins, 100 Races |
| Mathematics | Addition Expert, Multiplication Master, 100 Correct Answers, Fast Thinker |
| Collection | Create 5 avatars, Read every biography, Choose a favourite |
| Exploration | Play Championship, try every operation, play Duel |
| Persistence | 7-day streak, 30-day streak |
| Improvement | Improve average response time by 10%, 20%, 30% |
| Championships | Win Spring Cup, Finish a championship series |
| Fun | Trip over five hurdles, Race five foxes, Win with the slowest runner |

---

## Hidden Achievements

Some achievements are hidden until unlocked:

- Finish a race with no mistakes
- Create twins (two avatars with identical species)
- Win after trailing at the final obstacle
- Meet every available species

Hidden achievements encourage discovery.

---

## Achievement Presentation

Unlocking an achievement triggers a 2-second interruption:

```
Pause → Sparkles → Badge Appears → Character Celebration → Continue
```

The interruption must last no longer than 2 seconds.

---

## Badge Design

Every achievement is represented by a circular, colourful, instantly recognisable badge following the Art Bible. The badge collection should feel like a sticker album.

---

## Persistence

Achievements are permanent once unlocked. They never expire and cannot be reset.

---

## Acceptance Criteria

- [ ] All category achievements are implemented and visible in the achievements screen.
- [ ] Hidden achievements are not visible until unlocked.
- [ ] Unlocking fires the 2-second presentation animation.
- [ ] An unlocked achievement persists across sessions and devices.
- [ ] Daily-streak achievements never punish missing a day (only reset the streak counter).
