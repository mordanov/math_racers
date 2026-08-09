# Feature Specification: Backend Foundation

**Feature Branch**: `002-backend-foundation`
**Created**: 2026-08-09
**Status**: Draft
**Source**: docs/engineering/spec-backend-foundation.md

## Clarifications

### Session 2026-08-09

- Q: What is the authentication method? → A: Email and password only; no social/SSO login.
- Q: How are administrator accounts created and seeded? → A: A default administrator is always seeded from environment configuration at startup; administrator accounts can only be created by an existing administrator, never via self-registration.
- Q: Is there an account approval workflow? → A: Yes — all self-registered accounts start in a pending state and cannot access the platform until an administrator explicitly approves them.
- Q: What is the minimum administrator constraint? → A: The system must always have at least one administrator; any action that would remove the last administrator is rejected.
- Q: Can an administrator reject a pending account, or only approve? → A: Both — administrators can approve or reject. Rejection moves the account to a permanent rejected state; the account holder cannot log in and receives no automatic notification from this system.
- Q: Does the system expose account listing so administrators can discover pending accounts? → A: Yes — a list-accounts endpoint filterable by status (pending, approved, rejected) is required; accessible to administrators only.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Account Registration and Administrator Approval (Priority: P1)

A visitor submits their email address and a password to register. The system creates their account in a pending state. They cannot access any protected part of the platform until an administrator reviews and approves their registration. Once approved, they log in and receive a session. If they are inactive for a short period the session expires; a single tap renews it without re-entering credentials.

A default administrator account is always present — seeded from environment configuration at every service startup. Administrator accounts can only be created by existing administrators; self-registration as an administrator is not permitted. The system enforces that at least one administrator account exists at all times.

**Why this priority**: Authentication and the approval gate are the entry point to every other feature. Nothing else is usable until accounts, roles, and the approval workflow all work.

**Independent Test**: Can be fully tested by registering an account, confirming it is blocked before approval, approving it as the seeded administrator, logging in, making authenticated requests, and verifying session expiry and renewal.

**Acceptance Scenarios**:

1. **Given** a visitor with a valid email and a strong password, **When** they submit the registration form, **Then** the system creates their account in a pending state and they cannot access any protected resource.
2. **Given** a pending account, **When** an administrator approves it, **Then** the account holder can log in and receive a valid session.
3. **Given** a pending account, **When** the account holder attempts to log in, **Then** the system rejects the attempt with a clear message indicating the account is awaiting approval (not a generic credential failure).
4. **Given** an approved account holder, **When** they log in with correct credentials, **Then** the system issues a short-lived session token and a long-lived renewal token stored in a secure cookie.
5. **Given** an account holder whose short-lived token has expired, **When** they make any request, **Then** the system transparently issues a new token using the renewal cookie without requiring the password again.
6. **Given** an account holder who uses the same renewal token twice, **When** the second use is attempted, **Then** the system rejects it and the account holder must log in again (token rotation security).
7. **Given** a logged-in account holder, **When** they log out, **Then** all renewal tokens are invalidated and subsequent requests are rejected.
8. **Given** an unrecognised email or wrong password on an approved account, **When** login is attempted, **Then** the system returns a generic failure message that does not reveal which field was wrong.
9. **Given** the service starts, **When** no administrator account exists yet, **Then** the system creates the default administrator account from environment configuration before accepting any requests.
10. **Given** an administrator attempts to remove or deactivate the last remaining administrator account, **When** the action is submitted, **Then** the system rejects it to prevent losing all administrative access.
11. **Given** a rejected account holder attempts to log in, **When** the login is attempted, **Then** the system returns a distinct "account rejected" response — not a generic credential failure and not "pending approval".

---

### User Story 1a - Administrator Account Review (Priority: P1)

An administrator views a list of accounts filtered by status. They select a pending account and either approve or reject it. The list updates to reflect the new status.

**Why this priority**: Without the ability to discover and act on pending accounts, the approval workflow defined in User Story 1 cannot be exercised; these two stories form a single usable increment.

**Independent Test**: Can be tested by seeding a pending account, listing pending accounts as the default administrator, approving one and rejecting another, then verifying the list reflects the updated statuses and that the approved account can log in while the rejected one cannot.

**Acceptance Scenarios**:

1. **Given** an authenticated administrator, **When** they request the account list filtered to pending status, **Then** only accounts in pending state are returned.
2. **Given** an authenticated administrator, **When** they approve a pending account, **Then** the account status changes to approved and the account holder can now log in.
3. **Given** an authenticated administrator, **When** they reject a pending account, **Then** the account status changes to rejected and the account holder cannot log in.
4. **Given** an authenticated non-administrator (parent), **When** they attempt to access the account list, **Then** the system rejects the request with an authorisation error.
5. **Given** an unauthenticated request, **When** the account list endpoint is called, **Then** the system rejects it before any data is returned.

---

### User Story 2 - Child Profile Access (Priority: P2)

A logged-in parent selects which of their child profiles to act on behalf of. All subsequent actions (starting a race, viewing stats) are scoped to the chosen child. A parent cannot access another family's child profiles.

