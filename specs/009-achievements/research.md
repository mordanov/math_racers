# Research: Player Achievements

**Date**: 2026-08-12

---

## 1. Catalogue Storage Strategy

**Decision**: Static Python module (`catalogue.py`) — a plain list of dataclass instances, not a database table.

**Rationale**: The spec states the catalogue is "static and version-controlled" and entries are "never removed or renamed after release." A DB table adds a migration and seed step with no gain; a Python module is versioned via git, immediately consistent across all replicas, zero-latency to read, and trivially testable.

**Alternatives considered**:
- DB table with migration seed: adds complexity, no benefit for a read-only corpus.
- JSON/YAML file on disk: works but loses type-safety and is harder to import in tests.

---

## 2. Unlock Record Idempotency

**Decision**: Unique constraint on `(account_id, achievement_key)` in `player_achievements`. Application layer also checks `alreadyUnlocked` before inserting; DB constraint is the safety net for concurrent delivery.

**Rationale**: The spec requires "duplicate event delivery never creates duplicate unlock records." A `INSERT ... ON CONFLICT DO NOTHING` pattern (PostgreSQL UPSERT) makes the write atomic and idempotent with a single query, avoiding a SELECT + INSERT race.

**Alternatives considered**:
- Application-level SELECT + INSERT: susceptible to race conditions under concurrent delivery.
- Separate deduplication table: unnecessary complexity.

---

## 3. Achievement Evaluation Integration Point

**Decision**: Call `AchievementDomainService.evaluate_race_completed()` from `RaceDomainService.persist_race()`, immediately after XP is awarded. A `LevelUpEvent` is returned by the progression service; if it is non-null, also call `evaluate_level_up()`.

**Rationale**: Domain events in this codebase are synchronous Python calls (there is no message bus yet). The spec says evaluation and unlock happen within the same transaction as the triggering handler. Calling from `persist_race` is the natural extension of the existing pattern where XP is also awarded there.

**Alternatives considered**:
- Dedicated event bus / Celery tasks: over-engineered; the spec says same-transaction, and the codebase has no async event infrastructure.
- Hooks in the presentation layer: violates the constitution (business logic not in controllers).

---

## 4. Hidden Achievement Filtering

**Decision**: `GET /api/v1/achievements` filters `hidden=True` entries from the response for any player who hasn't unlocked them. The endpoint accepts an optional `account_id` query parameter to enable per-player filtering; unauthenticated callers receive only non-hidden entries.

**Rationale**: The spec is unambiguous: hidden achievements must not appear in catalogue or locked lists before unlock. The simplest approach is a server-side filter — the catalogue is small enough that no DB join is needed; the domain service can diff the full catalogue against the player's unlock list.

**Alternatives considered**:
- Client-side filtering: trust violation — hidden entries would exist in the API response.
- Separate hidden/visible endpoints: unnecessary split; a query param is cleaner.

---

## 5. Frontend Celebration Timing

**Decision**: The race engine already has a `RaceState` type (`IDLE | LOBBY | COUNTDOWN | RACING | FINISHING | RESULTS`). The `AchievementToast` component is only rendered when `state === 'RESULTS'`. New achievements are fetched (or returned in the POST /api/v1/races response body) and queued; the queue drains one at a time with a 2-second gap between items.

**Rationale**: No new state machine is needed — gating on the existing `RESULTS` state is sufficient. A simple queue (array + timeout) is the minimal implementation. `prefers-reduced-motion` is respected per the constitution accessibility gate.

**Alternatives considered**:
- WebSocket push: over-engineered; the frontend already polls/fetches after race completion.
- New race state `ACHIEVEMENT_CEREMONY`: unnecessary complexity; the Results Screen already exists.

---

## 6. Avatar-Specific Achievements

**Decision**: `player_achievements.avatar_id` is nullable UUID. For the initial catalogue, avatar-specific achievements (e.g. "win 10 races with the same avatar") are defined but their predicates require querying race history filtered by avatar — deferred to a future milestone. For now, predicates that need avatar context can be marked `not_yet_evaluable` and skipped without error.

**Rationale**: The spec includes `avatar_id` in the data model. Implementing the full predicate for avatar-specific milestones requires race-history aggregation that is out of scope for this feature. Designing the schema to support it from day one avoids a future migration.

**Alternatives considered**:
- Omit `avatar_id` column: requires a future schema migration to add it.
- Implement avatar predicates now: out of scope; added complexity for the initial release.

---

## 7. Achievement Response in POST /api/v1/races

**Decision**: Include a `new_achievements: list[AchievementResponse]` field in `RaceSummaryResponse` (alongside the existing `progression` field). This avoids a separate GET request from the frontend immediately after race completion.

**Rationale**: The frontend needs to know which achievements were just unlocked to drive the celebration queue. Returning them in the race POST response is the lowest-latency approach and follows the existing `progression` field pattern.

**Alternatives considered**:
- Separate `GET /api/v1/players/{id}/achievements?since=<race_completed_at>`: requires a second round-trip; timing-sensitive.
- WebSocket notification: infrastructure overhead not warranted.
