# Feature Specification: Infrastructure Setup

**Feature Branch**: `001-infrastructure-setup`
**Created**: 2026-08-08
**Status**: Draft
**Input**: User description: "@docs/engineering/spec-infrastructure.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — One-Command Deployment (Priority: P1)

An operator takes a fresh checkout of the repository and brings the entire
application stack online without manual configuration steps beyond supplying
secret values.

**Why this priority**: Without a working deployment, no other feature can be
delivered or tested. This is the foundation every subsequent phase depends on.

**Independent Test**: Running a single command from a clean checkout starts
all services and the application becomes accessible. Delivers the value of a
reproducible, documented deployment process.

**Acceptance Scenarios**:

1. **Given** a clean checkout with secrets configured, **When** the operator
   runs the deployment command, **Then** all services start and a health check
   endpoint returns a healthy status with no manual intervention.
2. **Given** the stack is running, **When** a database schema migration is
   pending, **Then** the migration runs automatically before the application
   accepts traffic.
3. **Given** the backend is started, **When** the database schema is not
   current, **Then** the backend refuses to start and logs a clear diagnostic
   message.

---

### User Story 2 — Automated Quality Gate on Every Commit (Priority: P2)

A developer pushes code to any branch and receives automated feedback on
format, code quality, type safety, test results, and security vulnerabilities
before the change can be merged.

**Why this priority**: Without enforced quality gates, defects, security issues,
and regressions accumulate silently. This gate protects the shared codebase.

**Independent Test**: Introducing a deliberate lint error, a failing test, or
a known-vulnerable dependency triggers a CI failure that blocks merge. Each
check type can be validated independently.

**Acceptance Scenarios**:

1. **Given** a commit with a formatting violation, **When** CI runs, **Then**
   the format check step fails and no further steps execute.
2. **Given** a commit with a failing unit test, **When** CI runs, **Then** the
   test step fails and no container image is built.
3. **Given** a commit that passes all checks on the default branch, **When** CI
   runs, **Then** the deployment step executes automatically after all prior
   steps pass.
4. **Given** a commit that introduces a critical security vulnerability, **When**
   CI runs the security scan, **Then** the scan step fails and the commit is
   blocked from merging.

---

### User Story 3 — Secure Secret and Credential Management (Priority: P3)

An operator configures the application with sensitive credentials (API keys,
database passwords, signing secrets) in a way that keeps them out of version
control and inaccessible to client-side code.

**Why this priority**: Credentials exposed in source control or to end users
create immediate security and compliance risk.

**Independent Test**: Inspecting the repository at any commit contains no
secret values; inspecting the client-side payload contains no secret values.
Can be verified independently of other stories.

**Acceptance Scenarios**:

1. **Given** a fresh clone of the repository, **When** all files are inspected,
   **Then** no secret values appear — only an example template with placeholder
   names.
2. **Given** the application is running, **When** any client-facing response is
   inspected, **Then** no internal credentials, tokens, or API keys appear.
3. **Given** a secret is rotated, **When** the new value is injected at the
   infrastructure level, **Then** the application picks up the new value on
   restart without code changes.

---

### User Story 4 — Data Backup and Recovery (Priority: P4)

An operator can recover application data to a known-good state following data
loss, corruption, or a failed deployment.

**Why this priority**: An educational application accumulates irreplaceable user
progress. Without tested recovery procedures, data loss is permanent.

**Independent Test**: Performing a simulated restore from a backup produces an
identical dataset. Independently verifiable without running the full application.

**Acceptance Scenarios**:

1. **Given** an automated daily backup is configured, **When** 24 hours elapse,
   **Then** a backup has been created and retained according to the retention
   policy.
2. **Given** a backup exists, **When** an operator follows the documented
   restore procedure, **Then** the database is restored to a consistent state.
3. **Given** the job queue service becomes unavailable, **When** it recovers,
   **Then** pending work is re-queued from durable storage with no permanent
   data loss.

---

### User Story 5 — Operational Visibility and Alerting (Priority: P5)

An operator can diagnose incidents quickly by inspecting structured logs and
receiving alerts when the system enters a degraded state.

**Why this priority**: Without observable signals, incidents are discovered only
through user reports, extending mean time to resolution.

**Independent Test**: Generating an error condition produces a structured log
entry with all required fields and triggers an alert where applicable.

**Acceptance Scenarios**:

1. **Given** any service emits a log entry, **When** the entry is inspected,
   **Then** it contains timestamp, severity, service name, request identifier,
   and message — with no sensitive data.
2. **Given** the API error rate exceeds an acceptable threshold, **When** the
   condition persists, **Then** an alert is raised within the defined window.
3. **Given** the health endpoint is queried, **When** any required service is
   unhealthy, **Then** the response reflects a non-healthy status.

