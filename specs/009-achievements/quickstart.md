# Quickstart: Player Achievements

Integration scenarios for testing the achievements feature end-to-end.

---

## Scenario 1 — First Race Achievement

**Goal**: Verify that completing a first race unlocks `first_race`.

```
1. Register + approve a new player account.
2. POST /api/v1/races with a valid race summary (1 participant, position 1).
3. Assert response.new_achievements contains { key: "first_race" }.
4. GET /api/v1/players/{account_id}/achievements
5. Assert response.achievements contains first_race with a non-null unlocked_at.
```

---

## Scenario 2 — Idempotency (duplicate race submission)

**Goal**: Verify submitting the same race twice does not create duplicate achievements.

```
1. Register + approve a new player account.
2. POST /api/v1/races (race_id = "race-001") → expect 201, new_achievements = [first_race].
3. POST /api/v1/races (race_id = "race-001") → expect 409 (duplicate race).
4. GET /api/v1/players/{account_id}/achievements
5. Assert first_race appears exactly once.
```

---

## Scenario 3 — Hidden Achievement Invisible Until Unlock

**Goal**: Verify a hidden achievement is absent from the catalogue until earned.

```
1. GET /api/v1/achievements → collect all visible keys.
2. Assert no hidden-achievement key appears.
3. Complete the qualifying condition for a hidden achievement.
4. GET /api/v1/achievements?account_id={account_id}
5. Assert the hidden achievement NOW appears (it is unlocked for this account).
6. GET /api/v1/achievements (no account_id)
7. Assert the hidden achievement is still absent from the unauthenticated view.
```

---

## Scenario 4 — Multiple Achievements in One Race

**Goal**: Verify two achievements earned simultaneously are both recorded.

```
1. Register a new player (zero race history).
2. POST /api/v1/races with 8/8 correct answers.
3. Assert response.new_achievements contains both:
   - { key: "first_race" }
   - { key: "perfect_race" }
4. GET /api/v1/players/{account_id}/achievements
5. Assert both keys appear with non-null unlocked_at.
```

---

## Scenario 5 — Level-Up Achievement

**Goal**: Verify reaching level 5 unlocks the level milestone.

```
1. Register a player and award enough XP (via multiple race POSTs) to reach level 5.
2. On the race that triggers the level-up, assert response.new_achievements contains { key: "level_5" }.
3. GET /api/v1/players/{account_id}/achievements → assert level_5 is present.
```

---

## Scenario 6 — Forbidden: viewing another player's achievements

```
1. Register players A and B.
2. GET /api/v1/players/{B.account_id}/achievements  (authenticated as A)
3. Assert HTTP 403.
```

---

## Frontend Smoke Test

```
1. Complete a race that unlocks first_race.
2. On the Results Screen, observe:
   - Sparkle particle effect starts.
   - Badge scales in with bounce easing.
   - Achievement title "Off to the Races!" is visible.
   - Total animation duration ≤ 2 seconds.
3. With prefers-reduced-motion enabled, confirm no animation plays (badge appears immediately).
```
