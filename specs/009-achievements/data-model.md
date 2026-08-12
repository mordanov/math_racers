# Data Model: Player Achievements

## Entities

### Achievement (Catalogue Entry — static, not persisted)

Defined in `backend/app/achievements/catalogue.py` as a Python dataclass.

| Field | Type | Constraints |
|-------|------|-------------|
| `key` | `str` | Unique across catalogue; snake_case; never renamed after release |
| `category` | `str` | One of: `racing`, `mathematics`, `streaks`, `collection`, `social`, `milestones`, `exploration`, `special` |
| `title` | `str` | Human-readable display name |
| `description` | `str` | Short explanation of how to earn it |
| `hidden` | `bool` | If `True`, invisible to players until unlocked |
| `icon_path` | `str` | Relative path to static asset (e.g. `assets/achievements/first_race.png`) |

No database table. The catalogue is a versioned Python list; predicates are a registry keyed by `key`.

---

### PlayerAchievement (Unlock Record — persisted)

Database table: `player_achievements`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `UUID` | Primary key, auto-generated |
| `account_id` | `UUID` | FK → `accounts.id` ON DELETE CASCADE, NOT NULL |
| `achievement_key` | `VARCHAR` | NOT NULL; references catalogue key (no FK — catalogue is static) |
| `avatar_id` | `UUID` | Nullable; FK → `avatars.id` ON DELETE SET NULL |
| `unlocked_at` | `TIMESTAMPTZ` | NOT NULL; server default `now()` |

**Unique constraint**: `(account_id, achievement_key)` — enforces idempotency at the database level.

**Indexes**:
- `idx_player_achievements_account_id` on `account_id` — for fast per-player queries
- Unique index implicit from unique constraint

**Invariants**:
- Records are never updated or deleted (except CASCADE on account deletion).
- `avatar_id` is NULL for player-level achievements; non-null only when the achievement is tied to a specific avatar's performance.

---

## Relationships

```
accounts  ──< player_achievements
avatars   ──< player_achievements  (optional)
```

The `achievements` catalogue is not a DB entity and has no FK relationships.

---

## Trigger → Achievement Mapping

| Trigger Event | Achievements Evaluated |
|--------------|----------------------|
| `RaceCompletedEvent` | `first_race`, `podium_finisher`, `champion`, `perfect_race`, race-count milestones |
| `LevelUpEvent` | `level_5`, `level_10`, `level_20` (and further milestones) |
| `AchievementUnlockedEvent` | Meta achievements (e.g. `unlock_10_achievements`) |

_Note_: `ProblemSolvedEvent`, `AvatarCreatedEvent`, `DailyChallengeCompletedEvent` are out of scope for this feature; evaluation stubs can be added later without schema changes.

---

## Predicate Contract

Each predicate is a pure async function:

```python
async def predicate(event: DomainEvent, account_id: UUID, session: AsyncSession) -> bool: ...
```

Predicates MAY query the database (e.g. `COUNT(*)` of past races) but MUST NOT mutate state. A predicate that raises an exception is caught per-achievement; the error is logged and the achievement is skipped.
