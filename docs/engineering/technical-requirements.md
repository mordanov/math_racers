# Technical Requirements & Non-Functional Requirements

**Level:** Specification
**Status:** Authoritative
**Source:** GDD Chapter 12; speckit_constitution.md
**Parent:** [Epic E6 — Engineering](../prd.md)
**See also:** [../adr/](../../initial_spec/ADR/)

---

## Engineering Philosophy

> **Simple systems are easier to extend than clever systems.**

- Prefer readability over brevity.
- Prefer explicitness over magic.
- Every engineer joining the project must understand the architecture within a few days.

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend language | Python 3.13 |
| Backend framework | FastAPI + Uvicorn |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Database | PostgreSQL |
| Job queue | Redis (via background workers) |
| Frontend language | TypeScript |
| Frontend framework | React |
| Build tool | Vite |
| Container | Docker Compose |
| Reverse proxy | Nginx |
| AI image provider | OpenAI GPT Image (via provider abstraction) |
| Object storage | S3-compatible |

---

## Architecture Principles

- **Clean Architecture**: Domain → Application → Infrastructure → Presentation
- **Domain-Driven Design**: bounded contexts per domain (races, avatars, mathematics, statistics, progression, accounts, assets, ai, shared)
- **Event-driven**: cross-domain communication via explicit events and interfaces
- **Repository pattern**: persistence abstracted behind interfaces
- **Race simulation in browser**: never server-side during gameplay

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Application startup | < 3 seconds |
| Race loading | < 2 seconds |
| Avatar gallery load | < 500 ms |
| Problem generation | < 1 ms |
| Audio feedback latency | < 50 ms |
| Target frame rate | 60 FPS |
| Minimum frame rate | 30 FPS |

Animation quality degrades gracefully on slower hardware. Gameplay timing is unaffected.

---

## Browser & Device Support

**Browsers (current stable only):** Chrome, Edge, Firefox, Safari

**Devices:**
- Primary: Desktop, Laptop, Tablet
- Secondary: Large-screen mobile
- Out of scope: Small phones (< 480px)

---

## Network Requirements

| Feature | Network Dependency |
|---------|-------------------|
| Race simulation | None (client-side) |
| Math validation | None (client-side) |
| Avatar generation | Required |
| Statistics sync | Background |
| Account operations | Required |

The game should fail gracefully offline: Training Mode, previously generated avatars, and cached statistics remain available.

---

## Security Requirements

- HTTPS only; no HTTP connections accepted.
- Secure cookies (HttpOnly, Secure, SameSite=Lax).
- CSRF protection on state-changing endpoints.
- Input validation at every API boundary.
- Output encoding on all user-supplied content.
- Rate limiting on generation and authentication endpoints.
- JWT tokens with expiry; refresh token rotation.
- No secrets committed to source control.
- Principle of least privilege for all service accounts.

---

## Privacy Requirements

The application stores data about children.

- Collect minimal personal data.
- Encrypt sensitive information at rest.
- Provide deletion capabilities for all child data.
- No educational analytics shared publicly.
- Parents retain full control of all stored data.
- COPPA-aware data practices.

---

## Testing Strategy

```
Unit Tests (majority)
       ↓
Integration Tests
       ↓
End-to-End Tests (key user journeys)
```

**Unit test coverage:** every business rule — race scoring, achievement unlocking, statistics calculation, math generation, adaptive difficulty.

**Integration test coverage:** API behaviour, database interactions, authentication, persistence, background workers.

**E2E scenarios:** create avatar → start race → complete race → view statistics → unlock achievement.

External dependencies are mocked in unit and integration tests. E2E tests use a test environment with real dependencies.

---

## API Design

- RESTful, versioned (`/api/v1/`).
- Predictable, idempotent where applicable.
- Consistent naming conventions.
- Structured error responses (error code + human message).
- Documented with OpenAPI schema.
- Future GraphQL support without replacing REST.

---

## Observability

- Structured JSON logs with correlation IDs.
- Metrics: response time, generation failures, API latency, race completion rate, active users.
- Health check endpoints for all services.
- Critical alerts: API failures, generation failures, auth failures, storage failures, unusually slow responses.
- Sensitive information never logged.

---

## Deployment

- Docker Compose for local development and production.
- Reproducible builds; immutable artefacts.
- Automated database migrations on deploy.
- Rollback capability.
- Zero-downtime deployments where practical.
- CI/CD pipeline with linting, formatting, static analysis, tests, and container build.

---

## Data Persistence

- ACID-compliant database for all critical data.
- Schema migrations with version history.
- Immutable UUIDs as primary keys.
- Audit timestamps (created_at, updated_at) on all entities.
- Regular backups of: avatars, statistics, achievements, player progress, generated prompts, metadata.
- No progress should be lost during schema updates.

---

## Coding Standards

- Automatic formatting (Black for Python, Prettier for TypeScript).
- Static analysis (mypy, ESLint).
- Linting enforced by CI.
- Type checking required (strict mode).
- Code review before merging.

---

## Success Criteria

The technical architecture is successful when:
- Gameplay is smooth on target hardware.
- AI services can be swapped without touching gameplay code.
- New game modes can be added with minimal architectural changes.
- Production incidents are observable and recoverable within 15 minutes.
- Engineering complexity is invisible to the player.
