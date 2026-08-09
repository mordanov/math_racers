# Contract: Administrator Account Management API

**Module**: `accounts`
**Base path**: `/api/v1/admin`
**Version**: v1
**Authentication**: Bearer access token required; `role` claim MUST be `"administrator"`

All endpoints in this contract return 403 `FORBIDDEN` if the caller is not an administrator.

---

## GET /api/v1/admin/accounts

List accounts, filterable by status. Administrators only.

**Query parameters**:

| Parameter | Type | Required | Default | Valid values |
|-----------|------|----------|---------|--------------|
| `status` | string | No | _(all)_ | `pending`, `approved`, `rejected` |
| `role` | string | No | _(all)_ | `parent`, `administrator` |
| `limit` | integer | No | 50 | 1–200 |
| `offset` | integer | No | 0 | ≥ 0 |

**Response 200**:
```json
{
  "accounts": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "role": "parent",
      "approval_status": "pending",
      "created_at": "2026-08-09T12:00:00Z",
      "approved_at": null,
      "approved_by": null
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

| Status | Condition |
|--------|-----------|
| 200 | Success (empty `accounts` array is valid) |
| 401 | Missing or invalid access token |
| 403 | Caller is not an administrator |

---

## POST /api/v1/admin/accounts/{account_id}/approve

Approve a pending account. Only pending accounts can be approved.

**Path parameter**: `account_id` — UUID of the account to approve.

**Request body**: _(empty)_

**Responses**:

| Status | Condition | Body |
|--------|-----------|------|
| 200 | Account approved | `{ "id": "uuid", "email": "...", "approval_status": "approved", "approved_at": "iso8601", "approved_by": "admin-uuid" }` |
| 400 | Account is not in pending state | `{ "error_code": "INVALID_ACCOUNT_STATE", "message": "Account is not pending.", "request_id": "uuid" }` |
| 401 | Missing or invalid access token | standard error |
| 403 | Caller is not an administrator | standard error |
| 404 | Account not found | `{ "error_code": "ACCOUNT_NOT_FOUND", "message": "Account not found.", "request_id": "uuid" }` |

---

## POST /api/v1/admin/accounts/{account_id}/reject

Reject a pending account. Rejection is permanent; rejected accounts cannot be approved later.

**Path parameter**: `account_id` — UUID of the account to reject.

**Request body**: _(empty)_

**Responses**:

| Status | Condition | Body |
|--------|-----------|------|
| 200 | Account rejected | `{ "id": "uuid", "email": "...", "approval_status": "rejected" }` |
| 400 | Account is not in pending state | `{ "error_code": "INVALID_ACCOUNT_STATE", "message": "Account is not pending.", "request_id": "uuid" }` |
| 401 | Missing or invalid access token | standard error |
| 403 | Caller is not an administrator | standard error |
| 404 | Account not found | standard error |

---

## POST /api/v1/admin/accounts

Create a new administrator account directly (bypasses the approval workflow). Only administrators can call this endpoint. The newly created account is immediately `approved`.

**Request body**:
```json
{
  "email": "admin2@example.com",
  "password": "••••••••",
  "role": "administrator"
}
```

| Field | Type | Validation |
|-------|------|------------|
| `email` | string | Valid email; max 255 chars |
| `password` | string | 8–128 chars |
| `role` | string | MUST be `"administrator"` (this endpoint is admin-creation only) |

**Responses**:

| Status | Condition | Body |
|--------|-----------|------|
| 201 | Administrator account created | `{ "id": "uuid", "email": "...", "role": "administrator", "approval_status": "approved", "created_at": "iso8601" }` |
| 400 | `role` is not `"administrator"` | `{ "error_code": "VALIDATION_ERROR", "message": "This endpoint only creates administrator accounts.", "request_id": "uuid" }` |
| 401 | Missing or invalid access token | standard error |
| 403 | Caller is not an administrator | standard error |
| 409 | Email already registered | `{ "error_code": "EMAIL_CONFLICT", "message": "An account with this email already exists.", "request_id": "uuid" }` |

---

## DELETE /api/v1/admin/accounts/{account_id}

Delete an account. Protected by the minimum-one-administrator invariant: if the target is the last approved administrator, the deletion is rejected.

**Path parameter**: `account_id` — UUID of the account to delete.

**Responses**:

| Status | Condition | Body |
|--------|-----------|------|
| 204 | Account deleted | _(empty)_ |
| 400 | Deleting last administrator | `{ "error_code": "LAST_ADMINISTRATOR", "message": "Cannot delete the last administrator account.", "request_id": "uuid" }` |
| 401 | Missing or invalid access token | standard error |
| 403 | Caller is not an administrator | standard error |
| 404 | Account not found | standard error |

---

## Common Error Response Shape

```json
{
  "error_code": "SNAKE_CASE_CODE",
  "message": "Human-readable message safe to display.",
  "request_id": "uuid"
}
```
