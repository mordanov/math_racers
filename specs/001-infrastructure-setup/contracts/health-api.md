# Contract: Health Endpoint

**Version**: 1.0
**Owner**: backend service
**Consumers**: Nginx (upstream health check), Docker Compose health check, monitoring system

---

## Endpoint

```
GET /health
```

No authentication required. No request body. No query parameters.

---

## Response — Healthy

**Status**: `200 OK`

```json
{
  "status": "ok",
  "version": "a3f1c9d",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "storage": "ok"
  }
}
```

---

## Response — Degraded (non-critical dependency unavailable)

**Status**: `200 OK`

The backend remains usable. Non-critical features may be unavailable.

```json
{
  "status": "degraded",
  "version": "a3f1c9d",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "storage": "unavailable"
  }
}
```

Storage is a non-critical dependency. A degraded status does not prevent
the backend from serving requests unrelated to asset generation.

---

## Response — Unavailable (critical dependency down)

**Status**: `503 Service Unavailable`

The backend cannot serve requests reliably.

```json
{
  "status": "unavailable",
  "version": "a3f1c9d",
  "checks": {
    "database": "unavailable",
    "redis": "ok",
    "storage": "ok"
  }
}
```

Database unavailability is the primary condition that produces `503`.

---

## Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `status` | `"ok" \| "degraded" \| "unavailable"` | Overall health summary |
| `version` | string | Git SHA of the running backend image |
| `checks.database` | `"ok" \| "unavailable"` | PostgreSQL connectivity |
| `checks.redis` | `"ok" \| "unavailable"` | Redis connectivity |
| `checks.storage` | `"ok" \| "unavailable"` | Object storage reachability |

---

## Behaviour Rules

1. The endpoint MUST respond within 100 ms under normal load.
2. The endpoint MUST NOT perform write operations.
3. The endpoint MUST NOT require authentication headers.
4. The `version` field MUST match the `VERSION` environment variable injected
   at container build time.
5. If the database check fails, `status` MUST be `"unavailable"` and HTTP
   status MUST be `503`.
6. If only storage is unavailable, `status` MUST be `"degraded"` and HTTP
   status MUST be `200`.
7. The endpoint MUST be reachable even when Redis is unavailable.

---

## Docker Compose Health Check Usage

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 10s
```