---

### Edge Cases

- **Deployment with live traffic**: A new deployment that includes a database
  migration must not corrupt data read by the previous application version
  still serving requests.
- **Redis unavailability at startup**: The application starts and serves core
  requests; features depending on the queue return a clear, user-friendly
  unavailable response rather than an unhandled error.
- **Object storage unreachable**: Avatar generation queues gracefully and
  retries when storage recovers; the health endpoint continues to report the
  backend as operational.
- **Certificate expiry with HSTS active**: Because HSTS prevents HTTP fallback,
  certificate renewal must be automated with advance warnings.
- **Duplicate job processing**: A job processed more than once must produce the
  same outcome as processing it once (idempotent).
- **Container built from uncommitted code**: The CI system must reject image
  builds from a dirty working tree to ensure every production image is
  traceable to a specific commit.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The application stack MUST start from a single command on a
  clean checkout after supplying required secret values.
- **FR-002**: Database migrations MUST apply automatically before the
  application accepts traffic on each deployment.
- **FR-003**: The application MUST refuse to start if the database schema is
  not current, and MUST emit a diagnostic message explaining the block.
- **FR-004**: Every commit to any branch MUST trigger an automated pipeline
  that checks formatting, linting, type safety, tests, and security before
  allowing merge.
- **FR-005**: The pipeline MUST build container images only after all quality
  checks pass; deployment MUST only occur on the default branch.
- **FR-006**: Container images used in production MUST be tagged with an
  immutable identifier traceable to a specific commit; the `latest` tag MUST
  NOT be used in production.
- **FR-007**: Secret values MUST be injected at runtime via the deployment
  environment and MUST NOT appear in version control.
- **FR-008**: No secret values, API keys, or internal credentials MUST appear
  in client-facing responses or logs.
- **FR-009**: All external application traffic MUST be served over TLS; plain
  HTTP requests MUST be redirected to HTTPS.
- **FR-010**: TLS certificate renewal MUST be automated; operators MUST receive
  an advance alert no fewer than 30 days before expiry.
- **FR-011**: Database backups MUST be taken at least daily and retained for at
  least 30 days; restore procedures MUST be tested at least monthly.
- **FR-012**: Pending work items MUST be recoverable from durable storage
  following a queue service restart; no race results or progression data MUST
  be permanently lost.
- **FR-013**: Every log entry MUST include timestamp, severity level, service
  name, and request identifier; sensitive data MUST NOT appear in logs.
- **FR-014**: The application MUST expose a health endpoint that reflects the
  live status of its dependencies.
- **FR-015**: Security scans MUST run on every CI build; a critical
  vulnerability finding MUST block the build.

### Key Entities

- **Deployment**: A versioned, traceable release of the application stack tied
  to a specific commit.
- **Migration**: A versioned, ordered schema change applied automatically on
  deploy; each migration is reversible where practical.
- **Secret**: A credential or key injected at runtime, never stored in the
  repository.
- **Backup**: A point-in-time snapshot of application data retained for a
  defined period, verified by periodic restore tests.
- **Job**: A unit of deferred work (e.g., asset generation) stored durably and
  processed at most once with idempotent outcomes.
- **Health check**: A real-time signal from each service indicating whether it
  is ready to serve requests.
- **Log entry**: A structured record of an event, containing standard fields
  and free of sensitive data.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer with repository access and secrets can bring the
  full application stack online in under 5 minutes from a clean checkout.
- **SC-002**: A code change that introduces a lint error, failing test, or
  critical security vulnerability is blocked from merging within the CI run
  that processes it.
- **SC-003**: A data restore exercise (simulated from backup) completes
  successfully and produces a consistent dataset, verified at least monthly.
- **SC-004**: The application starts and core features remain available within
  60 seconds of the queue service recovering from an outage.
- **SC-005**: An operator can trace any production container image to a
  specific source commit using the image tag alone.
- **SC-006**: No secret values are present in any committed file, CI artefact,
  or client-side response, as verified by automated and manual inspection.
- **SC-007**: 100% of log entries from all services contain the required
  structured fields and contain no sensitive data, as verified by log sampling.

---

## Assumptions

- Operators are developers or DevOps engineers with access to the repository
  and deployment infrastructure; end-users (children) never interact with
  deployment tooling.
- The deployment environment supports environment variable injection at
  container runtime.
- A TLS certificate authority compatible with automated renewal is available
  (e.g., Let's Encrypt or equivalent).
- Object storage is an external managed service; the application does not
  manage storage infrastructure directly.
- CI infrastructure has access to Docker for building and running integration
  tests.
- A single staging environment that mirrors production is available for
  pre-release verification.
- Redis data loss (RDB snapshots) is tolerable for cache and queue data because
  pending jobs are reconstructable from durable storage.
