<!--
SYNC IMPACT REPORT
==================
Version change: [TEMPLATE] → 1.0.0
Ratified: 2026-08-07
Last Amended: 2026-08-07

Modified principles:
  All placeholder tokens replaced on initial population from
  initial_spec/speckit_constitution.md.

Added sections (beyond template defaults):
  Core Principles expanded to 23 named principles (template defaulted to 5).
  § Definition of Done (with 7 subsections).
  § Non-Negotiable Rules (absolute prohibitions list).

Removed sections:
  None.

Templates reviewed:
  ✅ .specify/templates/plan-template.md — Constitution Check gate present; no updates required.
  ✅ .specify/templates/spec-template.md — Sections compatible; no updates required.
  ✅ .specify/templates/tasks-template.md — Task categories compatible; no updates required.

Deferred TODOs:
  None — all fields resolved from source document and project context.
-->

# Math Racers Constitution

## Core Principles

### I. Purpose

This Constitution defines the immutable engineering principles governing the
implementation of **Math Racers**. Its purpose is to ensure that all
implementation decisions remain consistent throughout the lifetime of the
project.

This document does **not** describe gameplay, user experience, artwork or
progression systems. Those topics are defined by dedicated project
documentation. Every contributor, human or AI, MUST follow this Constitution.

### II. Source of Truth

Project documentation is authoritative. Documents have the following
precedence (higher number = lower authority):

1. Constitution
2. Architecture Decision Records (ADR)
3. Game Design Document (GDD)
4. Art Bible
5. Prompt Bible
6. Game Economy & Progression Specification

Lower-priority documents MUST NOT contradict higher-priority documents. If a
contradiction is discovered, implementation MUST follow the higher-priority
document. No implementation may redefine architectural or gameplay decisions
already documented.

The `docs/` directory contains the derived, structured documentation hierarchy
organised per the Spec Kit hierarchy:

```
Vision (docs/vision.md)
       ↓
Product Requirements Document (docs/prd.md)
       ↓
Epics (docs/*/epic.md)
       ↓
Features (docs/*/feature-*.md)
       ↓
Specifications (docs/*/spec-*.md)
```

In any conflict between a `docs/` file and a source document in the priority
list above, the source document takes precedence.

### III. Project Vision

Math Racers is a premium educational web application that teaches mathematics
through short, engaging racing gameplay.

The project prioritises (in order):

- educational value;
- child-friendly experience;
- maintainability;
- deterministic behaviour;
- long-term extensibility.

Technology exists to support learning. Learning MUST NOT be compromised for
technical convenience.

### IV. Architecture

The architecture defined by the ADRs is mandatory. Implementation MUST NOT
introduce architectural changes unless the ADRs are updated first.

The project SHALL:

- remain a modular monolith;
- separate domain logic from infrastructure;
- maintain clear module boundaries;
- avoid circular dependencies;
- minimise coupling;
- maximise cohesion.

Business logic MUST remain independent of frameworks wherever practical.

### V. Documentation First

Implementation follows documentation. Documentation does NOT follow
implementation.

Before implementing any feature, the implementation MUST identify the relevant
documentation in `docs/`, organised by epic.

If documentation is incomplete, the implementation SHOULD request documentation
updates rather than invent behaviour. No undocumented architectural decisions
may be introduced.

### VI. Simplicity

Prefer the simplest correct solution.

Avoid:

- premature optimisation;
- unnecessary abstractions;
- speculative architecture;
- over-engineering.

Every abstraction MUST solve an existing problem.

### VII. Code Quality

Production-quality code is required. Code MUST be:

- readable;
- deterministic;
- testable;
- maintainable;
- explicit;
- consistently formatted.

Small, focused modules are preferred over large multi-purpose components.
Magic values MUST be replaced with named constants where appropriate.

### VIII. Consistency

The existing project conventions are authoritative. New implementations MUST
match:

- project structure;
- naming conventions;
- dependency patterns;
- coding style;
- testing style.

Consistency is preferred over personal preference.

### IX. Backend Principles

The backend owns:

- persistence;
- authentication;
- authorisation;
- AI orchestration;
- statistics;
- progression;
- asset management;
- REST APIs.

The backend does **not** own gameplay simulation. Business logic MUST NOT be
placed inside controllers.

### X. Frontend Principles

The frontend owns:

- rendering;
- user interaction;
- animations;
- race simulation;
- mathematics presentation;
- accessibility.

Frontend components SHOULD remain reusable and composable. Rendering logic and
application logic MUST remain separated.

### XI. Gameplay

Gameplay MUST follow the Game Design Document. Implementation MUST NOT change:

- race mechanics;
- progression;
- educational behaviour;
- balancing;
- adaptive difficulty.

Gameplay changes require documentation changes before implementation.

### XII. Artificial Intelligence

All AI interactions MUST be deterministic and versioned. AI providers are
infrastructure; application logic MUST remain provider-independent.

Prompt generation MUST occur exclusively through the Prompt Builder. The
frontend MUST NOT construct prompts directly. Prompts MUST NOT be hard-coded
throughout the application.

### XIII. Image Generation

Image generation follows the Art Bible and Prompt Bible. Every generated asset
MUST be reproducible from structured metadata. Images MUST satisfy the
project's visual consistency requirements. Manual prompt writing inside
application code is prohibited.

### XIV. Data Ownership

Persistent data belongs to the backend. The frontend MAY cache data but is
NEVER the source of truth. Database schemas MUST evolve through migrations.
Breaking schema changes require explicit migration strategies.

### XV. Security

Security is mandatory. Implementation MUST include:

- input validation;
- authentication;
- authorisation;
- secure secret management;
- dependency maintenance;
- least-privilege principles.

