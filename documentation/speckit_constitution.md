# Math Racers — Constitution

Version: 1.0

Status: Authoritative

---

# 1. Purpose

This Constitution defines the immutable engineering principles governing the implementation of **Math Racers**.

Its purpose is to ensure that all implementation decisions remain consistent throughout the lifetime of the project.

This document does **not** describe gameplay, user experience, artwork or progression systems. Those topics are defined by dedicated project documentation.

Every contributor, human or AI, must follow this Constitution.

---

# 2. Source of Truth

The project documentation is authoritative.

Documents have the following precedence.

1. Constitution
2. Architecture Decision Records (ADR)
3. Game Design Document (GDD)
4. Art Bible
5. Prompt Bible
6. Game Economy & Progression Specification

Lower-priority documents must never contradict higher-priority documents.

If a contradiction is discovered, implementation must follow the higher-priority document.

No implementation may redefine architectural or gameplay decisions already documented.

---

# 3. Project Vision

Math Racers is a premium educational web application that teaches mathematics through short, engaging racing gameplay.

The project prioritises:

- educational value;
- child-friendly experience;
- maintainability;
- deterministic behaviour;
- long-term extensibility.

Technology exists to support learning.

Learning is never compromised for technical convenience.

---

# 4. Architecture Principles

The architecture defined by the ADRs is mandatory.

Implementation must not introduce architectural changes unless the ADRs are updated first.

The project shall:

- remain a modular monolith;
- separate domain logic from infrastructure;
- maintain clear module boundaries;
- avoid circular dependencies;
- minimise coupling;
- maximise cohesion.

Business logic must remain independent of frameworks wherever practical.

---

# 5. Documentation First

Implementation follows documentation.

Documentation does not follow implementation.

Before implementing any feature, the implementation must identify the relevant documentation.

If documentation is incomplete, the implementation should request documentation updates rather than invent behaviour.

No undocumented architectural decisions may be introduced.

---

# 6. Simplicity

Prefer the simplest correct solution.

Avoid:

- premature optimisation;
- unnecessary abstractions;
- speculative architecture;
- over-engineering.

Every abstraction must solve an existing problem.

---

# 7. Code Quality

Production-quality code is required.

Code should be:

- readable;
- deterministic;
- testable;
- maintainable;
- explicit;
- consistently formatted.

Small, focused modules are preferred over large multi-purpose components.

Magic values should be replaced with named constants where appropriate.

---

# 8. Consistency

The existing project conventions are authoritative.

New implementations should match:

- project structure;
- naming conventions;
- dependency patterns;
- coding style;
- testing style.

Consistency is preferred over personal preference.

---

# 9. Backend Principles

The backend owns:

- persistence;
- authentication;
- authorisation;
- AI orchestration;
- statistics;
- progression;
- asset management;
- REST APIs.

The backend does **not** own gameplay simulation.

Business logic must never be placed inside controllers.

---

# 10. Frontend Principles

The frontend owns:

- rendering;
- user interaction;
- animations;
- race simulation;
- mathematics presentation;
- accessibility.

Frontend components should remain reusable and composable.

Rendering logic and application logic should remain separated.

---

# 11. Gameplay

Gameplay must follow the Game Design Document.

Implementation must not change:

- race mechanics;
- progression;
- educational behaviour;
- balancing;
- adaptive difficulty.

Gameplay changes require documentation changes before implementation.

---

# 12. Artificial Intelligence

All AI interactions must be deterministic and versioned.

AI providers are infrastructure.

Application logic must remain provider-independent.

Prompt generation must occur exclusively through the Prompt Builder.

The frontend must never construct prompts directly.

Prompts must never be hard-coded throughout the application.

---

# 13. Image Generation

Image generation follows the Art Bible and Prompt Bible.

Every generated asset must be reproducible from structured metadata.

Images must satisfy the project's visual consistency requirements.

Manual prompt writing inside application code is prohibited.

---

# 14. Data Ownership

Persistent data belongs to the backend.

The frontend may cache data but is never the source of truth.

Database schemas must evolve through migrations.

Breaking schema changes require explicit migration strategies.

---

# 15. Security

Security is mandatory.

Implementation must include:

- input validation;
- authentication;
- authorisation;
- secure secret management;
- dependency maintenance;
- least-privilege principles.

Sensitive information must never be exposed to the client.

---

# 16. Performance

Optimisation follows measurement.

Readability is preferred over micro-optimisation.

