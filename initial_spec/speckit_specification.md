# Math Racers — Specification

Version: 1.0

Status: Authoritative

---

# Part I — Project Specification & Implementation Strategy

---

# 1. Purpose

This specification defines **how the Math Racers project shall be implemented**.

Unlike the Game Design Document, this document does not describe gameplay mechanics or user experience.

Instead, it defines:

- implementation strategy;
- project organisation;
- execution order;
- engineering workflow;
- implementation constraints;
- acceptance criteria.

This specification is intended to be consumed by both human developers and AI-assisted development tools such as Claude Code.

---

# 2. Scope

This specification covers:

- project implementation;
- backend development;
- frontend development;
- AI integration;
- infrastructure;
- testing;
- deployment preparation.

It does **not** redefine:

- gameplay;
- balancing;
- artwork;
- prompt templates;
- architecture.

Those subjects already exist in dedicated project documentation.

---

# 3. Existing Documentation

The following documentation already exists.

It MUST NOT be recreated.

It MUST NOT be duplicated.

Implementation shall reference these documents instead.

| Document | Purpose |
|-----------|---------|
| Constitution | Engineering principles |
| Game Design Document | Gameplay specification |
| Architecture Decision Records | Technical architecture |
| Art Bible | Visual language |
| Prompt Bible | AI prompt templates |
| Game Economy & Progression | Balancing and progression |

If implementation requires information from these documents, they should be consulted directly.

---

# 4. Documentation Priority

If multiple documents appear to conflict, the following order is authoritative.

1. Constitution
2. Architecture Decision Records
3. Game Design Document
4. Art Bible
5. Prompt Bible
6. Game Economy & Progression

No implementation may violate a higher-priority document.

---

# 5. Implementation Philosophy

The project shall be implemented incrementally.

Each implementation step should:

- solve one clearly defined problem;
- remain independently reviewable;
- be testable;
- be deployable in isolation where practical.

Large implementation tasks should be decomposed into smaller independent units.

---

# 6. Increment Size

Each development task should ideally fit into a single development session.

Recommended duration:

30–90 minutes.

Typical task examples:

- implement Avatar Repository;
- implement Statistics API;
- implement Login Screen;
- implement Race Track component;
- implement Prompt Builder.

Tasks should avoid spanning multiple unrelated modules.

---

# 7. Repository Structure

The repository structure is defined by the ADRs.

This specification does not redefine directory layout.

Implementation must follow the documented repository organisation exactly.

No additional architectural layers should be introduced without updating the ADRs.

---

# 8. Development Workflow

Every implementation task follows the same lifecycle.

```
Read Documentation
        ↓
Understand Constraints
        ↓
Plan Implementation
        ↓
Implement Feature
        ↓
Write Tests
        ↓
Run Quality Checks
        ↓
Update Documentation (if required)
        ↓
Commit
```

Skipping steps is discouraged.

---

# 9. Reading Documentation

Before implementing any feature, identify all relevant documentation.

Typical examples:

Avatar generation

↓

Art Bible

↓

Prompt Bible

↓

AI ADR

Statistics

↓

Game Economy

↓

Backend ADR

↓

Frontend ADR

Race mechanics

↓

GDD

↓

Frontend ADR

↓

Progression

Implementation should never rely solely on assumptions.

---

# 10. Feature Boundaries

Every feature should have:

- one responsibility;
- one public purpose;
- minimal dependencies;
- clearly defined interfaces.

Features should remain independently understandable.

---

# 11. Change Scope

During implementation:

Modify only the code necessary to complete the requested feature.

Avoid unrelated refactoring.

Avoid stylistic rewrites.

Avoid architectural redesign.

---

# 12. Architectural Compliance

Implementation must follow every relevant ADR.

If implementation appears to require architectural changes:

Stop.

Update the ADR first.

Only after the architecture has been approved should implementation continue.

---

# 13. Source of Behaviour

Behaviour originates from documentation.

Never from implementation.

Examples:

Race rules

→ GDD

Adaptive difficulty

→ Game Economy

Prompt construction

→ Prompt Bible

Avatar appearance

→ Art Bible

Implementation simply realises documented behaviour.

---

# 14. Build Order

The project shall be implemented in the following order.

Phase 1

Infrastructure

Phase 2

Backend Foundation

Phase 3

Frontend Foundation

Phase 4

AI Integration

Phase 5

Gameplay

Phase 6

Integration

Phase 7

Quality