**Why this priority**: The platform's core audience is children; the parent-child relationship is fundamental to all domain features.

**Independent Test**: Can be tested by a parent authenticating and then performing an action that references a child profile ID — confirming that their own children are accessible and another family's children are rejected.

**Acceptance Scenarios**:

1. **Given** an authenticated parent, **When** they reference one of their own child profile IDs in a request, **Then** the system processes the request normally.
2. **Given** an authenticated parent, **When** they reference a child profile ID belonging to another account, **Then** the system rejects the request with a clear authorisation error.
3. **Given** an unauthenticated request referencing any child profile, **Then** the system rejects it before any child data is accessed.

---

### User Story 3 - Background Job Processing (Priority: P3)

When a user action (e.g. completing a race) triggers work that cannot complete instantly (such as generating an avatar image), the system accepts the request immediately, queues the work, and processes it in the background. If the work fails, it is retried automatically up to three times. If all retries fail, the failure is recorded for review. The user does not wait and is not left with a silent error.

**Why this priority**: Enables the platform to handle slow third-party operations (AI generation) without degrading the interactive experience.

**Independent Test**: Can be tested by submitting a job that is configured to fail, observing three automatic retries with increasing wait times, and confirming the final failure is persisted durably.

**Acceptance Scenarios**:

1. **Given** a job submitted to the queue, **When** the first processing attempt succeeds, **Then** the job is marked complete with no side effects if re-run.
2. **Given** a job that fails on the first attempt, **When** the system retries, **Then** each retry waits progressively longer (approximately 30 s, 2 min, 8 min).
3. **Given** a job that fails all three retries, **When** no more attempts are made, **Then** the failure is persisted durably and visible to operators.
4. **Given** a job submitted twice with the same unique identifier, **When** the second submission arrives, **Then** the job is not processed twice.

---

### User Story 4 - System Health Visibility (Priority: P4)

An operator or monitoring tool can check whether the platform is healthy at any time without authentication. The response tells them whether the service is fully operational, partially degraded (can still serve users but something is wrong), or fully down — and which specific components are the problem.

**Why this priority**: Operational visibility is essential for reliable deployments and incident response, but delivers no end-user value until other stories are working.

**Independent Test**: Can be tested independently by calling the health endpoint and verifying the response reflects the actual state of backing services (e.g. disconnecting the database and observing the status change).

**Acceptance Scenarios**:

1. **Given** all components are reachable, **When** the health endpoint is called, **Then** the response indicates fully operational status.
2. **Given** the database is unreachable but the service is still running, **When** the health endpoint is called, **Then** the response indicates degraded status, names the database as the problem component, and returns a success HTTP status (so monitoring does not page unnecessarily).
3. **Given** the service itself cannot start (e.g. database unavailable at boot), **When** the health endpoint is called, **Then** no response is served — the process exits and the container is restarted automatically.

---

### User Story 5 - Request Traceability (Priority: P5)

Every request through the system is assigned a unique identifier. That identifier appears in all logs related to the request, in any background work the request triggers, and in the response returned to the caller. Support and engineering can use this identifier to reconstruct exactly what happened during any given request.

**Why this priority**: Traceability is a cross-cutting quality attribute. Valuable once the system is in production but delivers no user-facing functionality.

**Independent Test**: Can be tested by making a request, capturing the identifier from the response, and verifying that all log entries and any spawned background jobs reference the same identifier.

**Acceptance Scenarios**:

1. **Given** an incoming request with no identifier header, **When** the request is processed, **Then** the system generates a unique identifier and includes it in all logs, the response, and any background jobs.
2. **Given** an incoming request that already carries an identifier, **When** the request is processed, **Then** the system uses that identifier rather than generating a new one.
3. **Given** any error response, **When** the caller receives it, **Then** the identifier is present in the response body alongside the error details.

---

### Edge Cases

