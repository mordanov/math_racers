# Specification Implementation Order

Ordered by dependency. Each spec assumes all prior specs are complete.

---

| # | Spec | Epic | Why this order |
|---|------|------|----------------|
| 1 | `engineering/spec-infrastructure.md` | E6 | Docker, CI/CD — foundation for everything |
| 2 | `engineering/spec-backend-foundation.md` | E6 | Auth, module layout, error handling, job lifecycle |
| 3 | `gameplay/spec-math-engine.md` | E1 | Core logic; no upstream deps |
| 4 | `gameplay/spec-race-engine.md` | E1 | Depends on math engine |
| 5 | `gameplay/spec-ai-opponents.md` | E1 | Depends on race engine |
| 6 | `gameplay/spec-game-modes.md` | E1 | Depends on race + math + AI opponents |
| 7 | `content/spec-avatar-generation.md` | E2 | Depends on backend foundation; parallel to gameplay |
| 8 | `economy/spec-xp-progression.md` | E3 | Depends on game modes (race completion events) |
| 9 | `economy/spec-achievements.md` | E3 | Depends on XP + statistics events |
| 10 | `economy/spec-statistics.md` | E3 | Depends on game modes + race engine |
| 11 | `ui/spec-ui-implementation.md` | E5 | Depends on all backend specs |