Each phase depends on the previous phase.

---

# 15. Commit Strategy

Every completed feature should produce one logical commit.

Examples:

```
feat(authentication)

feat(avatar-service)

feat(prompt-builder)

feat(race-engine)

feat(statistics)

fix(adaptive-difficulty)

refactor(api-client)

docs(prompt-bible)
```

Large commits should be avoided.

---

# 16. Branch Strategy

Recommended workflow:

```
main

↓

feature branch

↓

review

↓

merge

↓

delete feature branch
```

Development should remain linear and predictable.

---

# 17. Code Reviews

Every completed feature should be reviewed before merging.

Review priorities:

1. Correctness
2. Architecture
3. Maintainability
4. Readability
5. Performance
6. Security

Minor stylistic differences should not block progress.

---

# 18. AI-Assisted Development

Claude Code should be treated as an implementation engineer.

Before writing code it should:

- identify affected modules;
- identify relevant ADRs;
- summarise implementation constraints;
- implement only the requested feature.

Claude Code should never redesign documented systems.

---

# 19. Quality Gates

Every feature must satisfy:

- builds successfully;
- passes tests;
- passes linting;
- passes formatting;
- passes static analysis;
- satisfies documentation requirements.

Quality gates are mandatory.


# 21. Phase 1 — Infrastructure

Infrastructure establishes the foundation of the project.

This phase contains no business logic.

Objectives:

- repository configuration;
- development environment;
- build system;
- dependency management;
- Docker environment;
- CI/CD pipeline;
- code quality tooling;
- project documentation.

Completion Criteria:

- project builds successfully;
- local development environment is reproducible;
- CI pipeline executes successfully.

---

# 22. Backend Foundation

The backend shall be implemented according to the Backend ADR.

Implementation includes:

- application bootstrap;
- configuration system;
- dependency injection;
- database connectivity;
- logging;
- health endpoints;
- error handling;
- API versioning.

Business modules are intentionally excluded from this phase.

---

# 23. Configuration

Configuration must be environment-driven.

Requirements:

- deterministic startup;
- typed configuration;
- environment isolation;
- no hard-coded secrets.

Configuration should remain independent of deployment platform.

---

# 24. Database Foundation

Database implementation follows the Database ADR.

Implementation includes:

- migration framework;
- schema management;
- UUID identifiers;
- timestamps;
- foreign keys;
- indexes.

Schema design must prioritise clarity over optimisation.

---

# 25. Authentication

Authentication should be implemented before user-facing functionality.

Responsibilities include:

- user registration;
- login;
- session management;
- token validation;
- protected endpoints.

Authentication must remain isolated from business modules.

---

# 26. Authorisation

Permissions should be explicit.

Authorisation decisions belong in the backend.

Frontend visibility does not constitute security.

---

# 27. Core Domain Modules

Core backend modules include:

- Users
- Avatars
- Assets
- Statistics
- Progression
- Achievements
- AI
- Mathematics
- Configuration

Each module should expose a minimal public API.

Internal implementation details must remain private.

---

# 28. Avatar Module

Responsibilities:

- avatar persistence;
- metadata validation;
- favourite avatar management;
- avatar retrieval;
- avatar lifecycle.

Image generation is not performed directly by this module.

---

# 29. Statistics Module

Responsibilities:

- race history;
- accuracy;
- response times;
- streaks;
- player statistics;
- avatar statistics.

Statistics are append-only where practical.

Historical records should remain reproducible.

---

# 30. Progression Module

Responsibilities:

- XP calculation;
- level calculation;
- achievement unlocking;
- daily streaks.

All progression formulas are defined in the Game Economy document.

The implementation must not introduce alternative formulas.

---

# 31. Mathematics Module

Responsibilities:

- generate exercises;
- validate answers;
- determine difficulty tier;
- support adaptive difficulty.

Generation rules originate from the Game Economy specification.

---

# 32. AI Module

Responsibilities:

- prompt generation;
- provider abstraction;
- image requests;
- LLM requests;
- metadata persistence;
- retry handling.

The AI module must not contain business logic unrelated to AI orchestration.

---

# 33. Prompt Builder

Prompt Builder is the only component allowed to generate prompts.

Inputs:

- structured metadata.

Outputs:

- GPT Image prompts;
- LLM prompts.

Prompt templates originate exclusively from the Prompt Bible.

No other module should construct prompts.

---

# 34. Asset Module

Responsibilities:

- generated image metadata;
- asset storage;
- version tracking;
- retrieval;
- lifecycle management.

Generated assets should remain immutable.

---

# 35. Background Jobs

Long-running operations should execute asynchronously.

Examples:

- avatar generation;
- image generation;
- future batch processing.

Background jobs should be retryable and idempotent.

---

# 36. REST API

The backend exposes REST endpoints only.

Requirements:

- predictable resource naming;
- request validation;
- consistent responses;
- structured errors;
- versioned endpoints.

REST endpoints should never expose internal implementation details.

---

# 37. Validation

All external input must be validated.

Validation occurs before business logic executes.

Invalid requests should fail early with consistent error responses.

---

# 38. Error Handling

Errors should be:

- predictable;
- structured;
- actionable;
- safe.

Internal implementation details must never be exposed to clients.

---

# 39. Logging

Logging should support:

- debugging;
- monitoring;
- auditing.

Logs must never contain:

- secrets;
- authentication tokens;
- sensitive user information.

---

# 40. Testing Strategy

Every backend module requires automated tests.

Recommended coverage includes:

- unit tests;
- integration tests;
- API tests;
- regression tests.

Tests should validate observable behaviour.

---

# 41. Performance

Optimisation should follow measurement.

Priority order:

1. correctness;
2. readability;
3. maintainability;
4. performance.

Caching should be introduced only when justified.

---

# 42. Security

Security review is required before completion.

Review should verify:

- authentication;
- authorisation;
- validation;
- dependency security;
- secret handling;
- API exposure.

Security findings should be resolved before release.

---

# 43. Completion Criteria

Backend implementation is complete when:

- all documented modules exist;
- APIs satisfy the ADRs;
- tests pass;
- documentation remains accurate;
- quality gates succeed.


# 45. Phase 3 — Frontend Foundation

The frontend provides the complete user experience of Math Racers.

It is responsible for:

- rendering;
- interaction;
- animation;
- gameplay;
- accessibility;
- responsive behaviour.

The frontend must remain independent from backend implementation details.

---

# 46. Design System

The Design System shall be implemented before application pages.

The implementation must follow the Art Bible.

The Design System includes:

- colours;
- typography;
- spacing;
- buttons;
- cards;
- dialogs;
- icons;
- form controls;
- animations;
- layout primitives.

Every screen should be composed from reusable components.

---

# 47. Application Layout

The application layout should provide:

- consistent navigation;
- responsive structure;
- predictable page transitions;
- shared visual hierarchy.

Layouts should minimise duplicated code.

---

# 48. Routing

Routing should follow application structure rather than implementation details.

Pages should remain independently navigable.

Routing logic must remain separate from business logic.

---

# 49. Application State

State should remain local whenever practical.

Global state should be introduced only for data shared across multiple application areas.

Derived state should not be duplicated.

---

# 50. API Integration

Frontend communicates exclusively through documented REST APIs.

Requirements:

- typed client;
- centralised request handling;
- consistent error processing;
- retry strategy where appropriate.

Application code should not construct HTTP requests directly.

---

# 51. Asset Loading

Static assets should be loaded efficiently.

Generated assets should be cached.

Missing assets should degrade gracefully without breaking gameplay.

---

# 52. Pages

Version 1.0 includes the following pages.

- Home
- Avatar Gallery
- Avatar Creator
- Race Setup
- Race
- Statistics
- Achievements
- Settings

Each page should have a single primary responsibility.

---

# 53. Avatar Gallery

Responsibilities:

- list available avatars;
- display favourite avatar;
- avatar selection;
- avatar statistics.

Avatar editing belongs to the Avatar Creator.

---

# 54. Avatar Creator

Responsibilities:

- collect avatar configuration;
- submit structured metadata;
- display generation progress;
- display generated avatar.

Prompt creation must never occur in the frontend.

---

# 55. Race Setup

Responsibilities:

- select participants;
- select mathematics tier;
- configure race options;
- start race.

Game configuration should remain independent from gameplay.

---

# 56. Race Screen

The Race Screen is the primary gameplay interface.

Responsibilities:

- render runners;
- display mathematical challenges;
- animate progress;
- display race status;
- display finishing order.

The interface must remain visually focused on the educational task.

---

# 57. Gameplay Engine

Gameplay simulation belongs entirely to the frontend.

Responsibilities include:

- race progression;
- runner movement;
- obstacle timing;
- animation sequencing;
- finish detection.

Gameplay simulation should not require continuous backend communication.

---

