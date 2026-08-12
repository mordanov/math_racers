# Research: XP & Player Progression

**Branch**: `008-xp-progression` | **Date**: 2026-08-11

## Decision 1: Where XP award is triggered

**Decision**: XP award happens inside the existing `POST /api/v1/races` handler — not a separate endpoint.

**Rationale**: The spec (`docs/economy/spec-xp-progression.md`) explicitly states "triggered by `POST /api/v1/races/{id}/results`." The codebase uses `POST /api/v1/races` for race persistence (`races.py`). These are the same route. XP logic is added inside `RaceDomainService.persist_race()` by calling a new `ProgressionDomainService` after the race is saved, within the same transaction.

**Alternatives considered**:
- Separate `POST /api/v1/races/{id}/results` endpoint — rejected because the spec notes the route already exists for race recording and the codebase has one race submission endpoint.
- Async background job — rejected because the spec requires XP to appear in the same request-response cycle (SC-001).

---

## Decision 2: Player identity — account_id as player_id

**Decision**: `player_id` in progression tables maps to `account_id` from the `accounts` table. The spec uses the term "player" but the existing system uses `Account`. There is no separate `Player` entity in the codebase.

**Rationale**: The existing auth system identifies users via `Account.id`. All participant tracking in races and championships uses `account_id` for ownership. Adding a separate `Player` entity would be speculative complexity with no documented requirement.

**Alternatives considered**:
- New `Player` entity — rejected; over-engineering, no ADR supporting it.
- `avatar_id` as player identifier — rejected; `avatar_id` in race participants is a string identifier for the racing character, not the account owner. The player account identity is tracked separately.

---

## Decision 3: XP award is attributed to the account making the request

**Decision**: When `POST /api/v1/races` is called, the authenticated `account.id` owns the progression record updated by that race result. The spec calls this "the player."

**Rationale**: The race endpoint already receives `account: Account = Depends(get_current_account)`. Progression is attributed to the submitting account. This matches the championship pattern where `championship.account_id = account.id`.

---

## Decision 4: Idempotency key = race_id

**Decision**: The `race_id` (UUID) on `RaceSummaryRequest` serves as the idempotency key. If a `Race` with that `id` already exists, `SQLAlchemyRaceRepository.create()` raises `ConflictError`. XP is only awarded if the race was newly inserted.

**Rationale**: The existing repository already checks for duplicate `race_id` and raises `ConflictError` (`RACE_ALREADY_EXISTS`). Hooking into this — awarding XP only when the race insert succeeds — is the natural idempotency mechanism. No separate idempotency key field is needed.

**Alternatives considered**:
- Separate `idempotency_key` field — rejected; the race_id already uniquely identifies a race event and the duplicate check already exists.

---

## Decision 5: Progression module structure

**Decision**: New module `app/progression/` following the exact same module pattern as existing modules (`accounts`, `races`, `championships`): `models.py`, `repository.py`, `domain_service.py`, `schemas.py`, and `presentation/api/v1/progression.py`.

**Rationale**: Constitution §VIII (Consistency) requires matching project structure and naming conventions. All domain modules follow this layout.

---

## Decision 6: LevelUpEvent is not persisted as a separate DB table

**Decision**: `LevelUpEvent` is returned in the API response only, not stored in the database.

**Rationale**: The spec says the event is "consumed by the achievement system and frontend." The achievement system does not yet exist. The frontend receives the event in the race submission response. Persisting it to a DB table now would be speculative (Constitution §VI — Simplicity). The event data can be recomputed from `PlayerProgression` history when needed.

**Alternatives considered**:
- Persist `LevelUpEvent` to a DB table — deferred; implement when the achievement system feature is planned.

---

## Decision 7: correct_answers vs problems_solved validation

**Decision**: The `RaceSummaryRequest` does not currently include a `problems_solved` field. The spec (edge case 5) requires rejecting results where `correct_answers > problems_solved`. Since `problems_correct` maps to `correct_answers` and `problems_solved` is not in the existing schema, this validation cannot be enforced today without a schema change.

**Resolution**: Add an optional `problems_solved` field to `RaceSummaryRequest` with a cross-field validator that enforces `problems_correct ≤ problems_solved` when `problems_solved` is provided. This is backwards-compatible — existing clients that omit the field continue to work.

---

## Decision 8: XP formula inputs

**Decision**: The formula uses `problems_correct` (already in `RaceParticipant`) and `longest_streak` (not currently in the schema). The spec requires `floor(longest_streak / 5) × 10` as a streak bonus.

**Resolution**: Add `longest_streak: int` (≥ 0) to `ParticipantSummaryRequest`. This is a new required field. The streak is recorded on the participant and used for XP calculation. The DB migration adds the column.

---

## Decision 9: No championship bonus from race mode alone

**Decision**: The `mode` field on `RaceSummaryRequest` (already exists, `Literal["quick", "championship", "duel", "training"]`) is used directly to determine the mode bonus: 500 XP for `championship`, 0 otherwise.

**Rationale**: All required data is already present or can be trivially added. No new relationships needed.