- What happens when the database is unavailable at application startup? The process must exit immediately rather than silently serving requests with no persistence.
- What happens when a client presents an expired short-lived token and the renewal token is also expired or revoked? The session cannot be refreshed; the user must log in again.
- What happens when the same idempotent job is submitted a second time? The second submission must not trigger re-processing.
- What happens when a background job queue becomes overloaded beyond a configurable threshold? New submissions must be rejected with a clear capacity error rather than silently dropping or indefinitely queuing.
- What happens when a database migration is incomplete at startup? The service must refuse to start until the schema is current.
- What happens when a pending account attempts to access a protected resource? The system must reject with a specific "pending approval" error, not a generic authentication failure.
- What happens when an administrator tries to remove the only remaining administrator account? The system must reject the action and preserve the minimum-one-administrator invariant.
- What happens when the default administrator credentials are absent from environment configuration at startup? The service must fail to start with a clear configuration error.
- What happens when a non-administrator tries to create or promote an administrator account? The system must reject the action regardless of the requester's approval status.
- What happens when a rejected account holder attempts to log in? The system must return a distinct "account rejected" response, not a generic credential failure and not the "pending approval" message.
- Can a rejected account be re-approved later? This is not specified as a requirement — rejected state is permanent in this feature.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow accounts to be created with a unique email address and a password; all newly registered accounts start in a pending state.
- **FR-001a**: System MUST seed a default administrator account from environment configuration at every startup if no administrator account exists.
- **FR-001b**: Administrator accounts MUST only be created or promoted by an existing administrator; self-registration as an administrator is not permitted.
- **FR-001c**: System MUST enforce that at least one administrator account exists at all times; any action that would remove the last administrator MUST be rejected.
- **FR-001d**: System MUST block all access to protected resources for accounts in pending state; login must return a distinct "pending approval" response, not a generic credential failure.
- **FR-001e**: An administrator MUST be able to approve a pending account, after which the account holder may log in normally.
- **FR-001f**: An administrator MUST be able to reject a pending account; a rejected account moves to a permanent rejected state and the account holder cannot log in. The system does not send automatic notification to the rejected account holder.
- **FR-001g**: System MUST expose an account listing capability accessible only to administrators, filterable by account status (pending, approved, rejected), so administrators can discover and act on accounts awaiting review.
- **FR-002**: System MUST issue a short-lived session token and a long-lived renewal token upon successful login by an approved account.
- **FR-003**: System MUST store renewal tokens in a secure, HTTP-only cookie inaccessible to client-side scripts.
- **FR-004**: System MUST rotate renewal tokens on each use — invalidating the previously issued token and issuing a new one.
- **FR-005**: System MUST reject any request to a protected resource that does not carry a valid, unexpired session token.
- **FR-006**: System MUST validate that any child profile referenced in a request belongs to the authenticated account before processing.
- **FR-007**: System MUST accept background jobs and return immediately, processing work asynchronously without blocking the caller.
- **FR-008**: System MUST retry failed background jobs up to three times with exponentially increasing wait intervals.
- **FR-009**: System MUST record permanently failed jobs (exhausted all retries) for operator review.
- **FR-010**: System MUST process idempotent jobs exactly once even if submitted multiple times with the same identifier.
- **FR-011**: System MUST expose a health endpoint accessible without authentication that reports operational, degraded, or down status along with per-component detail.
- **FR-012**: System MUST exit at startup rather than serve requests if the data store schema is not current.
- **FR-013**: System MUST assign a unique request identifier to every inbound request and propagate it through all log entries, background jobs, and error responses.
- **FR-014**: System MUST return a structured error response (a code plus a human-readable message) for all failure cases, with no internal stack traces visible to callers.
- **FR-015**: System MUST reject new background job submissions when the queue depth exceeds a configurable safety threshold.
- **FR-016**: All configuration (credentials, keys, connection strings) MUST be supplied via environment variables; no values may be hardcoded.

### Key Entities

- **Account**: A user's identity — unique email, hashed credentials, role (parent or administrator), approval status (pending, approved, or rejected), and one or more child profiles (for parent accounts).
- **Role**: A classification of an account — either administrator (can approve accounts and manage other administrators) or parent (subject to approval before access).
- **Child Profile**: A named profile belonging to a parent account, used to scope gameplay and progress.
- **Session Token**: A short-lived credential that grants access to protected resources for a single session window.
- **Renewal Token**: A long-lived, single-use credential that exchanges for a new session token without requiring the password.
- **Background Job**: A unit of deferred work with a type, payload, status, attempt count, and audit trail.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new parent account can be created and a first authenticated request made in under 10 seconds end to end.
- **SC-002**: Session refresh (exchanging a renewal token for a new session) completes without any perceptible delay to the user.
- **SC-003**: A failed background job is retried and eventually succeeds without any user intervention, within the defined retry window.
- **SC-004**: The health endpoint accurately reflects a component failure within 30 seconds of the failure occurring.
- **SC-005**: 100% of error responses returned to callers contain a structured error code and message — zero unhandled exceptions leak to the API surface.
- **SC-006**: Every log entry for a given request shares the same request identifier, enabling full trace reconstruction from a single identifier.
- **SC-007**: The service refuses to start if the data store is unavailable or the schema is not current — confirmed by 100% of startup-failure scenarios resulting in a clean process exit rather than a degraded serving state.

---

## Assumptions

- All accounts are created directly with email + password; no third-party identity provider (social login) is in scope for this feature.
- There are two roles: administrator and parent. Parent is the default role for self-registered accounts. Administrator can only be assigned by an existing administrator.
- The default administrator credentials (email and password) must be present in environment configuration; the service refuses to start without them.
- Child profiles are managed by separate flows not covered here; this feature only validates ownership — it does not create or modify child profiles.
- The background job queue is expected to handle bursts of up to 1,000 queued jobs; beyond that, the capacity safety threshold kicks in.
- Mobile and browser clients are the primary callers; the HTTP-only renewal cookie approach is compatible with both.
- All secrets (signing key, database credentials, storage keys, default administrator credentials) are provisioned by the deployment environment; no defaults are acceptable for these values.
- The service runs behind a TLS-terminating proxy in production; internal service-to-service calls are on a private network.
