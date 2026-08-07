# UI Implementation — Specification

**Level:** Specification
**Status:** Authoritative
**Source:** FR-all; ui/screens.md; art/ui-style.md; ADR-004; speckit_specification.md §45–68
**Parent:** [Epic E5 — UI/UX](../prd.md)
**See also:** [screens.md](screens.md), [../art/ui-style.md](../art/ui-style.md), [../art/visual-language.md](../art/visual-language.md)

---

## Page Inventory

| Page | Route | Primary Responsibility |
|------|-------|----------------------|
| Home | `/` | Entry point; navigate to avatar gallery or start race |
| Avatar Gallery | `/avatars` | Browse, select, manage avatars |
| Avatar Creator | `/avatars/new` | Create new avatar; view generation progress |
| Race Setup | `/race/setup` | Choose mode, opponents, difficulty; start race |
| Race Screen | `/race/:id` | Active gameplay; render runners, problems, progress |
| Results Screen | `/race/:id/results` | Show finishing order, XP, achievements |
| Statistics | `/statistics` | Player and avatar statistics; history |
| Settings | `/settings` | Audio, difficulty preference, account |
| Parent Dashboard | `/parent` | Weekly summary, child profile management |
| Championship | `/championship/:id` | Championship standings and next race |

---

## Component Hierarchy

Follows ADR-004 layered architecture:

```
Pages
  └── Features (isolated business capability modules)
        └── Components (reusable presentation units)
              └── Shared UI (design tokens, primitives)
                    └── Infrastructure (API client, router, stores)
```

Rules:
- Pages contain layout only; no business logic.
- Features communicate through explicit interfaces; never import from another feature directly.
- Components are stateless where practical; receive data via props.
- Shared UI has no business logic; contains only design tokens and primitive components.

---

## Feature State Models

### Race Feature

```typescript
interface RaceFeatureState {
  sessionId: string;
  status: 'idle' | 'loading' | 'countdown' | 'racing' | 'finishing' | 'results';
  currentCheckpoint: number;         // 1–8
  currentProblem: Problem | null;
  playerPosition: number;            // accumulated distance in metres
  opponents: AIOpponentState[];
  answerHistory: AnswerRecord[];
  clock: number;                     // ms since race start (single source of truth)
  seed: number;
}
```

### Avatar Gallery Feature

```typescript
interface AvatarGalleryState {
  avatars: Avatar[];
  selectedAvatarId: string | null;
  favouriteAvatarId: string | null;
  status: 'loading' | 'ready' | 'error';
  generationJobs: GenerationJobStatus[];
}
```

### Championship Feature

```typescript
interface ChampionshipState {
  championshipId: string;
  standings: StandingEntry[];
  racesCompleted: number;
  totalRaces: number;
  status: 'active' | 'completed';
}
```

---

## API Client Pattern

All server communication goes through a single typed client. Application code never constructs `fetch` calls directly.

```typescript
// src/infrastructure/api-client.ts

class APIClient {
  private baseURL = '/api/v1';

  async get<T>(path: string): Promise<T> {
    return this.request<T>('GET', path);
  }

  async post<T>(path: string, body: unknown): Promise<T> {
    return this.request<T>('POST', path, body);
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
    attempt = 1
  ): Promise<T> {
    const response = await fetch(this.baseURL + path, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
      credentials: 'same-origin',
    });

    if (response.status >= 500 && attempt < 3) {
      await delay(200 * attempt);
      return this.request<T>(method, path, body, attempt + 1);
    }

    if (!response.ok) {
      throw new APIError(response.status, await response.json());
    }

    return response.json() as Promise<T>;
  }
}
```

- Retry on 5xx up to 3 attempts with exponential backoff (200 ms, 400 ms).
- 4xx errors are not retried; they propagate as `APIError`.
- All errors are caught at the feature layer and translated to user-friendly messages.

---

## Design System Tokens

All visual values come from the design token file. Components must never use hardcoded values.

```typescript
// src/shared/tokens.ts — reference only; do not redefine here
// See: docs/art/ui-style.md for authoritative values

const tokens = {
  spacing: { unit: 8, xs: 4, sm: 8, md: 16, lg: 24, xl: 32, xxl: 48 },
  radius: { sm: 4, md: 8, lg: 16, xl: 24 },
  animation: {
    instant: '100ms',
    fast: '200ms',
    normal: '300ms',
    slow: '500ms',
  },
  color: {
    primary: '#4A90D9',
    success: '#5CB85C',
    warning: '#F0AD4E',
    error: '#D9534F',
    // full palette: see art/ui-style.md
  },
};
```

---

## Offline Degradation Rules

| Page | Offline Behaviour |
|------|------------------|
| Home | Available (static) |
| Avatar Gallery | Available with cached avatars; creation disabled |
| Avatar Creator | Unavailable; show "Internet required" message |
| Race Setup | Available; only Training Mode enabled |
| Race Screen | Available in Training Mode |
| Statistics | Available with cached data; sync indicator shown |
| Settings | Available (local settings) |
| Parent Dashboard | Unavailable; show "Internet required" message |

