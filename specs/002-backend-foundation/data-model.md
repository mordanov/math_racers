# Data Model: Backend Foundation

**Branch**: `002-backend-foundation` | **Date**: 2026-08-09

---

## Entity: Account

**Table**: `accounts`

Primary entity for all authenticated users. Holds both parent accounts and administrator accounts.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID | No | `gen_random_uuid()` | Primary key |
| `email` | VARCHAR(255) | No | — | Unique; lowercase-normalised at write |
| `password_hash` | VARCHAR(72) | No | — | bcrypt hash; never returned in API responses |
| `role` | VARCHAR(20) | No | `'parent'` | CHECK (`'parent'`, `'administrator'`) |
| `approval_status` | VARCHAR(20) | No | `'pending'` | CHECK (`'pending'`, `'approved'`, `'rejected'`) |
| `created_at` | TIMESTAMPTZ | No | `now()` | Immutable after insert |
| `approved_at` | TIMESTAMPTZ | Yes | NULL | Set when admin approves; NULL for pending/rejected |
| `approved_by` | UUID (FK → accounts.id) | Yes | NULL | Administrator who approved; NULL for pending/rejected |

**Indexes**:
- UNIQUE on `email`
- INDEX on `(role, approval_status)` — supports the list-accounts query filtered by both
- INDEX on `approval_status` — supports pending account count check

**Constraints**:
- `approved_at` and `approved_by` must both be NULL or both be non-NULL (enforced at application layer)
- Administrator accounts seeded from env are inserted with `approval_status = 'approved'`
- `approved_by` for the seed administrator is self-referencing (the seeded admin ID)

**State transitions**:
```
                ┌──────────┐
  register ──► │ pending  │──► approved_by_admin ──► approved
                └──────────┘
                     │
                     └──► rejected_by_admin ──► rejected (terminal)
```

---

## Entity: RefreshToken

**Table**: `refresh_tokens`

One-to-many from `accounts`. Each approved login issues one refresh token. Tokens are invalidated (hard-deleted or soft-deleted) on use (rotation) or logout.

| Column | Type | Nullable | Default | Notes |
|--------|------|----------|---------|-------|
| `id` | UUID | No | `gen_random_uuid()` | Primary key |
| `account_id` | UUID (FK → accounts.id, ON DELETE CASCADE) | No | — | Owning account |
| `token_hash` | VARCHAR(64) | No | — | SHA-256 of the raw opaque token; never store raw |
| `issued_at` | TIMESTAMPTZ | No | `now()` | Immutable after insert |
| `expires_at` | TIMESTAMPTZ | No | — | `issued_at + JWT_REFRESH_TTL_DAYS` |
| `revoked_at` | TIMESTAMPTZ | Yes | NULL | Set on rotation or logout; NULL = active |
| `replaced_by` | UUID (FK → refresh_tokens.id) | Yes | NULL | Points to the new token issued during rotation |

**Indexes**:
- UNIQUE on `token_hash`
- INDEX on `(account_id, revoked_at)` — supports active-token lookup per account
- INDEX on `expires_at` — supports background cleanup of expired tokens

**Invariants**:
- Only one active (non-revoked, non-expired) refresh token per account is enforced at the application layer (not DB). Strict rotation means old tokens are immediately revoked when a new one is issued.
- `ON DELETE CASCADE` ensures all tokens are removed when the account is deleted.

---

## Entity: JobAudit (existing)

**Table**: `job_audit` — already created in migration `0001`. No changes needed.

Documented here for completeness.

| Column | Type | Notes |
|--------|------|-------|
| `job_id` | UUID PK | Idempotency key |
| `job_type` | VARCHAR(100) | |
| `payload` | JSONB | |
| `created_at` | TIMESTAMPTZ | |
| `attempts` | INTEGER | |
| `status` | VARCHAR(50) | `pending`, `running`, `succeeded`, `failed`, `permanent_failure` |

---

## Alembic Migration Plan

| Migration | Action |
|---|---|
| `0002_accounts_table.py` | Create `accounts` table with all columns, indexes, and CHECK constraints |
| `0003_refresh_tokens_table.py` | Create `refresh_tokens` table with FK to `accounts` |

Migrations are separate to enable independent rollback. Both are created in this feature.

---

## No Cross-Domain Imports

The `accounts` domain module never imports from `avatars`, `races`, or any other domain module.

Cross-domain operations (e.g. "account deleted → delete child profiles") will use domain events dispatched through an application-service event bus, implemented in a later feature.

---

## Access Patterns (query reference for task generation)

| Operation | Query shape |
|---|---|
| Login lookup | `SELECT * FROM accounts WHERE email = $1` |
| Pending accounts list | `SELECT * FROM accounts WHERE approval_status = $1 [AND role = $2]` |
| Approve/reject account | `UPDATE accounts SET approval_status, approved_at, approved_by WHERE id = $1` |
| Minimum admin check | `SELECT COUNT(*) FROM accounts WHERE role = 'administrator' AND approval_status = 'approved'` |
| Active refresh token lookup | `SELECT * FROM refresh_tokens WHERE token_hash = $1 AND revoked_at IS NULL AND expires_at > now()` |
| Revoke all tokens for account | `UPDATE refresh_tokens SET revoked_at = now() WHERE account_id = $1 AND revoked_at IS NULL` |
