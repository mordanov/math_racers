# Research: Game Modes

**Branch**: `006-game-modes` | **Date**: 2026-08-10

---

## Decision 1 — API design: combined vs. two-step race lifecycle

**Decision**: Retain the existing combined `POST /api/v1/races` (submit full summary at race end) rather than splitting into "create session" + "submit result" as described in `spec-game-modes.md`.

**Rationale**: Feature 004 (race engine) already implemented and shipped the combined endpoint. The frontend (`raceApi.ts:postRaceSummary`) and the backend (`app/races/`) are designed around a single submission at race completion. The `race_id` is generated client-side (UUID v4) before race start, so the client already has the `race_id` without a round-trip. Splitting into two calls introduces a mandatory network round-trip at race start and a new "pending session" lifecycle the spec's idempotency key already handles for the result side.

**Alignment with spec intent**: The spec's `idempotency_key` requirement maps to the existing `race_id`-as-natural-key on `POST /api/v1/races` (409 on duplicate `race_id`). The spec requirement that "the client retries result submission" is satisfied. The `seed` is also generated client-side (seeded RNG) which is consistent with the current implementation.

**Alternatives considered**:
- Two-step (create session + submit result): rejected because it requires a migration of the existing races endpoint, breaks current frontend, and adds network latency at race start.
- Hybrid (optional session creation): unnecessarily complex.

**Implication for contracts**: The `POST /api/v1/races` contract remains as-is. The game-modes spec API table is treated as intent; the concrete contract follows the existing implementation.

---

## Decision 2 — Championship persistence model

**Decision**: Add `Championship` and `ChampionshipRace` tables via Alembic migration.

**Rationale**: The spec defines `ChampionshipState` with standings that persist across browser sessions — this requires backend-owned storage. A `Championship` table stores series-level state (total races, status). A `ChampionshipRace` junction table links each race result to a championship and stores the finishing position and points awarded in that race. This is the minimal schema that supports standings reconstruction and resumability.

**Alternatives considered**:
- Single `Championship` table with JSON standings column: rejected — violates §XIV (structured data belongs in relational schema; JSON blobs hinder querying and migration).
- Frontend-only state (localStorage): rejected — violates §XIV and §IX (persistent data belongs on backend).

---

## Decision 3 — Training partial result: nullable position

**Decision**: Add a database migration to make `RaceParticipant.position` nullable (NULL = training exit, no finishing position).

**Rationale**: The spec requires `finishing_position: null` for Training exits. The current `RaceParticipant.position` has a `CHECK BETWEEN 1 AND 5` constraint and is non-nullable. A migration removes the constraint and sets the column nullable. The Pydantic schema is updated to `Optional[int]` bounded 1–5. The race engine's `getSummary()` needs a `training` branch that passes `position: null` for the human runner.

**Alternatives considered**:
- Sentinel value (e.g., position = 0): rejected — magic numbers violate §VII.
- Separate `TrainingResult` table: over-engineering; Training sessions share the same participant summary shape.

---

## Decision 4 — Avatar guard

**Decision**: Avatar validation is a frontend responsibility at Race Setup; the backend does not need a new endpoint for this feature.

**Rationale**: No `Avatar` model or `/api/v1/avatars` endpoint exists in the codebase yet. The spec states: "Race Setup screen must validate avatar availability before creating a RaceSession." Since the race session in this codebase is submitted after the race (Decision 1), the guard is: if the player has no configured avatar, disable or redirect the "Start Race" button/screen. The frontend holds the current avatar context. Backend avatar management is a separate feature scope.

**Implication**: The Race Setup UI must check avatar state from context before enabling the race start. If no avatar API exists yet, this guard is a no-op placeholder that can be wired when the avatar feature ships.

---

## Decision 5 — XP calculation

**Decision**: XP is calculated client-side in `raceEngine.ts:getSummary()` using a simple formula and submitted as `xp_earned` per participant; the backend trusts the submitted value.

**Rationale**: The current implementation already submits `xp_earned` per participant (currently hardcoded to 0 in `raceEngine.ts:163`). The spec defines per-position XP (10/6/3/1/0 pts for championship) and implies per-correct-answer XP for training. A formula belongs in the race engine. The backend stores whatever is submitted (no re-calculation server-side), consistent with the existing design.

**Formula** (from spec):
- Championship: 10/6/3/1/0 points by finishing position
- Quick Race / Duel: simple per-correct-answer bonus (to be confirmed against GDD — use placeholder: 10 XP per correct answer)
- Training: per-correct-answer XP, no completion bonus

**Note**: Full XP/progression spec may exist in `docs/economy/`. This plan implements the XP values stated in the game-modes spec; alignment with the economy spec is out of scope for this feature.

---

## Decision 6 — Championship standings calculation

**Decision**: Standings are calculated on-the-fly from `ChampionshipRace` rows rather than stored as a denormalised JSON column.

**Rationale**: With a maximum of 7 races and 5 runners per championship, standing reconstruction is O(35) row reads — negligible. Storing standings as JSON creates update-conflict risk and schema rigidity. The `GET /api/v1/championships/{id}` endpoint aggregates `points`, `podiums`, and `position` from `ChampionshipRace` rows at query time.

---

## Decision 7 — Championship auto-complete

**Decision**: The `PATCH /api/v1/championships/{id}/races/{race_id}` endpoint checks whether all races in the series are complete and transitions `Championship.status` to `completed` atomically within the same database transaction.

**Rationale**: The spec states: "PATCH on the final race result automatically transitions status to completed." This must be atomic to prevent race conditions (two concurrent PATCH calls for the last two races). Implemented as a single transactional update inside the domain service.