Performance improvements should preserve maintainability.

The application should remain responsive on typical consumer hardware.

---

# 17. Accessibility

Accessibility is a functional requirement.

The application should support:

- keyboard navigation;
- visible focus states;
- semantic markup;
- scalable typography;
- reduced motion preferences;
- colour accessibility.

Accessibility should be considered during implementation rather than added later.

---

# 18. Testing

Every feature must include automated tests appropriate to its scope.

Testing should prioritise observable behaviour over implementation details.

External services should be mocked where appropriate.

Regression tests must accompany bug fixes.

Code without appropriate tests should not be considered complete.

---

# 19. Dependencies

Dependencies are introduced only when they provide clear long-term value.

Before adding a dependency, implementation should consider:

- existing project capabilities;
- maintenance burden;
- security;
- community maturity;
- architectural impact.

Avoid unnecessary libraries.

---

# 20. Documentation

Documentation is part of the implementation.

Whenever public behaviour changes, relevant documentation should be updated.

Documentation should remain concise, accurate and synchronised with the codebase.

Duplicating information across multiple documents should be avoided.

---

# 21. Logging and Observability

Logs should be structured and meaningful.

Logging should assist debugging without exposing sensitive information.

Errors should provide actionable diagnostics while remaining safe for production.

---

# 22. Versioning

All externally visible contracts should be versioned where appropriate.

This includes:

- APIs;
- prompts;
- generated assets;
- database migrations.

Version history should remain reproducible.

---

# 23. AI-Assisted Development

AI is an implementation assistant.

AI must not:

- redesign architecture;
- invent undocumented requirements;
- replace project documentation;
- ignore ADRs;
- generate placeholder implementations presented as complete solutions.

AI should implement documented behaviour faithfully.

---

# 24. Definition of Done

A feature is complete only when **all** of the following conditions are satisfied:

## 24.1 Compliance

- it conforms to the Constitution;
- it follows all relevant ADRs;
- it satisfies the GDD;
- it complies with the Art Bible where applicable;
- it complies with the Prompt Bible where applicable;
- it respects the Game Economy specification where applicable.

## 24.2 Quality Gates

- automated tests pass (unit, integration, and relevant E2E);
- static analysis passes with no suppressions introduced;
- formatting passes;
- no known regressions remain.

## 24.3 Documentation

- documentation is updated where public behaviour has changed;
- the relevant Feature or Specification document in `docs/` reflects the implemented behaviour;
- any ADR affected by the change has been reviewed and updated if necessary.

## 24.4 Specification Completeness

Every Feature specification must include, before implementation begins:

- **Acceptance criteria** — a verifiable checklist of observable outcomes (not implementation details);
- **Edge cases** — documented scenarios for boundary inputs, failure modes, and unexpected states;
- **Manual verification steps** — a step-by-step procedure a human tester can follow to confirm the feature works end-to-end.

A feature whose specification is missing any of these three sections is not considered ready for implementation.

## 24.5 Art & Prompt Compliance

If the feature generates or displays visual assets:

- every generated asset satisfies the Art Bible quality gates (technical, artistic, content safety);
- every prompt was constructed by the Prompt Builder — no manually authored prompts in application code;
- the generation record stores prompt_version, model_version, and timestamp.

## 24.6 Accessibility

- all interactive elements are keyboard-navigable;
- all images have meaningful alt text or are marked as decorative;
- colour contrast meets the minimum 4.5:1 ratio for text;
- `prefers-reduced-motion` is respected.

## 24.7 Child Safety

- no technical error messages are visible to children;
- no user-supplied content reaches a generation API without sanitisation;
- privacy requirements (data minimisation, parental controls) are satisfied.

---

# 25. Non-Negotiable Rules

The following rules are absolute.

- Do not contradict project documentation.
- Do not introduce undocumented architecture.
- Do not hard-code AI prompts.
- Do not bypass the Prompt Builder.
- Do not place business logic in controllers.
- Do not duplicate business logic across frontend and backend.
- Do not introduce unnecessary dependencies.
- Do not commit unfinished placeholder implementations.
- Do not weaken test coverage.
- Do not sacrifice maintainability for short-term convenience.

---

# 26. Guiding Principle

Every implementation decision should support the following objective:

> Build a maintainable, deterministic, child-friendly educational game whose implementation faithfully reflects the documented architecture, gameplay and artistic vision while remaining simple, extensible and production-ready.
> 