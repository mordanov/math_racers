# Quickstart: XP & Player Progression

Integration scenarios for testing the feature end-to-end.

---

## Scenario 1: Earn XP on race completion

**Setup**: Authenticated player account, no prior races.

1. `POST /api/v1/races` with `mode=quick`, `problems_correct=7`, `longest_streak=5`:
   - Response 201 includes `progression.xp_earned_this_race = 240` (100 + 140 + 10)
   - `progression.total_xp = 240`, `progression.current_level = 1`
   - `progression.level_up` is null (starting from 0 XP, level was 0, now level 1 — level_up present)
   - Actually: `floor(sqrt(0/100))=0` → `floor(sqrt(240/100))=1`, so level_up fires with `previous_level=0, new_level=1`
2. `GET /api/v1/progression`:
   - Response `total_xp=240`, `current_level=1`, `xp_to_next_level=160`

---

## Scenario 2: Idempotent duplicate submission

1. Submit `POST /api/v1/races` with `race_id=<uuid-A>` — 201, XP awarded.
2. Submit `POST /api/v1/races` again with the same `race_id=<uuid-A>` — 409 `RACE_ALREADY_EXISTS`, no XP change.
3. `GET /api/v1/progression` — `total_xp` unchanged from step 1.

---

## Scenario 3: Championship bonus

1. `POST /api/v1/races` with `mode=championship`, `problems_correct=5`, `longest_streak=0`:
   - `xp_earned_this_race = 100 + 100 + 0 + 500 = 700`

---

## Scenario 4: Level-up detection

1. Player starts with 360 XP (level 1, `xp_to_next_level=40`).
2. `POST /api/v1/races` with `problems_correct=2`, `longest_streak=0`, `mode=quick`:
   - XP delta = 100 + 40 = 140
   - New total = 500 — `floor(sqrt(500/100))=2` → level-up fires
   - Response includes `progression.level_up = { previous_level: 1, new_level: 2, total_xp: 500 }`

---

## Scenario 5: Zero-state read

1. New account, no races submitted.
2. `GET /api/v1/progression`:
   - Response `{ total_xp: 0, current_level: 0, xp_to_next_level: 100 }`

---

## Manual Verification Checklist

From `docs/economy/spec-xp-progression.md`:

- [ ] Complete Quick Race with 7 correct (longest streak = 5): XP = 100+140+10 = 250. Confirm total increases by 250.
- [ ] Verify level formula: if total was 350 before (+250 = 600): `floor(sqrt(600/100))` = 2. Confirm level = 2.
- [ ] Submit same race result again: confirm XP not re-awarded and progression unchanged.
- [ ] Championship race with same stats: XP = 250 + 500 = 750.
- [ ] Open `GET /api/v1/progression`: confirm matches post-race response values.
- [ ] Verify `xp_to_next_level` is never negative for any XP total.