# 58. Mathematics Presentation

Mathematical exercises should:

- be immediately readable;
- minimise visual distractions;
- support keyboard input;
- provide immediate feedback.

Exercise generation follows backend-provided data.

---

# 59. Animation

Animations should follow the Art Bible.

Animation principles:

- communicate interaction;
- reinforce feedback;
- improve readability;
- never delay gameplay.

Animation should enhance, not dominate, the experience.

---

# 60. Responsive Behaviour

The application should support:

- desktop;
- laptop;
- tablet;
- large mobile devices.

Responsive behaviour should preserve functionality rather than redesign interaction.

---

# 61. Accessibility

Accessibility requirements are mandatory.

Implementation should support:

- keyboard navigation;
- semantic HTML;
- focus management;
- screen readers;
- scalable text;
- reduced motion preferences.

Accessibility should be validated continuously.

---

# 62. Error Handling

Frontend errors should be:

- understandable;
- recoverable;
- user-friendly.

Technical terminology should remain hidden from players.

---

# 63. Offline Behaviour

Temporary network failures should not immediately terminate gameplay.

Where practical:

- preserve local state;
- retry failed requests;
- synchronise when connectivity returns.

Graceful degradation is preferred over interruption.

---

# 64. Performance

Frontend performance goals:

- responsive interactions;
- smooth animations;
- minimal unnecessary rendering;
- efficient asset loading.

Optimisation should preserve readability.

---

# 65. Frontend Testing

Testing should include:

- component tests;
- integration tests;
- gameplay behaviour;
- accessibility verification.

Critical gameplay behaviour should be covered by automated tests.

---

# 66. UI Consistency

Every implemented screen should comply with:

- Art Bible;
- Design System;
- navigation conventions;
- interaction patterns.

New UI patterns should not be introduced without updating the Art Bible.

---

# 67. Gameplay Integrity

Frontend implementation must not modify gameplay rules defined by:

- Game Design Document;
- Game Economy & Progression.

Rendering may change.

Game rules may not.

---

# 68. Completion Criteria

Frontend implementation is complete when:

- all pages are implemented;
- gameplay functions correctly;
- accessibility requirements are met;
- responsive behaviour is verified;
- automated tests pass;
- implementation follows the Art Bible.


# 70. Phase 6 — System Integration

System integration combines independently implemented modules into a single application.

Integration should occur only after:

- infrastructure is stable;
- backend modules are complete;
- frontend modules are complete;
- AI services are operational.

Integration should not introduce new functionality.

Its purpose is verification.

---

# 71. Integration Strategy

Integrate modules incrementally.

Recommended order:

```
Database
        ↓
Backend Modules
        ↓
REST API
        ↓
Frontend API Client
        ↓
AI Services
        ↓
Gameplay
        ↓
Statistics
        ↓
Progression
```

Each integration step should be validated before continuing.

---

# 72. API Compatibility

Frontend and backend communicate exclusively through documented REST contracts.

Requirements:

- stable request models;
- stable response models;
- explicit versioning;
- backward-compatible changes where practical.

Contract changes should be implemented simultaneously across both applications.

---

# 73. AI Integration

AI services are infrastructure components.

Integration should verify:

- Prompt Builder output;
- provider abstraction;
- asynchronous processing;
- metadata persistence;
- generated asset retrieval;
- retry behaviour.

Frontend should interact only with backend APIs.

---

# 74. Asset Pipeline

The complete asset lifecycle is:

```
Structured Metadata
        ↓
Prompt Builder
        ↓
AI Provider
        ↓
Validation
        ↓
Storage
        ↓
Frontend Delivery
```

Every generated asset should remain reproducible.

---

# 75. Data Consistency

The backend is the single source of truth.

Frontend state should synchronise with backend state.

Data duplication should be avoided unless required for performance.

---

# 76. End-to-End Workflows

The following user journeys should be fully functional:

- create account;
- create avatar;
- generate avatar artwork;
- select favourite avatar;
- configure race;
- complete race;
- update statistics;
- award achievements;
- update progression.

These workflows represent the minimum viable product.

---

# 77. Automated Testing

Automated testing is mandatory.

The project should include:

- unit tests;
- integration tests;
- end-to-end tests.

Tests should be deterministic and executable in CI.

---

# 78. Test Priorities

Testing priority:

1. Domain logic
2. API behaviour
3. Gameplay behaviour
4. AI integration
5. User interface
6. Visual regression (future)

