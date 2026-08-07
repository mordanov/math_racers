# Math Racers — Game Economy & Progression Specification

**Version:** 1.0

---

# 1. Purpose

This document defines the progression model of **Math Racers**.

Unlike traditional games, the primary reward is **learning**, not collecting currency.

The progression system exists to:

- encourage regular practice;
- maintain motivation;
- personalise challenge;
- reward improvement rather than perfection.

---

# 2. Design Principles

The progression system should always be:

- positive;
- transparent;
- deterministic;
- skill-based;
- non-punitive.

Players should never lose progress.

---

# 3. Core Progression Loop

```
Solve Problems
        ↓
Finish Race
        ↓
Earn XP
        ↓
Unlock Levels
        ↓
Unlock Cosmetics
        ↓
Race Again
```

---

# 4. Player Experience (XP)

XP rewards participation more than winning.

```
Race Completed            +100 XP
Correct Answer            +20 XP
Perfect Answer Streak     +10 XP
Daily Challenge           +200 XP
Championship Completed    +500 XP
```

XP is never deducted.

---

# 5. Level Curve

Use a quadratic progression.

```
XP(level) = 100 × level²
```

Examples:

| Level | Total XP |
|--------|---------:|
| 1 | 0 |
| 2 | 400 |
| 3 | 900 |
| 5 | 2,500 |
| 10 | 10,000 |
| 20 | 40,000 |

The curve slows naturally without becoming excessively grindy.

---

# 6. Avatar Progression

Each avatar maintains independent statistics.

Track:

- races;
- wins;
- podium finishes;
- correct answers;
- average response time;
- favourite operation;
- longest streak.

No gameplay advantages are granted.

Progression is cosmetic only.

---

# 7. Difficulty Levels

Mathematics is organised into tiers.

| Tier | Operations |
|------|------------|
| 1 | Addition |
| 2 | Addition + Subtraction |
| 3 | Multiplication |
| 4 | Division |
| 5 | Mixed Operations |
| 6 | Custom Sets |

Parents or players may manually select a tier.

Adaptive difficulty may recommend—but never force—a change.

---

# 8. Adaptive Difficulty

The game estimates player skill using recent performance.

Inputs:

- accuracy;
- response time;
- consecutive mistakes;
- recent improvement.

Suggested formula:

```
Skill Score =
0.70 × Accuracy
+
0.30 × Speed Score
```

Where:

```
Accuracy = correct / total

Speed Score = normalised answer speed (0–100)
```

Use the last **50 problems** as a rolling window.

---

# 9. Difficulty Adjustment Rules

Increase difficulty if:

- accuracy ≥ 90%;
- average response time is consistently below the target;
- at least 50 recent answers analysed.

Decrease difficulty if:

- accuracy < 60%;
- repeated frustration is detected.

Never change difficulty during an active race.

---

# 10. Race Scoring

Each obstacle awards a movement score.

Suggested formula:

```
Movement =
Base Distance
× Accuracy Modifier
× Speed Modifier
```

Example modifiers:

Accuracy

Correct → 1.0

Incorrect → 0.3

Speed

Fast → 1.2

Normal → 1.0

Slow → 0.8

This rewards both correctness and fluency while ensuring that mistakes still allow progress.

---

# 11. Daily Streak

One completed race per day extends the streak.

Milestones:

- 3 days
- 7 days
- 14 days
- 30 days
- 100 days

Missing a day resets only the streak counter.

No other progress is lost.

---

# 12. Achievements

Achievements are permanent.

Suggested categories:

### Learning

- First Correct Answer
- 100 Correct Answers
- 1,000 Correct Answers
- Perfect Race

### Racing

- First Victory
- 10 Wins
- 100 Races

### Consistency

- 7-Day Streak
- 30-Day Streak
- 365-Day Streak

### Collection

- First Avatar
- Five Avatars
- Favourite Champion

Achievements never expire.

---

# 13. Reward Philosophy

Rewards should be cosmetic.

Examples:

- medals;
- badges;
- avatar accessories;
- celebration animations;
- profile frames;
- stadium decorations.

Never unlock stronger runners or gameplay bonuses.

Learning outcomes should never depend on purchases or grinding.

---

# 14. Statistics

Track:

Player

- XP;
- level;
- races;
- accuracy;
- average response time;
- favourite operation.

Avatar

- races;
- wins;
- podiums;
- average placement;
- total distance;
- best streak.

Session

- duration;
- solved problems;
- mistakes;
- difficulty tier.

Statistics are used for motivation, not comparison.

---

# 15. Leaderboards

Version 1.0 intentionally excludes global leaderboards.

Future versions may support:

- family leaderboards;
- classroom leaderboards;
- private friend groups.

Public worldwide rankings are avoided to reduce unhealthy competition.

---

# 16. Progression Curve

The ideal learning curve follows:

```
Easy Success
      ↓
Small Challenge
      ↓
Mastery
      ↓
Slight Increase
      ↓
Repeat
```

Difficulty should grow gradually rather than in large steps.

---

# 17. Session Length

Recommended race duration:

**2–5 minutes**

Recommended daily play:

**10–15 minutes**

The game should encourage stopping after a successful session rather than promoting endless play.

---

# 18. Success Metrics

The progression system is successful if:

- players maintain an accuracy of **75–90%**;
- average sessions last **10–15 minutes**;
- adaptive difficulty changes are rarely noticed;
- players continue returning through intrinsic motivation rather than grinding;
- cosmetic rewards reinforce achievement without affecting gameplay.

---

# Summary

Math Racers uses a **mastery-based progression system** centred on learning rather than accumulation.

XP, levels, achievements and cosmetics celebrate effort and improvement, while adaptive difficulty keeps mathematical challenges within each child's "zone of proximal development."

The result is a progression model that remains motivating, fair, deterministic and educational, supporting long-term engagement without introducing pay-to-win mechanics or unnecessary complexity.
