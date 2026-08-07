# Achievements — Implementation Specification

**Level:** Specification
**Status:** Authoritative
**Source:** FR-063; feature-achievements.md; ADR-001; ADR-002
**Parent:** [Epic E3 — Progression](epic.md)
**See also:** [feature-achievements.md](feature-achievements.md), [spec-xp-progression.md](spec-xp-progression.md)

---

## Data Models

### Achievement (Catalogue Entry)

```json
{
  "key": "first_race",
  "category": "racing | mathematics | streaks | collection | social | milestones | exploration | special",
  "title": "Off to the Races!",
  "description": "Complete your first race.",
  "hidden": false,
  "icon_path": "assets/achievements/first_race.png"
}
```

The catalogue is static and version-controlled. New achievements are added via a catalogue update; existing achievements are never removed or renamed after release.

### PlayerAchievement (Unlock Record)

```json
{
  "id": "uuid",
  "player_id": "uuid",
  "avatar_id": "uuid | null",
  "achievement_key": "first_race",
  "unlocked_at": "ISO8601"
}
```

`avatar_id` is set when the achievement is tied to a specific avatar's performance (e.g., "Win 10 races with the same avatar"). It is `null` for player-level achievements.

Once created, `PlayerAchievement` records are never updated or deleted (FR-063: achievements are permanent).

---

## Achievement Trigger Table

| Domain Event | Achievements Evaluated |
|-------------|----------------------|
| `RaceCompletedEvent` | first_race, podium_finisher, champion, race_count milestones |
| `ProblemSolvedEvent` | correct_streak milestones, first_perfect_race |
| `LevelUpEvent` | level milestones (5, 10, 20, …) |
| `AvatarCreatedEvent` | first_avatar, avatar_count milestones |
| `DailyChallengeCompletedEvent` | daily_streak milestones |
| `AchievementUnlockedEvent` | meta achievements (unlock N achievements) |

---

## Evaluation Pseudocode

```
on domain event received:
  triggered_keys = AchievementTriggerTable[event.type]

  for key in triggered_keys:
    if alreadyUnlocked(player_id, key):
      continue

    if evaluatePredicate(key, event, player_id):
      unlock(player_id, key, avatar_id=event.avatar_id)


function unlock(player_id, key, avatar_id):
  record = PlayerAchievement(player_id, key, avatar_id, now())
  INSERT record
  emit AchievementUnlockedEvent(player_id, key, avatar_id)
```

Evaluation and unlock happen within the same database transaction as the triggering event handler. `AchievementUnlockedEvent` is published after the transaction commits.

---

## Predicate Examples

```python
# first_race: player has completed at least 1 race
predicates["first_race"] = lambda event, player_id: (
    event.type == "RaceCompletedEvent"
    and get_race_count(player_id) >= 1
)

# perfect_race: completed a race with 8/8 correct answers
predicates["perfect_race"] = lambda event, player_id: (
    event.type == "RaceCompletedEvent"
    and event.correct_answers == event.problems_solved == 8
)

# level_5: player reached level 5
predicates["level_5"] = lambda event, player_id: (
    event.type == "LevelUpEvent"
    and event.new_level >= 5
)
```

Predicates are pure functions. They query the database for aggregate counts as needed but never mutate state.

---

## Presentation Flow (Frontend)

When `AchievementUnlockedEvent` is received by the frontend:

```
If race is active:
  Queue notification → defer until Results Screen

On Results Screen (or immediately if not in race):
  1. Sparkle particle effect (0.3 s)
  2. Badge scales in with bounce easing (0.5 s)
  3. Ascending chime notes play
  4. Short fanfare (0.4 s)
  5. Achievement title + description visible for 1.5 s minimum
  Total: < 2 seconds
```

Multiple achievements unlocked in the same event cycle are presented sequentially, 2 seconds apart.

---

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/v1/achievements` | Return full achievement catalogue |
| `GET` | `/api/v1/players/{id}/achievements` | Return all unlocked achievements for a player |

The unlock endpoint is internal — achievements are unlocked by domain event handlers, never by direct API call.

---

## Edge Cases

1. **Two achievements trigger simultaneously** — both are evaluated and unlocked within the same transaction. Both `AchievementUnlockedEvent`s are emitted; the frontend queues and presents them sequentially.
2. **Hidden achievement revealed prematurely** — `hidden: true` achievements must not appear in the catalogue API response or the player's locked achievement list. They appear only after unlock. The frontend must not attempt to display their title or icon before unlock.
3. **Achievement unlocked while race is active** — the frontend defers the presentation animation until the Results Screen. The unlock record is persisted immediately in the backend regardless.
4. **Duplicate domain event delivery** — `alreadyUnlocked` check is idempotent. If the same event is processed twice, the second pass skips all already-unlocked achievements without error.
5. **Achievement predicate throws** — catch the exception per achievement; log it; do not prevent other achievements from evaluating. Never surface the error to the player.
6. **Player deleted** — cascade delete `PlayerAchievement` records. The catalogue entries remain.

---

## Manual Verification Steps

1. Create a fresh player account. Complete the first race. Confirm "Off to the Races!" achievement triggers, the badge animation plays on the Results Screen, and the achievement appears in `GET /api/v1/players/{id}/achievements`.
2. Complete a race with 8/8 correct answers. Confirm the "Perfect Race" achievement unlocks.
3. Reach level 5. Confirm a level-based achievement unlocks on the Results Screen.
4. Trigger two achievements in a single race (e.g., "First Race" and "Perfect Race" simultaneously on a new account). Confirm both present sequentially on the Results Screen without overlap.
5. Start a race. During the race, satisfy an achievement condition (e.g., correct streak). Confirm the achievement badge does not appear during the race but does appear on the Results Screen.
6. Call `GET /api/v1/players/{id}/achievements` and verify it returns only unlocked achievements. Confirm hidden achievements are absent from the locked catalogue.
7. Submit the same race result twice (idempotency test). Confirm no duplicate achievements are created.

---

## Acceptance Criteria

- [ ] Achievements are permanent once unlocked (never deleted or reset).
- [ ] Hidden achievements are not visible until unlocked.
- [ ] Achievement evaluation is triggered by domain events, not direct API calls.
- [ ] Two simultaneous unlocks are presented sequentially with no overlap.
- [ ] Achievement presentation during an active race is deferred to Results Screen.
- [ ] Duplicate event delivery never creates duplicate unlock records.
- [ ] Achievement animation total duration is < 2 seconds.
