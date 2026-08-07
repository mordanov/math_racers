# Feature F3.4 — Statistics

**Level:** Feature
**Status:** Authoritative
**Source:** GDD Chapter 10 §18–25; game_economy_specification.md §14
**Parent:** [Epic E3 — Progression](epic.md)

---

## Purpose

Statistics provide three different audiences with motivating, meaningful feedback:

| Audience | What they see |
|----------|---------------|
| Child | Charts, stars, progress bars, personal bests — never raw numbers |
| Parent | Weekly/monthly summaries, accuracy trends, strongest/weakest operation |
| Admin (future) | Aggregate metrics, retention, difficulty distribution |

---

## Player Statistics

Track per player account:

- XP and current level
- Total races
- Total correct answers
- Average response time
- Favourite operation (most played)
- Strongest operation (highest accuracy)
- Weakest operation (lowest accuracy)
- Longest session streak
- Total learning time

These statistics are private to the player and their parent.

---

## Avatar Statistics

Track per avatar:

- Races
- Wins
- Podium finishes (1st/2nd/3rd)
- Average placement
- Total distance run
- Best answer streak

---

## Session Statistics

Track per session:

- Session duration
- Problems solved
- Mistakes
- Difficulty tier used
- Personal records broken
- Achievements unlocked

---

## Parent Dashboard Data

Weekly summary:

- Problems solved
- Accuracy (%)
- Average response time
- Strongest operation
- Weakest operation (labelled as "Needs Practice")

Display principle: show improvement over time, not only absolute numbers.

---

## Child-Facing Display

Children see:

- Colourful progress bars
- Medal/star counts
- "You're 18% faster than last month!" — not "Average: 3.28 s"

Complex analytics remain hidden from children.

---

## Personal Records

Records tracked:

- Fastest correct answer
- Highest accuracy in one race
- Longest winning streak
- Fastest championship victory
- Most races completed in one session

Breaking a personal record triggers a special congratulatory animation.

---

## History & Timeline

- Historical data is retained permanently and versioned for future schema evolution.
- Improvement timeline shows weekly, monthly, and yearly trends.
- Favourite avatar timeline records every favourite-change event.
- Championship history is permanently visible.

---

## Privacy

- All progression data belongs to the player.
- Parents may review, export, or delete all data.
- No educational analytics are shared publicly.
- No global rankings in v1.0.

---

## Acceptance Criteria

- [ ] Player statistics update after every race.
- [ ] Parent dashboard shows accurate weekly summary.
- [ ] Personal record broken event triggers the celebration animation.
- [ ] Data export produces a downloadable file with complete history.
- [ ] Data deletion removes all records for the selected child profile.
- [ ] No statistics are publicly visible.
