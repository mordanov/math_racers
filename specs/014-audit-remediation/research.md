# Research: Audit Remediation

## Decisions

### Follow the source-document hierarchy

**Decision**: Apply the Constitution order. Apply approved choices and update
the source and derived documents before code.

**Rationale**: `docs/README.md` identifies the original documents as
authoritative. The Constitution gives the order of precedence.

**Alternatives considered**: Treat the latest derived specification as the
source of truth. Rejected because it can contradict a higher-priority source.

### Championship scoring

**Decision**: Use 10, 8, 6, 4, 2 for first through fifth place.

**Rationale**: The user approved these values. They match the GDD example table.
Replace the GDD note that says the values may change with the approved rule.

### Level baseline

**Decision**: Level 1 begins at 0 XP; Level 2 begins at 400 XP. Calculate the
level as `max(1, floor(sqrt(total_xp / 100)))`.

**Rationale**: The user selected the zero-XP Level 1 rule. The `max(1, ...)`
baseline resolves the source formula's Level 0 result.

### Child ownership migration

**Decision**: Keep legacy records unassigned until a parent selects a child
owner. Do not infer or split ownership.

**Rationale**: The user approved parent assignment. The database must preserve
all rows and prevent child access before assignment.

### Training, tier, XP, challenge, and image rules

**Decision**: Training has unlimited problems and no time pressure or opponents.
Correct answers earn +20 XP; Training has no race-completion XP. Tier 3 is
multiplication; Tier 4 is division. A completed championship earns +500 XP once.
Daily Challenge is outside v1.0. Image validation is automatic and blocks
publication; there is no parental approval step in v1.0.

**Rationale**: These rules follow the higher-priority source documents and
their explicit GDD or Game Economy rules. The user confirmed the only missing
choices: championship points, legacy ownership, and Level 1 baseline.

### Transactions and idempotency

**Decision**: Use the request's SQLAlchemy session transaction. Repositories
flush but do not commit. Store the idempotency key with the saved result.

**Rationale**: `get_session` commits once after the route returns and rolls
back on an exception. This supports one atomic result flow without adding a
transaction framework.

### Offline storage

**Decision**: Use browser IndexedDB with a small typed wrapper. Keep queued
results until the server confirms sync.

**Rationale**: The frontend has no offline persistence for child data. A new
dependency is not required for this bounded use case.

### Rate limits

**Decision**: Use Redis counters for login and registration. Retain the
documented avatar limits: two active jobs and ten generations per hour per
account. Store limits and windows as named settings.

**Rationale**: Redis is already a project dependency and supports multi-worker
limits. Do not use in-memory counters.

## Known Constraints

- The project must use reversible Alembic migrations where practical.
- AI and storage calls must stay in infrastructure adapters.
- The Prompt Builder remains the only prompt construction path.
- A failed or unavailable content-safety check must block publication.
- Performance, browser, accessibility, and restore targets require environment
  evidence. Code inspection alone cannot prove them.
