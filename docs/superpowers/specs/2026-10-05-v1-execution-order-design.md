# Math Racers v1.0 — Implementation Execution Order

**Date:** 2026-10-05
**Branch:** `010-v1-execution-plan`
**Status:** Approved design — ready for implementation planning

---

## Problem Statement

The backend domain layer (specs 001–009) is complete. The frontend is an empty
shell (`App.tsx` returns `<div>Math Racers</div>`). The backlog has 11 sections
of buildable work, but their natural dependency graph is not a strict sequence —
some sections can interleave, some must be split, and one section (§10
Accessibility) is cheaper as a build-time rule than a post-hoc audit.

This document records the approved execution order and the reasoning behind each
placement decision.

---

## Fixed Dependency Backbone

The race setup screen requires the child to select an avatar before entering a
race (spec-ui-implementation.md §Page Inventory). This creates an unbreakable
partial order:

```
§3 (Frontend infrastructure)
  → §4 (Auth flow)
    → §5 (Avatar flow)
      → §6 (Race flow)
```

Every remaining section hangs off this backbone. Auth gates all pages. The
avatar wizard gates the race because a race without avatar selection is an
incomplete UX, not just a visual gap.

---

## Approved Execution Order

### Sprint 1 — Frontend Infrastructure (`§3`)

**Sections covered:** §3 entirely

Install React Router; create route stubs for all 10 pages. Build the typed
`APIClient` class (retry on 5xx, `APIError` on 4xx). Define design tokens from
`docs/art/ui-style.md`. Build the minimum shared primitives: `Button`, `Card`,
`XPBar`, `LoadingSpinner`, `ErrorState`, `ConfirmDialog`, `NotificationToast`.

**Accessibility rule active from sprint 1:** Every component ships with
correct focus management, ARIA roles, and minimum colour contrast. This is not
an audit item — it is a build-time acceptance criterion from this point forward.

**Milestone:** App has routing, typed API layer, and a working design system.
No visible pages yet.

---

### Sprint 2 — Auth + Child Profiles (`§4` + `§1.1`)

**Sections covered:** §4 entirely; §1 task group T030–T031

Auth flow (login/register page, child profile select, auth context, route
guards). Also: create the `child_profiles` table (Alembic migration `0010`) and
replace the ownership-check stub in `child_profile.py` middleware.

**Why §1.1 here:** The child profile table is a prerequisite for the child
profile select page (§4.2). Building §4 without §1.1 would require a second
pass immediately after. The cost is zero: §1.1 is a small migration + one
middleware file.

**Milestone:** App can log in, select a child profile, and navigate to
authenticated routes.

---

### Sprint 3 — Avatar Flow + Job Retry (`§5` + `§1.2`)

**Sections covered:** §5 entirely; §1 task groups T032–T035

Avatar gallery page (grid, empty state, generation polling). Avatar creator
wizard (5-step species/colour/accessories/clothing/reveal flow).

Also: background job retry logic — add `retrying` / `permanent_failure` states,
exponential backoff (30s / 120s / 480s), idempotency check on `enqueue_job()`.

**Why §1.2 here:** The avatar creator triggers background AI generation jobs.
Without retry logic, a failed GPT Image call leaves the job status stuck at
`running` forever. The child sees a spinner that never resolves. §1.2 fixes this
before users ever encounter it.

**Milestone:** A child can create a personalised avatar. The generation failure
path degrades gracefully.

---

### Sprint 4 — Race Flow (`§6`)

**Sections covered:** §6 entirely

Race setup page (mode selector, opponent count, difficulty display). Countdown
screen (3-2-1-GO, `aria-live`). Race screen (`useRaceEngine` wired to track,
runner markers, problem card, answer input, per-problem timer bar). Results
screen (positions table, XP breakdown, `AchievementToast`, level-up overlay).
Championship standings page.

**Milestone:** The core game loop is playable end-to-end. A child can log in,
create an avatar, start a race, solve problems, and see results.

---

### Sprint 5 — Statistics Slice (`§2` + `§7` + `§8`)

**Sections covered:** §2 entirely; §7 entirely; §8 entirely

Backend statistics module (Alembic migration `0011`, `player_stats`,
`avatar_stats`, `race_sessions` ORM models, repository, domain service, 6 API
endpoints, wired into `races/domain_service.py` `persist_race()`).

