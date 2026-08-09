# Quickstart: Backend Foundation

**Branch**: `002-backend-foundation` | **Date**: 2026-08-09

End-to-end integration scenarios. Each scenario can be executed against a running local stack (`docker compose up`) or the CI integration test suite.

---

## Prerequisites

```bash
# Start the stack
docker compose up -d

# Confirm healthy
curl -s http://localhost/health | jq .
# Expected: { "status": "ok", ... }
```

Ensure `.env` contains:
```
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=Admin1234!
```

---

## Scenario 1: Administrator Seeding

Verifies the default administrator is created on startup when no administrator exists.

```bash
# The stack just started with a clean database. Check the seeded admin exists.
# Log in as the seeded administrator — should succeed immediately.

curl -s -c cookies.txt -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Admin1234!"}' | jq .

# Expected:
# { "access_token": "eyJ...", "token_type": "bearer" }
```

---

## Scenario 2: Parent Registration and Approval Flow

Full happy path: register → blocked → approve → login.

```bash
# Step 1: Register a parent account
curl -s -X POST http://localhost/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"parent@example.com","password":"Parent1234!"}' | jq .
# Expected: { "message": "Registration successful. Awaiting administrator approval." }

# Step 2: Attempt login before approval — must be blocked
curl -s -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"parent@example.com","password":"Parent1234!"}' | jq .
# Expected: { "error_code": "ACCOUNT_PENDING", ... } HTTP 403

# Step 3: Log in as administrator
curl -s -c admin-cookies.txt -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Admin1234!"}' | jq .
# Capture access_token from response → $ADMIN_TOKEN

# Step 4: List pending accounts
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost/api/v1/admin/accounts?status=pending" | jq .
# Expected: accounts array containing parent@example.com
# Capture parent account ID → $PARENT_ID

# Step 5: Approve the parent account
curl -s -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost/api/v1/admin/accounts/$PARENT_ID/approve" | jq .
# Expected: { "approval_status": "approved", ... }

# Step 6: Parent can now log in
curl -s -c parent-cookies.txt -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"parent@example.com","password":"Parent1234!"}' | jq .
# Expected: { "access_token": "eyJ...", "token_type": "bearer" }
```

---

## Scenario 3: Rejection Flow

```bash
# Register another account
curl -s -X POST http://localhost/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"rejected@example.com","password":"Test1234!"}' | jq .

# Reject it (uses $ADMIN_TOKEN and $REJECTED_ID from list)
curl -s -X POST -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost/api/v1/admin/accounts/$REJECTED_ID/reject" | jq .
# Expected: { "approval_status": "rejected", ... }

# Attempt login — must return ACCOUNT_REJECTED (not ACCOUNT_PENDING)
curl -s -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"rejected@example.com","password":"Test1234!"}' | jq .
# Expected: { "error_code": "ACCOUNT_REJECTED", ... } HTTP 403
```

---

## Scenario 4: Token Rotation

```bash
# Log in to get initial refresh token cookie
curl -s -c parent-cookies.txt -b parent-cookies.txt \
  -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"parent@example.com","password":"Parent1234!"}' | jq .

# Use refresh to get a new access token
curl -s -c parent-cookies.txt -b parent-cookies.txt \
  -X POST http://localhost/api/v1/auth/refresh | jq .
# Expected: new access_token; new Set-Cookie refresh_token

# Use the OLD refresh token cookie — must be rejected (rotation)
# (Manually set cookie to old value)
curl -s -b "refresh_token=<old-token-value>" \
  -X POST http://localhost/api/v1/auth/refresh | jq .
# Expected: { "error_code": "INVALID_REFRESH_TOKEN", ... } HTTP 401
```

---

## Scenario 5: Last Administrator Protection

```bash
# Attempt to delete the only administrator account
curl -s -X DELETE -H "Authorization: Bearer $ADMIN_TOKEN" \
  "http://localhost/api/v1/admin/accounts/$ADMIN_SELF_ID" | jq .
# Expected: { "error_code": "LAST_ADMINISTRATOR", ... } HTTP 400
```

---

## Scenario 6: Health Endpoint

```bash
# Full stack up
curl -s http://localhost/health | jq .
# Expected: { "status": "ok", "checks": { "database": "ok", "redis": "ok", ... } }

# Stop postgres, re-check
docker compose stop postgres
curl -s http://localhost/health | jq .
# Expected: { "status": "unavailable", "checks": { "database": "unavailable", ... } } HTTP 503

docker compose start postgres
```

---

## Scenario 7: Correlation ID Propagation

```bash
# Send request with custom X-Request-ID
curl -s -H "X-Request-ID: test-trace-abc123" \
  http://localhost/api/v1/auth/login \
  -X POST -H "Content-Type: application/json" \
  -d '{"email":"x","password":"y"}' -v 2>&1 | grep -i x-request-id
# Expected: X-Request-ID: test-trace-abc123 in response headers

# Send request without X-Request-ID
curl -s http://localhost/health -v 2>&1 | grep -i x-request-id
# Expected: X-Request-ID: <generated-uuid> in response headers
```