Sensitive information MUST NOT be exposed to the client.

### XVI. Performance

Optimisation follows measurement. Readability is preferred over
micro-optimisation. Performance improvements SHOULD preserve maintainability.
The application MUST remain responsive on typical consumer hardware.

### XVII. Accessibility

Accessibility is a functional requirement. The application MUST support:

- keyboard navigation;
- visible focus states;
- semantic markup;
- scalable typography;
- reduced motion preferences;
- colour accessibility.

Accessibility MUST be considered during implementation rather than added later.

### XVIII. Testing

Every feature MUST include automated tests appropriate to its scope. Testing
SHOULD prioritise observable behaviour over implementation details. External
services SHOULD be mocked where appropriate. Regression tests MUST accompany
bug fixes. Code without appropriate tests MUST NOT be considered complete.

### XIX. Dependencies

Dependencies are introduced only when they provide clear long-term value.
Before adding a dependency, implementation MUST consider:

- existing project capabilities;
- maintenance burden;
- security;
- community maturity;
- architectural impact.

Unnecessary libraries MUST be avoided.

### XX. Documentation Maintenance

Documentation is part of the implementation. Whenever public behaviour changes,
relevant documentation MUST be updated. Documentation MUST remain concise,
accurate and synchronised with the codebase. When a feature specification in
`docs/` is affected by a change, that file MUST be updated as part of the same
implementation task. Duplicating information across multiple documents MUST be
avoided.

### XXI. Logging and Observability

Logs MUST be structured and meaningful. Logging SHOULD assist debugging without
exposing sensitive information. Errors MUST provide actionable diagnostics
while remaining safe for production.

### XXII. Versioning

All externally visible contracts MUST be versioned where appropriate. This
includes:

- APIs;
- prompts;
- generated assets;
- database migrations.

Version history MUST remain reproducible.

### XXIII. AI-Assisted Development

AI is an implementation assistant. AI MUST NOT:

- redesign architecture;
- invent undocumented requirements;
- replace project documentation;
- ignore ADRs;
- generate placeholder implementations presented as complete solutions.

AI MUST implement documented behaviour faithfully.

## Definition of Done

A feature is complete only when **all** of the following conditions are
satisfied.

### Compliance

- Conforms to the Constitution.
- Follows all relevant ADRs.
- Satisfies the GDD.
- Complies with the Art Bible where applicable.
- Complies with the Prompt Bible where applicable.
- Respects the Game Economy specification where applicable.

### Quality Gates

- Automated tests pass (unit, integration, and relevant E2E).
- Static analysis passes with no suppressions introduced.
- Formatting passes.
- No known regressions remain.

### Documentation

- Documentation updated where public behaviour has changed.
- The relevant Feature or Specification document in `docs/` reflects the
  implemented behaviour.
- Any ADR affected by the change has been reviewed and updated if necessary.

### Specification Completeness

Every Feature specification MUST include, before implementation begins:

- **Acceptance criteria** — a verifiable checklist of observable outcomes (not
  implementation details).
- **Edge cases** — documented scenarios for boundary inputs, failure modes, and
  unexpected states.
- **Manual verification steps** — a step-by-step procedure a human tester can
  follow to confirm the feature works end-to-end.

A feature whose specification is missing any of these three sections is NOT
considered ready for implementation.

### Art and Prompt Compliance

If the feature generates or displays visual assets:

- Every generated asset satisfies the Art Bible quality gates (technical,
  artistic, content safety).
- Every prompt was constructed by the Prompt Builder — no manually authored
  prompts in application code.
- The generation record stores `prompt_version`, `model_version`, and
  `timestamp`.

### Accessibility Gates

- All interactive elements are keyboard-navigable.
- All images have meaningful alt text or are marked as decorative.
- Colour contrast meets the minimum 4.5:1 ratio for text.
- `prefers-reduced-motion` is respected.

### Child Safety

- No technical error messages are visible to children.
- No user-supplied content reaches a generation API without sanitisation.
- Privacy requirements (data minimisation, parental controls) are satisfied.

## Non-Negotiable Rules

The following rules are absolute:

- Do NOT contradict project documentation.
- Do NOT introduce undocumented architecture.
- Do NOT hard-code AI prompts.
- Do NOT bypass the Prompt Builder.
- Do NOT place business logic in controllers.
- Do NOT duplicate business logic across frontend and backend.
- Do NOT introduce unnecessary dependencies.
- Do NOT commit unfinished placeholder implementations.
- Do NOT weaken test coverage.
- Do NOT sacrifice maintainability for short-term convenience.

## Governance

This Constitution supersedes all other practices and guidelines within the
Math Racers project.

**Amendment procedure**: Any amendment requires (1) a documented rationale,
(2) a version increment per semantic versioning rules (MAJOR for
backward-incompatible governance changes; MINOR for new sections or material
expansions; PATCH for clarifications and wording fixes), and (3) propagation
of changes to all affected templates and documentation.

**Versioning policy**: `CONSTITUTION_VERSION` uses semantic versioning.
Amendments are recorded in the Sync Impact Report embedded as an HTML comment
at the top of this file.

**Compliance review**: All implementation tasks MUST pass the Constitution
Check gate in the plan before Phase 0 research begins, and MUST be re-checked
after Phase 1 design.

**Guiding principle**: Every implementation decision should support the
objective: *Build a maintainable, deterministic, child-friendly educational
game whose implementation faithfully reflects the documented architecture,
gameplay and artistic vision while remaining simple, extensible and
production-ready.*

**Version**: 1.0.0 | **Ratified**: 2026-08-07 | **Last Amended**: 2026-08-07
