# Math Racers — Spec Kit

This directory contains the project's structured documentation, organised into topic-focused files following the Spec Kit hierarchy.

---

## Document Hierarchy

```
Vision
  ↓
Product Requirements Document (PRD)
  ↓
Epics
  ↓
Features
  ↓
Specifications
```

---

## Quick Navigation

### Top-Level

| Document | Description |
|----------|-------------|
| [vision.md](vision.md) | One-page product vision — why this game exists |
| [prd.md](prd.md) | Full product requirements — all FRs and NFRs |

### Gameplay (`gameplay/`)

| Document | Level |
|----------|-------|
| [epic.md](gameplay/epic.md) | Epic E1 overview |
| [feature-race-engine.md](gameplay/feature-race-engine.md) | Race mechanics, movement model, state machine |
| [spec-race-engine.md](gameplay/spec-race-engine.md) | Implementation spec, edge cases, verification steps |
| [feature-math-engine.md](gameplay/feature-math-engine.md) | Problem generation, difficulty tiers, adaptive difficulty |
| [spec-math-engine.md](gameplay/spec-math-engine.md) | Math engine implementation spec — data models, generation algorithm, validation |
| [feature-ai-opponents.md](gameplay/feature-ai-opponents.md) | AI personalities and behaviour simulation |
| [spec-ai-opponents.md](gameplay/spec-ai-opponents.md) | AI opponent implementation spec — personality parameters, simulation algorithm |
| [feature-game-modes.md](gameplay/feature-game-modes.md) | Quick Race, Championship, Training, Duel |
| [spec-game-modes.md](gameplay/spec-game-modes.md) | Game modes implementation spec — session models, lifecycles, API endpoints |

### Economy (`economy/`)

| Document | Level |
|----------|-------|
| [epic.md](economy/epic.md) | Epic E3 overview |
| [feature-xp-progression.md](economy/feature-xp-progression.md) | XP awards, level curve, cosmetic rewards |
| [spec-xp-progression.md](economy/spec-xp-progression.md) | XP & progression implementation spec — data models, formula, workflow |
| [feature-adaptive-difficulty.md](economy/feature-adaptive-difficulty.md) | Skill score formula, adjustment rules |
| [feature-achievements.md](economy/feature-achievements.md) | Achievement categories, presentation, persistence |
| [spec-achievements.md](economy/spec-achievements.md) | Achievements implementation spec — trigger table, evaluation, presentation flow |
| [feature-statistics.md](economy/feature-statistics.md) | Player, avatar, and session statistics |
| [spec-statistics.md](economy/spec-statistics.md) | Statistics implementation spec — data models, aggregation, weekly summary |

### Content / Avatar System (`content/`)

| Document | Level |
|----------|-------|
| [epic.md](content/epic.md) | Epic E2 overview |
| [feature-avatar-creation.md](content/feature-avatar-creation.md) | Creation flow, LLM steps, validation |
| [feature-avatar-lifecycle.md](content/feature-avatar-lifecycle.md) | Gallery, favourite, rename, versioning, deletion |
| [spec-avatar-generation.md](content/spec-avatar-generation.md) | Data models, API endpoints, edge cases, verification |

### Art (`art/`)

| Document | Description |
|----------|-------------|
| [visual-language.md](art/visual-language.md) | Palette, shape language, lighting, consistency rules |
| [character-design.md](art/character-design.md) | Anatomy, proportions, expressions, forbidden characteristics |
| [ui-style.md](art/ui-style.md) | Spacing, typography, animation timing, component states |
| [image-generation-standards.md](art/image-generation-standards.md) | Technical specs, quality gates, regeneration policy |

### Prompts (`prompts/`)

| Document | Description |
|----------|-------------|
| [gpt-image-prompts.md](prompts/gpt-image-prompts.md) | All GPT Image templates, global prefix/negative, variables |
| [llm-prompts.md](prompts/llm-prompts.md) | All LLM prompts — avatar, biography, achievements, messages |
| [claude-code-prompts.md](prompts/claude-code-prompts.md) | Engineering prompts for Claude Code sessions |

### AI Architecture (`ai/`)

| Document | Description |
|----------|-------------|
| [ai-architecture.md](ai/ai-architecture.md) | Provider abstraction, Prompt Builder, async pipeline |
| [asset-pipeline.md](ai/asset-pipeline.md) | Full asset lifecycle: request → validate → store → cache |

### UI (`ui/`)

| Document | Description |
|----------|-------------|
| [screens.md](ui/screens.md) | All screens, key components, navigation flow, accessibility |
| [spec-ui-implementation.md](ui/spec-ui-implementation.md) | UI implementation spec — page inventory, component hierarchy, API client, offline rules |

### Engineering (`engineering/`)

| Document | Description |
|----------|-------------|
| [technical-requirements.md](engineering/technical-requirements.md) | Stack, architecture, performance targets, security, testing |
| [audio-design.md](engineering/audio-design.md) | Audio layers, music progression, sounds, accessibility |
| [roadmap.md](engineering/roadmap.md) | Version roadmap, content calendar, what not to build |
| [spec-backend-foundation.md](engineering/spec-backend-foundation.md) | Backend foundation spec — module layout, auth flow, error handling, job lifecycle |
| [spec-infrastructure.md](engineering/spec-infrastructure.md) | Infrastructure spec — Docker Compose services, build phases, CI/CD, release criteria |

---

## Source Documents

The original monolithic documents remain authoritative and unchanged:

| Document | Role |
|----------|------|
| `initial_spec/gdd.md` | Complete Game Design Document (14 chapters) |
| `initial_spec/game_economy_specification.md` | Economy & progression formulas |
| `initial_spec/art_bible.md` | Visual language (4 parts) |
| `initial_spec/prompt_bible.md` | All prompts (3 parts) |
| `initial_spec/speckit_constitution.md` | Engineering principles & Definition of Done |
| `initial_spec/speckit_specification.md` | Build phases & implementation strategy (superseded by `docs/` specs) |
| `initial_spec/ADR/ADR-001.md` | Foundation Architecture |
| `initial_spec/ADR/ADR-002.md` | Backend Architecture |
| `initial_spec/ADR/ADR-003.md` | AI Architecture |
| `initial_spec/ADR/ADR-004.md` | Frontend Architecture |
| `initial_spec/ADR/ADR-005.md` | Infrastructure Architecture |

The `docs/` files are derived summaries and structured extracts. In any conflict, the source documents take precedence (per the Constitution's document hierarchy).

---

## Definition of Done

Every feature is complete when it satisfies all sections of **Constitution §24**:

- §24.1 Compliance — Constitution, ADRs, GDD, Art Bible, Prompt Bible
- §24.2 Quality Gates — tests, static analysis, formatting, no regressions
- §24.3 Documentation — updated docs in `docs/` and affected ADRs
- §24.4 Specification Completeness — acceptance criteria, edge cases, manual verification steps
- §24.5 Art & Prompt Compliance — quality gates, Prompt Builder, versioned records
- §24.6 Accessibility — keyboard nav, alt text, colour contrast, reduced motion
- §24.7 Child Safety — no technical errors shown to children, sanitised inputs, privacy respected
