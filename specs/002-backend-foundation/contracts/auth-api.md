# Contract: Authentication API

**Module**: `accounts`
**Base path**: `/api/v1/auth`
**Version**: v1
**Authentication**: None required (these endpoints issue credentials)

---

## POST /api/v1/auth/register

Register a new parent account. The account starts in `pending` state and cannot be used until an administrator approves it.

**Request body**:
```json
{
  "email": "user@example.com",
  "password": "••••••••"
}
```

| Field | Type | Validation |
|-------|------|------------|
| `email` | string | Valid email format; max 255 chars |
| `password` | string | 8–128 chars |

**Responses**:

| Status | Condition | Body |
|--------|-----------|------|
| 201 | Account created | `{ "message": "Registration successful. Awaiting administrator approval." }` |
| 409 | Email already registered | `{ "error_code": "EMAIL_CONFLICT", "message": "An account with this email already exists.", "request_id": "uuid" }` |
| 422 | Validation failure | `{ "error_code": "VALIDATION_ERROR", "message": "...", "request_id": "uuid" }` |

No session token is issued at registration. The account must be approved first.

---

## POST /api/v1/auth/login

Authenticate with email and password. Returns a session token (in the JSON body) and a refresh token (in an HttpOnly cookie). Only approved accounts may log in.

**Request body**:
```json
{
  "email": "user@example.com",
  "password": "••••••••"
}
```

**Responses**:

| Status | Condition | Body |
|--------|-----------|------|
| 200 | Credentials valid, account approved | `{ "access_token": "jwt...", "token_type": "bearer" }` + Set-Cookie |
| 401 | Credentials invalid (unknown email or wrong password) | `{ "error_code": "INVALID_CREDENTIALS", "message": "Invalid email or password.", "request_id": "uuid" }` |
| 403 | Credentials valid but account is pending | `{ "error_code": "ACCOUNT_PENDING", "message": "Your account is awaiting administrator approval.", "request_id": "uuid" }` |
| 403 | Credentials valid but account is rejected | `{ "error_code": "ACCOUNT_REJECTED", "message": "Your account registration was not approved.", "request_id": "uuid" }` |

**Set-Cookie** (on 200):
```
Set-Cookie: refresh_token=<opaque-uuid>; HttpOnly; Secure; SameSite=Lax; Path=/api/v1/auth/refresh; Max-Age=2592000
```

The cookie path is scoped to `/api/v1/auth/refresh` so it is not sent with other requests.

---

## POST /api/v1/auth/refresh

Exchange a valid refresh token cookie for a new access token and a new refresh token. The old refresh token is immediately revoked (rotation).

**Request**: No body. The refresh token is read from the HttpOnly cookie.

**Responses**:

| Status | Condition | Body |
|--------|-----------|------|
| 200 | Refresh token valid and not revoked | `{ "access_token": "jwt...", "token_type": "bearer" }` + new Set-Cookie |
| 401 | Cookie absent, token not found, expired, or already revoked | `{ "error_code": "INVALID_REFRESH_TOKEN", "message": "Session expired. Please log in again.", "request_id": "uuid" }` |

---

## POST /api/v1/auth/logout

Revoke all refresh tokens for the authenticated account and clear the cookie.

**Authentication**: Bearer access token required (`Authorization: Bearer <jwt>`).

**Responses**:

| Status | Condition | Body |
|--------|-----------|------|
| 204 | All refresh tokens revoked | _(empty)_ + `Set-Cookie: refresh_token=; Max-Age=0` |
| 401 | Missing or invalid access token | `{ "error_code": "UNAUTHORIZED", "message": "Authentication required.", "request_id": "uuid" }` |

---

## Access Token Format

The access token is a signed JWT with the following claims:

| Claim | Value |
|-------|-------|
| `sub` | Account UUID (string) |
| `role` | `"parent"` or `"administrator"` |
| `iat` | Issued-at timestamp |
| `exp` | Expiry timestamp (`iat + JWT_ACCESS_TTL_MINUTES`) |

The token is signed with HMAC-SHA-256 using `JWT_SECRET`. Algorithm is `HS256`.

---

## Common Error Response Shape

All error responses follow:

```json
{
  "error_code": "SNAKE_CASE_CODE",
  "message": "Human-readable message safe to display.",
  "request_id": "uuid"
}
```

No stack traces. No internal field names. `request_id` always matches the `X-Request-ID` response header.
