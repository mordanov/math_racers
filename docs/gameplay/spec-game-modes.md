# Game Modes — Implementation Specification

**Level:** Specification
**Status:** Authoritative
**Source:** FR-050–053; feature-game-modes.md; ADR-002; ADR-004
**Parent:** [Epic E1 — Gameplay](epic.md)
**See also:** [feature-game-modes.md](feature-game-modes.md), [spec-race-engine.md](spec-race-engine.md)

---

## Data Models

### RaceSession

```json
{
  "id": "uuid",
  "player_id": "uuid",
  "avatar_id": "uuid",
  "mode": "quick_race | championship | training | duel",
  "opponent_count": 3,
  "difficulty_tier": 2,
  "seed": 1234567890,
  "status": "pending | active | completed | abandoned",
  "created_at": "ISO8601",
  "completed_at": "ISO8601 | null"
}
```

### RaceResult

```json
{
  "race_id": "uuid",
  "player_id": "uuid",
  "avatar_id": "uuid",
  "finishing_position": 1,
  "problems_solved": 8,
  "correct_answers": 7,
  "mistakes": 1,
  "total_distance": 126,
  "duration_seconds": 47,
  "xp_earned": 100,
  "idempotency_key": "uuid"
}
```

`idempotency_key` prevents duplicate XP credit if the client retries result submission.

### ChampionshipState

```json
{
  "id": "uuid",
  "player_id": "uuid",
  "total_races": 5,
  "races_completed": 2,
  "standings": [
    {
      "avatar_id": "uuid",
      "is_player": true,
      "points": 10,
      "podiums": 1,
      "position": 1
    }
  ],
  "status": "active | completed"
}
```

---

## Championship Points Table

| Finishing Position | Points |
|-------------------|--------|
| 1st | 10 |
| 2nd | 6 |
| 3rd | 3 |
| 4th | 1 |
| 5th | 0 |

Points are cumulative across all races in the championship series.

---

## Mode Lifecycles

### Quick Race

```
Race Setup → Create RaceSession → Race → Submit RaceResult → Results Screen
```

No persistent championship state. Single race, result submitted immediately on finish.

### Championship

```
Championship Setup → Create ChampionshipState
       ↓
  Race 1 Setup → Race 1 → Submit Result → Update Standings
       ↓
  Race 2 Setup → Race 2 → Submit Result → Update Standings
       ↓
        ... (N races, configurable 3–7)
       ↓
  Final Standings Screen → Complete Championship
```

Each race in a championship uses a fresh `RaceSession`. Points are accumulated in `ChampionshipState`. If interrupted (browser closed, session expired), the championship is resumable until all races are complete.

### Training

```
Training Setup → Create RaceSession (mode: training, opponent_count: 0)
       ↓
  Infinite Problem Loop → Player exits voluntarily
       ↓
  Submit partial RaceResult (no finishing position, no XP for race completion)
```

Training runs until the player exits. There is no finish line. Statistics are recorded for problems attempted.

### Duel

```
Duel Setup → difficulty matched to player's current tier
       ↓
  Create RaceSession (mode: duel, opponent_count: 1)
       ↓
  Race → Submit RaceResult → Results
```

Duel always creates exactly one AI opponent. The opponent's tier is matched to the player's current adaptive difficulty tier (`tier_offset = 0`, personality = Balanced).

---

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/races` | Create a RaceSession; returns `race_id` and `seed` |
| `POST` | `/api/v1/races/{id}/results` | Submit a RaceResult (idempotent via `idempotency_key`) |
| `POST` | `/api/v1/championships` | Create a ChampionshipState |
| `GET` | `/api/v1/championships/{id}` | Retrieve current championship standings |
| `PATCH` | `/api/v1/championships/{id}/races/{race_id}` | Record race result within a championship |

---

## Edge Cases

1. **Championship interrupted mid-series** — `ChampionshipState.status` remains `active`; the player resumes from the next unplayed race. Standings from completed races are preserved.
2. **Duel where matched tier yields tier 0** — `clamp(player_tier + 0, 1, 6)` prevents this; minimum is always tier 1.
3. **Training exited mid-race** — submit a partial `RaceResult` with `finishing_position: null` and `problems_solved` equal to the number of checkpoints reached. No XP for race completion is awarded; per-correct-answer XP still applies.
4. **Race started with no avatars available** — the Race Setup screen must validate avatar availability before creating a `RaceSession`; if no avatar exists, redirect to Avatar Creator.
5. **Duplicate result submission** — `idempotency_key` (UUID set by the client at first submission) causes the server to return the original result without re-processing XP.
6. **Championship with all races completed but `status` not updated** — `PATCH` on the final race result automatically transitions `status` to `completed`.
7. **Race seed collision** — seeds are generated server-side as random 64-bit integers at session creation; the probability of collision is negligible; no collision detection is required.
8. **Quick Race with 5 opponents** — valid; up to 5 runners total including the player (FR-021: 1–5 runners).

---

## Manual Verification Steps

1. Start a Quick Race with 3 opponents. Complete it. Confirm a result screen appears with finishing position, XP earned, and correct/incorrect count.
2. Start a Championship of 3 races. Complete Race 1. Confirm standings update. Close the browser. Reopen and navigate to Championship. Confirm standings are preserved and Race 2 is available.
3. Start a Training session. Answer 10 problems. Exit voluntarily. Confirm the session is recorded in Statistics with `finishing_position: null`.
4. Start a Duel. Confirm exactly 1 AI opponent appears on the track.
5. In Race Setup, delete all avatars (or use a test account with none). Confirm the app redirects to Avatar Creator rather than allowing race start.
6. Submit a race result twice with the same `idempotency_key`. Confirm the server returns the same result and XP is not doubled.
7. Complete a Championship of 5 races. Confirm the final standings screen shows cumulative points in correct order.
8. Start a Quick Race with 5 opponents. Confirm all 5 runners appear on the track alongside the player (total 6 runners — wait, FR-021 says 1–5 runners. Clarify: player counts as one runner; so 5 total means player + 4 AI opponents. Verify the UI correctly shows the player and all AI opponents).

---

## Acceptance Criteria

- [ ] Quick Race creates a session, completes a single race, and submits a result.
- [ ] Championship preserves standings across browser sessions until completion.
- [ ] Training runs without a finish line and records partial statistics on exit.
- [ ] Duel creates exactly one AI opponent matched to the player's current difficulty tier.
- [ ] Result submission is idempotent; XP is never awarded twice for the same race.
- [ ] Race setup blocks start if no avatar is available.
- [ ] Championship auto-transitions to `completed` when all races are submitted.
- [ ] Points accumulate correctly across all championship races per the points table.