Statistics page (player-level stats, per-avatar stats table, paginated race
history).

Parent dashboard (weekly summary card, difficulty override, CSV export, delete
child profile). Settings page (difficulty display, reduced motion toggle —
volume sliders are stubbed out and wired to the audio engine in Sprint 6).

**Why §2+§7+§8 together:** The statistics backend has no standalone value until
the UI consumes it. Building the backend one sprint before the UI means
maintaining two separate in-flight branches simultaneously with no interim
deliverable. The statistics domain service wires directly into the race result
path, which is fully operational after Sprint 4, so Sprint 5 is the earliest
useful moment for §2.

**Milestone:** Parent value proposition is complete. Statistics, dashboard, and
settings are all functional.

---

### Sprint 6 — Audio Engine (`§9`)

**Sections covered:** §9 entirely

`audioEngine.ts` (Web Audio API context, 6-layer mixer, volume controls, priority
system). `soundSprites.ts` (sprite map for low-latency UI sounds). `useAudio`
React hook. Wire volume sliders in Settings page. Wire `AchievementToast` chime
stub. Preload race sounds before `RACING` state. Graceful no-op when
`AudioContext` creation fails.

**Note:** Audio *files* are external assets (see `docs/enhancements/external-assets.md`
§2). The engine code works with placeholder silence until real files are dropped in.

**Milestone:** Audio engine is wired and testable. Inserting real audio files
requires no code changes.

---

### Sprint 7 — Offline Degradation (`§11`)

**Sections covered:** §11 entirely

`navigator.onLine` + connection probe on app load. Avatar Creator disabled
offline. Race Setup shows Training Mode only offline. Statistics shows cached
data with sync indicator. Parent Dashboard disabled offline.

**Milestone:** App degrades gracefully on flaky connections.

---

### Sprint 8 — Infrastructure Cleanup (`§1.3–1.5`)

**Sections covered:** §1 task groups T036, T037–T038, T041–T044

Health endpoint integration tests (degraded/unavailable HTTP paths, 503 when DB
is down). Correlation ID propagation into background jobs. `mypy` strict mode
across the backend; `ruff` + `black` clean; full test suite green.

**Why last:** These are observability and quality items with no user-visible
impact. None unblock anything. Doing them last means the final diff before v1.0
tag is a clean "no user-facing changes" pass that is low risk to merge.

**Milestone:** Codebase is production-ready: types clean, tests green, logs
carry request IDs end-to-end.

---

## Accessibility as a Build-Time Rule

§10 (Accessibility Hardening) does **not** appear as a standalone sprint. Instead
it is enforced as a build-time acceptance criterion for every component in
sprints 1–7:

- Tab order in logical reading order
- 2px focus outline, minimum 3:1 contrast ratio
- `alt` text or `aria-hidden` on all images
- Text colour contrast ≥ 4.5:1
- `prefers-reduced-motion` disables non-essential animations
- `aria-live="polite"` on race countdown timer
- `aria-label` on math problem input
- Focus trap + Escape dismiss on all dialogs
- Results table uses `<table>` with `scope` attributes

A post-build accessibility audit (§10 as originally written) is eliminated
because weaving these rules in costs nothing per component and retrofitting them
costs significant rework. If a final automated audit is desired (axe-core, pa11y),
it can run in CI as a non-blocking check from Sprint 1 onward.

---

## Sprint Summary

| Sprint | Sections | Key Milestone |
|--------|----------|---------------|
| 1 | §3 | Router + API client + design system |
| 2 | §4, §1.1 | Auth flow + child profiles table |
| 3 | §5, §1.2 | Avatar creator + job retry |
| 4 | §6 | Core game loop playable |
| 5 | §2, §7, §8 | Statistics + parent dashboard |
| 6 | §9 | Audio engine (code only) |
| 7 | §11 | Offline degradation |
| 8 | §1.3–1.5 | Backend lint + observability |

---

## What This Design Does Not Cover

- **External assets** (audio files, artwork, API keys, hosting) — see
  `docs/enhancements/external-assets.md`
- **v1.1+ features** (manual content review queue, leaderboards, additional
  game modes beyond v1.0 scope) — see `docs/engineering/roadmap.md`
- **Backend spec 003–009 extensions** — all are marked complete and no
  extensions are in scope for this plan