Offline detection: `navigator.onLine` + connection probe on app load.

---

## Navigation Flow

```
Home
  ├── Avatar Gallery
  │     └── Avatar Creator
  ├── Race Setup
  │     └── Race Screen
  │           └── Results Screen
  │                 └── Race Setup (next race)
  ├── Championship
  │     └── Race Setup (championship race)
  ├── Statistics
  └── Settings
        └── Parent Dashboard (parent auth required)
```

The browser Back button must work correctly on all routes. Race Screen disables Back during active gameplay (status == `racing`); navigating away requires confirmation dialog.

---

## Accessibility Implementation Checklist

- [ ] All interactive elements receive focus via Tab key in logical reading order.
- [ ] Focus is visible (2px outline, minimum 3:1 contrast with background).
- [ ] Every image has `alt` text or `aria-hidden="true"` if decorative.
- [ ] Text colour contrast ≥ 4.5:1 against background for all text elements.
- [ ] `prefers-reduced-motion: reduce` disables all non-essential CSS animations.
- [ ] Race countdown timer has `aria-live="polite"` region for screen readers.
- [ ] Math problem input has `aria-label` describing the current problem.
- [ ] Dialog components trap focus while open; restore focus on close.
- [ ] Error messages use `role="alert"` for immediate screen reader announcement.
- [ ] Race results are summarised in a `<table>` with proper headers (`scope="col"`, `scope="row"`).

---

## Edge Cases

1. **Race screen loses focus mid-race** (e.g., Alt+Tab) — the race timer continues; the game does not pause. On focus return, the current problem is still displayed. This matches the design decision that there is no pause mechanic in Quick Race.
2. **Avatar Gallery empty (no avatars yet)** — show an empty-state illustration with a "Create Your First Avatar" call-to-action button linking to Avatar Creator. Do not show a blank page.
3. **Results screen with network failure during sync** — show the results locally from the in-memory race state. Display a "Couldn't save results — tap to retry" inline message. The race result must not be lost; retry with the stored `idempotency_key`.
4. **Settings page with no audio hardware** — Web Audio API context creation may fail silently. All audio controls are still shown and functional; they simply produce no sound. No error is shown.
5. **Generation job still pending when Avatar Gallery is loaded** — show a "generating…" skeleton card in the gallery for the in-progress avatar. Poll `GET /api/v1/jobs/{id}` every 3 seconds; replace skeleton with the avatar card when status is `completed`.
6. **Parent Dashboard accessed without parent authentication** — redirect to a parent login screen; do not show child data.
7. **Championship interrupted** — on app reopen, if an active championship exists, show a "Continue Championship" prompt on the Home screen.
8. **Very long avatar name** — truncate display at 24 characters with ellipsis; store full name in backend (max 50 chars validated server-side).

---

## Manual Verification Steps

1. **Home page** — load the app. Confirm the Home page renders in < 3 seconds. Confirm navigation links to Avatar Gallery and Race Setup are keyboard-accessible.
2. **Avatar Gallery** — navigate to Avatar Gallery with 0 avatars. Confirm the empty state is shown. Create an avatar. Confirm the new avatar card appears.
3. **Avatar Creator** — complete the avatar creation form. Confirm the generation progress indicator appears. Confirm the avatar card is shown after generation completes.
4. **Race Setup** — configure a Quick Race. Change difficulty tier. Confirm the tier selection persists when navigating back.
5. **Race Screen** — start a race. Tab through interactive elements. Confirm the math problem input receives focus automatically. Confirm the timer and runner positions update in real time.
6. **Results Screen** — complete a race. Confirm the finishing positions, XP earned, and correct/incorrect counts are all correct. Confirm achievements play their animation.
7. **Statistics** — complete 3 races. Open Statistics. Confirm `total_races == 3` and accuracy is computed correctly.
8. **Settings** — reduce music volume to 0. Leave Settings. Start a race. Confirm no music plays.
9. **Offline simulation** — disable network. Attempt to open Avatar Creator. Confirm "Internet required" message is shown. Open Race Setup. Confirm only Training Mode is available.
10. **Parent Dashboard** — log in as a parent. Open Parent Dashboard. Confirm the weekly summary shows data for all child profiles. Confirm export and delete options are present.

---

## Acceptance Criteria

- [ ] All 8 v1.0 pages are implemented and routable.
- [ ] All interactive elements are keyboard-navigable in logical tab order.
- [ ] Colour contrast meets 4.5:1 for all text elements.
- [ ] `prefers-reduced-motion` disables non-essential animations.
- [ ] Empty state is shown in Avatar Gallery when no avatars exist.
- [ ] Race results are preserved locally and retried on network failure.
- [ ] Generation-in-progress avatars show a skeleton card with polling.
- [ ] Parent Dashboard is blocked behind parent authentication.
- [ ] Offline mode disables avatar creation and parent dashboard; Training Mode remains available.
- [ ] Long avatar names are truncated in the UI without breaking layout.