Critical educational functionality should receive the highest test coverage.

---

# 79. Static Analysis

Every change should pass:

- formatter;
- linter;
- type checker;
- static analysis tools.

Warnings should be resolved rather than ignored.

---

# 80. Continuous Integration

Every commit should automatically execute:

- dependency installation;
- project build;
- formatting checks;
- linting;
- static analysis;
- automated tests.

A failing pipeline blocks integration.

---

# 81. Continuous Delivery

Deployment should use reproducible artefacts.

Release builds should originate from the default branch after passing all quality gates.

Manual production changes should be avoided.

---

# 82. Observability

The application should provide sufficient observability for production support.

Recommended capabilities:

- structured logs;
- health endpoints;
- metrics;
- error reporting.

Monitoring should assist diagnosis without exposing sensitive information.

---

# 83. Performance Verification

Before release, verify:

- application startup;
- page responsiveness;
- race animation smoothness;
- API responsiveness;
- asset loading;
- memory stability.

Optimisation should be driven by measurement.

---

# 84. Security Verification

Before release, perform a security review covering:

- authentication;
- authorisation;
- input validation;
- dependency vulnerabilities;
- secret management;
- API exposure;
- AI integration.

Critical findings must be resolved before release.

---

# 85. Accessibility Verification

Before release, verify compliance with the accessibility requirements defined in the Constitution and Art Bible.

Review should include:

- keyboard navigation;
- focus visibility;
- semantic structure;
- reduced motion;
- scalable text;
- colour accessibility.

Accessibility regressions should be treated as defects.

---

# 86. Documentation Verification

Before release, confirm that:

- implementation matches documentation;
- documentation reflects implementation;
- obsolete documentation has been removed;
- public APIs are documented.

Documentation is part of the release deliverable.

---

# 87. Release Candidate

A Release Candidate may be created when:

- all planned features are complete;
- all critical defects are resolved;
- automated tests pass;
- documentation is complete;
- quality gates succeed.

Feature development should stop once a Release Candidate is created.

Only fixes are permitted afterwards.

---

# 88. Production Readiness Review

The final review should evaluate:

- architecture compliance;
- gameplay compliance;
- visual consistency;
- code quality;
- testing;
- security;
- accessibility;
- performance;
- documentation;
- deployment readiness.

Each finding should be classified as:

- Critical
- High
- Medium
- Low

Critical findings block release.

---

# 89. Definition of Done

A feature is considered complete only if:

- implementation follows the Constitution;
- relevant ADRs are respected;
- behaviour matches the Game Design Document;
- visuals comply with the Art Bible;
- AI integrations use the Prompt Bible;
- progression follows the Game Economy specification;
- automated tests pass;
- quality gates succeed;
- documentation is updated where required;
- implementation is production-ready.

Incomplete or placeholder implementations do not satisfy the Definition of Done.

---

# 90. Project Completion

Version 1.0 is considered complete when:

- all documented functionality has been implemented;
- all acceptance criteria have been satisfied;
- documentation and implementation are fully aligned;
- the application is stable, maintainable and deployable.

Future development should extend the project through updated documentation before implementation begins.

---

# Appendix A — Implementation Principles

Every implementation should consistently follow these principles:

- Documentation before implementation.
- Architecture before optimisation.
- Simplicity before abstraction.
- Readability before cleverness.
- Composition before inheritance.
- Determinism before convenience.
- Testing before release.
- Accessibility by default.
- Security by design.
- AI as an implementation tool, never as a source of truth.

---

# Appendix B — Acceptance Checklist

Every completed feature should satisfy the following checklist:

- [ ] Relevant documentation identified.
- [ ] Constitution respected.
- [ ] Applicable ADRs followed.
- [ ] Business logic implemented correctly.
- [ ] Public APIs documented.
- [ ] Automated tests added.
- [ ] Existing tests pass.
- [ ] Formatting passes.
- [ ] Linting passes.
- [ ] Static analysis passes.
- [ ] No unnecessary dependencies introduced.
- [ ] No architectural violations introduced.
- [ ] Documentation updated where necessary.
- [ ] Feature reviewed.
- [ ] Ready for production.

---

# End of Specification

This Specification defines the implementation process for Math Racers.

Together with the Constitution and the existing project documentation (Game Design Document, Architecture Decision Records, Art Bible, Prompt Bible and Game Economy & Progression Specification), it forms the complete implementation framework for the project.

No additional architectural or design documents are required for Version 1.0.
