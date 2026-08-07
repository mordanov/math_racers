# Product Requirements Document — Math Racers v1.0

**Level:** Product Requirements
**Status:** Authoritative
**Source:** GDD Chapter 1, 2, 8, 12; speckit_specification.md
**Parent:** [Vision](vision.md)

---

## 1. Product Goal

Deliver a browser-based educational racing game that measurably improves children's arithmetic fluency through short, joyful race sessions.

---

## 2. Epics

| Epic | Description | Link |
|------|-------------|------|
| E1 — Gameplay | Race engine, math engine, AI opponents, game modes | [gameplay/epic.md](gameplay/epic.md) |
| E2 — Avatar System | Character creation, AI generation, lifecycle | [content/epic.md](content/epic.md) |
| E3 — Progression | XP, achievements, statistics, adaptive difficulty | [economy/epic.md](economy/epic.md) |
| E4 — Content Pipeline | Asset generation, validation, storage | [ai/asset-pipeline.md](ai/asset-pipeline.md) |
| E5 — UI/UX | All screens, components, accessibility | [ui/screens.md](ui/screens.md) |
| E6 — Engineering | Backend, infrastructure, security | [engineering/technical-requirements.md](engineering/technical-requirements.md) |

---

## 3. Functional Requirements

### 3.1 Account System

- FR-001: Parent creates an account with email + password.
- FR-002: Parent creates up to 5 child profiles under one account.
- FR-003: Children do not require separate email addresses.
- FR-004: Parent can delete any child profile and all associated data.

### 3.2 Avatar System

- FR-010: Child selects animal species, fur/skin colour, eye colour, accessories, and clothing.
- FR-011: System generates a unique AI character description from child inputs.
- FR-012: System generates a character biography and proposed names using an LLM.
- FR-013: System generates a portrait using GPT Image from the character description.
- FR-014: Child can rename their avatar at any time.
- FR-015: Child can designate one avatar as their favourite.
- FR-016: Child can regenerate an avatar portrait; previous versions are retained.
- FR-017: Maximum avatar count per child profile: 50.

### 3.3 Race Engine

- FR-020: A race consists of exactly 8 mathematical checkpoints.
- FR-021: 1–5 runners participate in each race.
- FR-022: Runner movement is calculated from: `Base Distance × Accuracy Modifier × Speed Modifier`.
- FR-023: Movement tiers: Perfect (<2 s) = +18 m, Excellent (<4 s) = +15 m, Good (<6 s) = +12 m, Slow/Correct = +9 m, Incorrect = +0 m.
- FR-024: The entire race simulation runs client-side with no network round-trips during play.
- FR-025: A single authoritative game clock governs all race timing.

### 3.4 Mathematics Engine

- FR-030: Supported operations: addition (+), subtraction (−), multiplication (×), division (÷).
- FR-031: Six difficulty tiers (Tier 1: Addition only → Tier 6: Custom mixed sets).
- FR-032: Problem generation is deterministic given a seed.
- FR-033: Answer validation is instantaneous from the player's perspective.
- FR-034: No two consecutive identical problems are generated.

### 3.5 Adaptive Difficulty

- FR-040: Skill score = `0.70 × Accuracy + 0.30 × Speed Score` over last 50 problems.
- FR-041: Increase difficulty if accuracy ≥ 90% and response time is consistently below target.
- FR-042: Decrease difficulty if accuracy < 60%.
- FR-043: Difficulty never changes during an active race.

### 3.6 Game Modes

- FR-050: Quick Race — single race, 1–5 runners, player-chosen settings.
- FR-051: Championship — series of races with cumulative scoring and rankings.
- FR-052: Training — solo practice, no opponents, any operation, no time pressure.
- FR-053: Duel — player vs one AI opponent at a matched difficulty.

### 3.7 Progression

- FR-060: XP awarded for: race completion (+100), correct answer (+20), perfect-answer streak (+10), daily challenge (+200), championship (+500).
- FR-061: Level curve: `XP(level) = 100 × level²`.
- FR-062: XP is never deducted.
- FR-063: Achievements are permanent once unlocked.

### 3.8 Statistics

- FR-070: Track per-player: XP, level, races, accuracy, average response time, favourite operation.
- FR-071: Track per-avatar: races, wins, podiums, best streak.
- FR-072: Track per-session: duration, problems solved, mistakes, difficulty tier.
- FR-073: All history is retained permanently.

### 3.9 Parent Dashboard

- FR-080: Parent sees weekly summary: problems solved, accuracy, average time, strongest/weakest operation.
- FR-081: Parent can set preferred difficulty tier per child.
- FR-082: Parent can export or delete all child data.
- FR-083: No educational analytics are shared publicly.

---

## 4. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| Startup time | < 3 seconds |
| Race loading | < 2 seconds |
| Problem generation | < 1 millisecond |
| Rendering | 60 FPS target, 30 FPS minimum |
| Audio latency | < 50 milliseconds |
| Browser support | Chrome, Edge, Firefox, Safari (current stable) |
| Device support | Desktop, laptop, tablet (primary); large-screen mobile (secondary) |
| Accessibility | Keyboard navigation, visible focus, semantic HTML, scalable text, reduced-motion |
| Security | HTTPS only, CSRF protection, input validation, rate limiting, secure secrets |
| Privacy | COPPA-aware data minimisation; parent controls all child data |

---

## 5. Explicit Exclusions (v1.0)

- Global or public leaderboards
- Real-time multiplayer
- Paid content or premium currency
- Daily-login streak punishment
- Mobile-first small-screen UI
- Voice narration
- Offline avatar generation

---

## 6. Document Hierarchy

```
Vision (vision.md)
       ↓
   PRD (prd.md)           ← this document
       ↓
  Epics (*/epic.md)
       ↓
  Features (*/feature-*.md)
       ↓
Specifications (*/spec-*.md)
```
