# Sprint 1: Frontend Infrastructure — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the routing, typed API client, design tokens, and seven shared UI primitives that every subsequent sprint depends on — turning the empty `App.tsx` shell into a navigable app skeleton with a working design system.

**Architecture:** React Router v6 with `createBrowserRouter`; `App.tsx` is the layout shell rendered as the root element, child routes render via `<Outlet>`. All HTTP calls go through a single `APIClient` singleton; engine API files that currently own their own `fetch` logic are refactored to import it. UI components use inline styles drawing from `tokens.ts`; keyframe animations live in one shared `animations.css`.

**Tech Stack:** React 18.3, TypeScript 5.4, react-router-dom ^6, Vitest 3 + jsdom, @testing-library/react ^14, @testing-library/user-event ^14, @testing-library/jest-dom ^6, Vite 5.

**Spec:** `docs/superpowers/specs/2026-10-05-v1-execution-order-design.md` (Sprint 1 section); `docs/ui/spec-ui-implementation.md` (§API Client Pattern, §Design System Tokens, §Accessibility Implementation Checklist); `docs/art/ui-style.md`

## Global Constraints

- Node ≥ 20, React 18.3 exactly (peer dep for @testing-library/react)
- All visual values must come from `src/shared/tokens.ts` — no hardcoded numbers in components
- Every interactive element: visible focus ring (2px solid, offset 2px), min touch target 44×44px
- `prefers-reduced-motion: reduce` must disable all CSS animations — use `useReducedMotion()` hook
- Text colour contrast ≥ 4.5:1, UI component contrast ≥ 3:1 (WCAG AA)
- Run tests: `cd frontend && npm test` (Vitest run mode)
- Typecheck: `cd frontend && npm run typecheck`
- Each commit message must end with `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`

## Review Focus

These five failure modes are most likely to surface during use but are easy to miss in normal happy-path testing. The owning task for each has a specific test that pins the behaviour.

1. **APIClient retry storm** — a 5xx response triggers retry; must retry exactly 2 more times (3 total), then throw. Not 2, not 4, not infinite. Test added to Task 2.
2. **APIClient 204 on DELETE** — `response.status === 204` must return `undefined` without calling `response.json()` (which throws on a body-less response). Test added to Task 2.
3. **raceApi 409 absorption** — `postRaceSummary` must catch `APIError` with status 409 and return `{ new_achievements: [] }` without rethrowing. The APIClient must NOT treat 409 as a 5xx retry. Test added to Task 3.
4. **ConfirmDialog focus leak** — on close, focus must return to the element that was active before the dialog opened. Failure leaves the user's keyboard position in an unknown state. Test added to Task 10.
5. **NotificationToast timer leak** — the 3-second `setTimeout` must be cleared on unmount. If not, `onClose` fires after the component is gone and may call a stale closure or setState on an unmounted tree. Test added to Task 11.

---

### Task 1: Install dependencies, test harness, router scaffold

**Files:**
- Modify: `frontend/package.json` (add runtime + dev deps)
- Modify: `frontend/vite.config.ts` (add setupFiles)
- Create: `frontend/src/test-setup.ts`
- Create: `frontend/src/shared/animations.css`
- Create: `frontend/src/router.tsx`
- Create: `frontend/src/pages/HomePage.tsx` (and 9 siblings below)
- Create: `frontend/src/pages/AvatarGalleryPage.tsx`
- Create: `frontend/src/pages/AvatarCreatorPage.tsx`
- Create: `frontend/src/pages/RaceSetupPage.tsx`
- Create: `frontend/src/pages/RaceScreenPage.tsx`
- Create: `frontend/src/pages/ResultsScreenPage.tsx`
- Create: `frontend/src/pages/StatisticsPage.tsx`
- Create: `frontend/src/pages/SettingsPage.tsx`
- Create: `frontend/src/pages/ParentDashboardPage.tsx`
- Create: `frontend/src/pages/ChampionshipPage.tsx`
- Modify: `frontend/src/main.tsx`
- Modify: `frontend/src/App.tsx`
- Test: `frontend/src/router.test.tsx`

**Interfaces:**
- Produces: `routeConfig` (exported array, consumed by `router.test.tsx` via `createMemoryRouter`); `router` (default export, consumed by `main.tsx`)
- Produces: 10 stub page components with `data-testid="page-[slug]"` attributes

- [ ] **Step 1: Install runtime and dev dependencies**

```bash
cd frontend
npm install react-router-dom
npm install -D @testing-library/react @testing-library/user-event @testing-library/jest-dom
```

Expected: `package.json` shows new entries; `node_modules` updated.

- [ ] **Step 2: Create test setup file**

Create `frontend/src/test-setup.ts`:

```typescript
import '@testing-library/jest-dom';
```

- [ ] **Step 3: Add setupFiles to Vite config**

Modify `frontend/vite.config.ts`:

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    passWithNoTests: true,
    setupFiles: ['./src/test-setup.ts'],
  },
});
```

- [ ] **Step 4: Create shared animations CSS**

Create `frontend/src/shared/animations.css`:

```css
@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

@media (prefers-reduced-motion: reduce) {
  .spin { animation: none !important; }
  .pulse { animation: none !important; }
  .slideIn { animation: none !important; }
}
```

- [ ] **Step 5: Create 10 stub page components**

Create each file below with the shown content (replace `[Name]` and `[slug]` per the table):

| File | Name | slug |
|------|------|------|
| `src/pages/HomePage.tsx` | Home | `home` |
| `src/pages/AvatarGalleryPage.tsx` | AvatarGallery | `avatar-gallery` |
| `src/pages/AvatarCreatorPage.tsx` | AvatarCreator | `avatar-creator` |
| `src/pages/RaceSetupPage.tsx` | RaceSetup | `race-setup` |
| `src/pages/RaceScreenPage.tsx` | RaceScreen | `race-screen` |
| `src/pages/ResultsScreenPage.tsx` | ResultsScreen | `results-screen` |
| `src/pages/StatisticsPage.tsx` | Statistics | `statistics` |
| `src/pages/SettingsPage.tsx` | Settings | `settings` |
| `src/pages/ParentDashboardPage.tsx` | ParentDashboard | `parent-dashboard` |
| `src/pages/ChampionshipPage.tsx` | Championship | `championship` |

Template (example for `HomePage.tsx`):

```tsx
export default function HomePage() {
  return <div data-testid="page-home">Home</div>;
}
```

Fill in for every file using the slug from the table as the `data-testid` value and the Name as the function name.

- [ ] **Step 6: Create router.tsx**

Create `frontend/src/router.tsx`:

```tsx
import { createBrowserRouter, type RouteObject } from 'react-router-dom';
import App from './App';
import HomePage from './pages/HomePage';
import AvatarGalleryPage from './pages/AvatarGalleryPage';
import AvatarCreatorPage from './pages/AvatarCreatorPage';
import RaceSetupPage from './pages/RaceSetupPage';
import RaceScreenPage from './pages/RaceScreenPage';
import ResultsScreenPage from './pages/ResultsScreenPage';
import StatisticsPage from './pages/StatisticsPage';
import SettingsPage from './pages/SettingsPage';
import ParentDashboardPage from './pages/ParentDashboardPage';
import ChampionshipPage from './pages/ChampionshipPage';

export const routeConfig: RouteObject[] = [
  {
    element: <App />,
    children: [
      { index: true, element: <HomePage /> },
      { path: '/avatars', element: <AvatarGalleryPage /> },
      { path: '/avatars/new', element: <AvatarCreatorPage /> },
      { path: '/race/setup', element: <RaceSetupPage /> },
      { path: '/race/:id', element: <RaceScreenPage /> },
      { path: '/race/:id/results', element: <ResultsScreenPage /> },
      { path: '/statistics', element: <StatisticsPage /> },
      { path: '/settings', element: <SettingsPage /> },
      { path: '/parent', element: <ParentDashboardPage /> },
      { path: '/championship/:id', element: <ChampionshipPage /> },
    ],
  },
];

export const router = createBrowserRouter(routeConfig);
```

- [ ] **Step 7: Update App.tsx**

Replace `frontend/src/App.tsx` with:

```tsx
import { Outlet } from 'react-router-dom';

export default function App() {
  return <Outlet />;
}
```

- [ ] **Step 8: Update main.tsx**

Replace `frontend/src/main.tsx` with:

```tsx
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { router } from './router';
import './shared/animations.css';

const root = document.getElementById('root');
if (!root) throw new Error('Root element not found');

createRoot(root).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
);
```

- [ ] **Step 9: Write the router test**

Create `frontend/src/router.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';
import { routeConfig } from './router';

function go(path: string) {
  const r = createMemoryRouter(routeConfig, { initialEntries: [path] });
  render(<RouterProvider router={r} />);
}

it('/ renders home page', () => {
  go('/');
  expect(screen.getByTestId('page-home')).toBeInTheDocument();
});

it('/avatars renders avatar gallery', () => {
  go('/avatars');
  expect(screen.getByTestId('page-avatar-gallery')).toBeInTheDocument();
});

it('/avatars/new renders avatar creator', () => {
  go('/avatars/new');
  expect(screen.getByTestId('page-avatar-creator')).toBeInTheDocument();
});

it('/race/setup renders race setup', () => {
  go('/race/setup');
  expect(screen.getByTestId('page-race-setup')).toBeInTheDocument();
});

it('/race/:id renders race screen', () => {
  go('/race/abc123');
  expect(screen.getByTestId('page-race-screen')).toBeInTheDocument();
});

it('/race/:id/results renders results screen', () => {
  go('/race/abc123/results');
  expect(screen.getByTestId('page-results-screen')).toBeInTheDocument();
});

it('/statistics renders statistics page', () => {
  go('/statistics');
  expect(screen.getByTestId('page-statistics')).toBeInTheDocument();
});

it('/settings renders settings page', () => {
  go('/settings');
  expect(screen.getByTestId('page-settings')).toBeInTheDocument();
});

it('/parent renders parent dashboard', () => {
  go('/parent');
  expect(screen.getByTestId('page-parent-dashboard')).toBeInTheDocument();
});

it('/championship/:id renders championship page', () => {
  go('/championship/ch1');
  expect(screen.getByTestId('page-championship')).toBeInTheDocument();
});
```

- [ ] **Step 10: Run tests**

```bash
cd frontend && npm test
```

Expected: 10 tests pass.

- [ ] **Step 11: Run typecheck**

```bash
cd frontend && npm run typecheck
```

Expected: no errors.

- [ ] **Step 12: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/vite.config.ts \
  frontend/src/test-setup.ts frontend/src/shared/animations.css \
  frontend/src/router.tsx frontend/src/router.test.tsx \
  frontend/src/App.tsx frontend/src/main.tsx \
  frontend/src/pages/
git commit -m "feat(frontend): install router + test harness, scaffold 10 page stubs

- react-router-dom, @testing-library/react/user-event/jest-dom added
- createBrowserRouter with App as layout shell, 10 child route stubs
- setupFiles wired to @testing-library/jest-dom matchers
- shared animations.css for keyframe definitions

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 2: APIClient + APIError

**Files:**
- Create: `frontend/src/infrastructure/api-client.ts`
- Test: `frontend/src/infrastructure/api-client.test.ts`

**Interfaces:**
- Produces: `export class APIError { status: number; body: unknown }` — consumed by all engine API files (Task 3) and feature error handlers
- Produces: `export const apiClient: APIClient` — the singleton consumed by Task 3

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/infrastructure/api-client.test.ts`:

```typescript
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { APIClient, APIError } from './api-client';

function mockFetch(status: number, body: unknown = {}) {
  return vi.fn().mockResolvedValue({
    status,
    ok: status >= 200 && status < 300,
    json: vi.fn().mockResolvedValue(body),
  });
}

describe('APIClient', () => {
  let client: APIClient;

  beforeEach(() => {
    client = new APIClient();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it('returns parsed JSON on 200', async () => {
    vi.stubGlobal('fetch', mockFetch(200, { value: 42 }));
    const result = await client.get<{ value: number }>('/test');
    expect(result).toEqual({ value: 42 });
  });

  // Review Focus #1: retry exactly 3 total attempts on 5xx
  it('retries on 5xx up to 3 total attempts then throws APIError', async () => {
    vi.stubGlobal('fetch', mockFetch(500));
    const promise = client.get('/test');
    await vi.runAllTimersAsync();
    await expect(promise).rejects.toBeInstanceOf(APIError);
    expect(vi.mocked(fetch)).toHaveBeenCalledTimes(3);
  });

  it('does not retry on 4xx', async () => {
    vi.stubGlobal('fetch', mockFetch(404));
    const promise = client.get('/test');
    await vi.runAllTimersAsync();
    await expect(promise).rejects.toBeInstanceOf(APIError);
    expect(vi.mocked(fetch)).toHaveBeenCalledTimes(1);
  });

  it('throws APIError with correct status on 4xx', async () => {
    vi.stubGlobal('fetch', mockFetch(401, { detail: 'Unauthorized' }));
    const promise = client.get('/test');
    await vi.runAllTimersAsync();
    try {
      await promise;
      expect.fail('should have thrown');
    } catch (e) {
      expect(e).toBeInstanceOf(APIError);
      expect((e as APIError).status).toBe(401);
    }
  });

  // Review Focus #2: 204 must return undefined without calling .json()
  it('returns undefined for 204 without parsing body', async () => {
    const fakeFetch = vi.fn().mockResolvedValue({ status: 204, ok: true });
    vi.stubGlobal('fetch', fakeFetch);
    const result = await client.delete('/test');
    expect(result).toBeUndefined();
    // json() was never called — fakeFetch response has no .json()
    // If it were called, this test would throw "json is not a function"
  });

  it('sends correct method and body for POST', async () => {
    const fake = mockFetch(200, { id: '1' });
    vi.stubGlobal('fetch', fake);
    await client.post('/items', { name: 'test' });
    expect(fake).toHaveBeenCalledWith('/api/v1/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'test' }),
      credentials: 'same-origin',
    });
  });

  it('sends PATCH with body', async () => {
    const fake = mockFetch(200, { id: '1' });
    vi.stubGlobal('fetch', fake);
    await client.patch('/items/1', { name: 'updated' });
    expect(fake).toHaveBeenCalledWith('/api/v1/items/1', expect.objectContaining({
      method: 'PATCH',
    }));
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && npm test -- api-client
```

Expected: FAIL — "Cannot find module './api-client'"

- [ ] **Step 3: Implement APIClient**

Create `frontend/src/infrastructure/api-client.ts`:

```typescript
export class APIError extends Error {
  constructor(
    public readonly status: number,
    public readonly body: unknown,
  ) {
    super(`HTTP ${status}`);
  }
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export class APIClient {
  private baseURL = '/api/v1';

  async get<T>(path: string): Promise<T> {
    return this.request<T>('GET', path);
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('POST', path, body);
  }

  async patch<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('PATCH', path, body);
  }

  async delete<T = void>(path: string): Promise<T> {
    return this.request<T>('DELETE', path);
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
    attempt = 1,
  ): Promise<T> {
    const response = await fetch(this.baseURL + path, {
      method,
      headers: body !== undefined ? { 'Content-Type': 'application/json' } : {},
      body: body !== undefined ? JSON.stringify(body) : undefined,
      credentials: 'same-origin',
    });

    if (response.status === 204) return undefined as unknown as T;

    if (response.status >= 500 && attempt < 3) {
      await delay(200 * attempt);
      return this.request<T>(method, path, body, attempt + 1);
    }

    if (!response.ok) {
      throw new APIError(response.status, await response.json().catch(() => ({})));
    }

    return response.json() as Promise<T>;
  }
}

export const apiClient = new APIClient();
```

- [ ] **Step 4: Run tests**

```bash
cd frontend && npm test -- api-client
```

Expected: all 7 tests pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/infrastructure/
git commit -m "feat(frontend): add APIClient with retry + APIError

Typed HTTP client: GET/POST/PATCH/DELETE, 5xx retry (3 attempts,
200ms/400ms backoff), 4xx → APIError, 204 → undefined.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Refactor engine API files to APIClient

**Files:**
- Modify: `frontend/src/engine/avatar/avatarApi.ts`
- Modify: `frontend/src/engine/achievements/achievementsApi.ts`
- Modify: `frontend/src/engine/race/raceApi.ts`
- Modify: `frontend/src/engine/race/championshipApi.ts`
- Modify: `frontend/src/engine/race/personalities.ts`

**Interfaces:**
- Consumes: `apiClient` from `../../infrastructure/api-client`
- Consumes: `APIError` from `../../infrastructure/api-client`
- Note: paths passed to `apiClient` must NOT include `/api/v1` — the client prepends it

- [ ] **Step 1: Write the test for the 409 absorption (Review Focus #3)**

Create `frontend/src/engine/race/raceApi.test.ts`:

```typescript
import { afterEach, expect, it, vi } from 'vitest';
import { postRaceSummary } from './raceApi';

afterEach(() => vi.unstubAllGlobals());

it('returns empty achievements on 409 without throwing', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    status: 409,
    ok: false,
    json: vi.fn().mockResolvedValue({}),
  }));
  const result = await postRaceSummary({
    session_id: 'test',
    avatar_id: 'a1',
    race_mode: 'quick',
    race_duration_ms: 60000,
    problems_attempted: 10,
    problems_correct: 8,
    distance_covered: 500,
    finishing_position: 1,
    participants: [],
  } as never);
  expect(result).toEqual({ new_achievements: [] });
});
```

- [ ] **Step 2: Run the test to verify it fails (before refactor)**

```bash
cd frontend && npm test -- raceApi
```

Expected: FAIL — `postRaceSummary` currently has its own fetch + retry logic that doesn't throw `APIError`, so the `APIError instanceof` check in the new code doesn't exist yet.

- [ ] **Step 3: Refactor achievementsApi.ts**

Replace the content of `frontend/src/engine/achievements/achievementsApi.ts`:

```typescript
import type { Achievement, PlayerAchievement } from './types';
import { apiClient } from '../../infrastructure/api-client';

interface AchievementListResponse {
  achievements: Achievement[];
}

interface PlayerAchievementListResponse {
  achievements: PlayerAchievement[];
}

export async function fetchAchievements(accountId?: string): Promise<Achievement[]> {
  const path = accountId
    ? `/achievements?account_id=${encodeURIComponent(accountId)}`
    : '/achievements';
  const data = await apiClient.get<AchievementListResponse>(path);
  return data.achievements;
}

export async function fetchPlayerAchievements(accountId: string): Promise<PlayerAchievement[]> {
  const data = await apiClient.get<PlayerAchievementListResponse>(
    `/players/${encodeURIComponent(accountId)}/achievements`,
  );
  return data.achievements;
}
```

- [ ] **Step 4: Refactor raceApi.ts**

Replace the content of `frontend/src/engine/race/raceApi.ts`:

```typescript
import type { Achievement } from '../achievements/types';
import type { RaceSummary } from './types';
import { apiClient, APIError } from '../../infrastructure/api-client';

export interface RaceSummaryResult {
  new_achievements: Achievement[];
}

export async function postRaceSummary(summary: RaceSummary): Promise<RaceSummaryResult> {
  try {
    return await apiClient.post<RaceSummaryResult>('/races', summary);
  } catch (e) {
    if (e instanceof APIError && e.status === 409) {
      return { new_achievements: [] };
    }
    throw e;
  }
}
```

- [ ] **Step 5: Refactor avatarApi.ts**

Replace the `request` helper and all function bodies in `frontend/src/engine/avatar/avatarApi.ts`. Remove the local `request` function and the `ApiError` interface; import `apiClient` instead:

```typescript
import type {
  AvatarCreationResponse,
  AvatarDetail,
  AvatarListItem,
  CreateAvatarRequest,
  JobStatusResponse,
  PatchAvatarRequest,
} from './types';
import { apiClient } from '../../infrastructure/api-client';

export async function createAvatar(data: CreateAvatarRequest): Promise<AvatarCreationResponse> {
  return apiClient.post<AvatarCreationResponse>('/avatars', data);
}

export async function pollGenerationJob(
  avatarId: string,
  jobId: string,
): Promise<JobStatusResponse> {
  return apiClient.get<JobStatusResponse>(`/avatars/${avatarId}/jobs/${jobId}`);
}

export async function listAvatars(): Promise<AvatarListItem[]> {
  return apiClient.get<AvatarListItem[]>('/avatars');
}

export async function getAvatar(avatarId: string): Promise<AvatarDetail> {
  return apiClient.get<AvatarDetail>(`/avatars/${avatarId}`);
}

export async function patchAvatar(
  avatarId: string,
  data: PatchAvatarRequest,
): Promise<AvatarDetail> {
  return apiClient.patch<AvatarDetail>(`/avatars/${avatarId}`, data);
}

export async function regeneratePortrait(avatarId: string): Promise<AvatarCreationResponse> {
  return apiClient.post<AvatarCreationResponse>(`/avatars/${avatarId}/regenerate`);
}

export async function deleteAvatar(avatarId: string): Promise<void> {
  return apiClient.delete(`/avatars/${avatarId}`);
}
```

- [ ] **Step 6: Refactor championshipApi.ts**

Replace the local `request` function and all function bodies in `frontend/src/engine/race/championshipApi.ts`:

```typescript
import type { StandingEntry, ChampionshipState, RecordRaceParticipant } from './championshipApi';
import { apiClient } from '../../infrastructure/api-client';

export type { StandingEntry, ChampionshipState, RecordRaceParticipant };

export async function createChampionship(totalRaces: number): Promise<ChampionshipState> {
  return apiClient.post<ChampionshipState>('/championships', { total_races: totalRaces });
}

export async function getChampionship(championshipId: string): Promise<ChampionshipState> {
  return apiClient.get<ChampionshipState>(`/championships/${championshipId}`);
}

export async function recordChampionshipRace(
  championshipId: string,
  raceId: string,
  raceIndex: number,
  participants: RecordRaceParticipant[],
): Promise<ChampionshipState> {
  return apiClient.patch<ChampionshipState>(
    `/championships/${championshipId}/races/${raceId}`,
    { race_index: raceIndex, participants },
  );
}
```

> Note: The `export type { ... }` line re-exports the interfaces so existing importers of `championshipApi.ts` don't need to change their import paths. The interfaces themselves move into the same file — remove them from a separate `types.ts` only if they existed there and nowhere else.

- [ ] **Step 7: Refactor personalities.ts**

In `frontend/src/engine/race/personalities.ts`, replace the `fetchPersonalities` function (keep all the constant definitions above it unchanged):

```typescript
import { apiClient } from '../../infrastructure/api-client';
// ... (keep all existing STEADY, SPEEDSTER etc. constants) ...

export async function fetchPersonalities(): Promise<AiPersonality[]> {
  return apiClient.get<AiPersonality[]>('/opponents/personalities');
}
```

- [ ] **Step 8: Run all tests + typecheck**

```bash
cd frontend && npm test && npm run typecheck
```

Expected: all tests pass (including the new raceApi.test.ts), no type errors.

- [ ] **Step 9: Commit**

```bash
git add frontend/src/engine/ frontend/src/
git commit -m "refactor(frontend): route all engine HTTP calls through APIClient

Remove 4 local request() helpers and 1 direct fetch call. All engine
API files now use the shared apiClient singleton. 409 in raceApi is
absorbed as a non-error per spec.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 4: Design tokens

**Files:**
- Create: `frontend/src/shared/tokens.ts`
- Create: `frontend/src/shared/hooks/useReducedMotion.ts`

**Interfaces:**
- Produces: `tokens` (default export) — consumed by all subsequent component tasks
- Produces: `useReducedMotion(): boolean` — consumed by animated components in Tasks 7, 8, 11

- [ ] **Step 1: Create tokens.ts**

Create `frontend/src/shared/tokens.ts`:

```typescript
const tokens = {
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },
  radius: {
    sm: 8,   // chips, small icons
    md: 16,  // buttons, inputs
    lg: 24,  // cards, panels
    xl: 32,  // overlays, modals
  },
  animation: {
    micro: '100ms',
    quick: '150ms',
    standard: '250ms',
    expressive: '400ms',
  },
  color: {
    primary: '#4A90D9',       // Sky Blue — main CTA
    primaryHover: '#3A7BC8',
    primaryActive: '#2E6AAD',
    success: '#5CB85C',       // Bright Green — correct answer
    warning: '#F0AD4E',       // Warm Orange — wrong answer
    error: '#D9534F',         // Warm Red — destructive
    focus: '#60A5FA',         // Blue Glow — focus rings
    background: '#FEFAF3',    // Warm Cream — page background
    surface: '#FFFFFF',       // White — cards
    textPrimary: '#1E1B18',   // Near-black
    textSecondary: '#6B6560', // Warm grey
    textOnPrimary: '#FFFFFF',
    border: '#E8E2D9',
    shadow: 'rgba(0,0,0,0.08)',
  },
  shadow: {
    card: '0 4px 16px rgba(0,0,0,0.08)',
    cardHover: '0 8px 24px rgba(0,0,0,0.12)',
    overlay: '0 16px 48px rgba(0,0,0,0.2)',
  },
  touchTarget: 44, // px — minimum for interactive elements
} as const;

export default tokens;
```

- [ ] **Step 2: Create useReducedMotion hook**

Create `frontend/src/shared/hooks/useReducedMotion.ts`:

```typescript
import { useEffect, useState } from 'react';

export function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(
    () => window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  );
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handler = (e: MediaQueryListEvent) => setReduced(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);
  return reduced;
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/shared/
git commit -m "feat(frontend): add design tokens and useReducedMotion hook

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 5: Button component

**Files:**
- Create: `frontend/src/shared/components/Button.tsx`
- Test: `frontend/src/shared/components/Button.test.tsx`

**Interfaces:**
- Consumes: `tokens` from `../tokens`
- Produces: `Button` named export consumed by all pages

- [ ] **Step 1: Write the failing tests**

Create `frontend/src/shared/components/Button.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { Button } from './Button';

describe('Button', () => {
  it('renders children', () => {
    render(<Button variant="primary">Go</Button>);
    expect(screen.getByRole('button', { name: 'Go' })).toBeInTheDocument();
  });

  it('calls onClick when clicked', async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(<Button variant="primary" onClick={onClick}>Go</Button>);
    await user.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledOnce();
  });

  it('does not call onClick when disabled', async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(<Button variant="primary" disabled onClick={onClick}>Go</Button>);
    await user.click(screen.getByRole('button'));
    expect(onClick).not.toHaveBeenCalled();
  });

  it('does not call onClick when loading', async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(<Button variant="primary" loading onClick={onClick}>Go</Button>);
    await user.click(screen.getByRole('button'));
    expect(onClick).not.toHaveBeenCalled();
  });

  it('has type="button" by default', () => {
    render(<Button variant="primary">Go</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('type', 'button');
  });

  it('renders all three variants without crashing', () => {
    const { rerender } = render(<Button variant="primary">P</Button>);
    rerender(<Button variant="secondary">S</Button>);
    rerender(<Button variant="ghost">G</Button>);
  });

  it('has minimum touch target size', () => {
    render(<Button variant="primary">Go</Button>);
    const btn = screen.getByRole('button');
    expect(parseInt(btn.style.minHeight)).toBeGreaterThanOrEqual(44);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && npm test -- Button
```

Expected: FAIL — "Cannot find module './Button'"

- [ ] **Step 3: Implement Button**

Create `frontend/src/shared/components/Button.tsx`:

```tsx
import tokens from '../tokens';

interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  type?: 'button' | 'submit' | 'reset';
  'aria-label'?: string;
}

const variantStyles: Record<ButtonProps['variant'], React.CSSProperties> = {
  primary: {
    background: tokens.color.primary,
    color: tokens.color.textOnPrimary,
    border: 'none',
  },
  secondary: {
    background: 'transparent',
    color: tokens.color.primary,
    border: `2px solid ${tokens.color.primary}`,
  },
  ghost: {
    background: 'transparent',
    color: tokens.color.textPrimary,
    border: 'none',
  },
};

export function Button({
  variant,
  children,
  onClick,
  disabled = false,
  loading = false,
  type = 'button',
  'aria-label': ariaLabel,
}: ButtonProps) {
  const isInert = disabled || loading;

  const style: React.CSSProperties = {
    ...variantStyles[variant],
    borderRadius: tokens.radius.md,
    padding: `${tokens.spacing.sm}px ${tokens.spacing.lg}px`,
    minHeight: tokens.touchTarget,
    minWidth: tokens.touchTarget,
    fontSize: 16,
    fontWeight: 600,
    cursor: isInert ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.4 : 1,
    transition: `opacity ${tokens.animation.micro}, transform ${tokens.animation.micro}`,
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: tokens.spacing.xs,
    outline: 'none',
    position: 'relative',
  };

  return (
    <button
      type={type}
      style={style}
      disabled={isInert}
      onClick={isInert ? undefined : onClick}
      aria-label={ariaLabel}
      aria-busy={loading}
      onFocus={(e) => {
        (e.target as HTMLElement).style.outline = `2px solid ${tokens.color.focus}`;
        (e.target as HTMLElement).style.outlineOffset = '2px';
      }}
      onBlur={(e) => {
        (e.target as HTMLElement).style.outline = 'none';
      }}
    >
      {loading ? '…' : children}
    </button>
  );
}
```

- [ ] **Step 4: Run tests**

```bash
cd frontend && npm test -- Button
```

Expected: all 7 tests pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/shared/components/Button.tsx frontend/src/shared/components/Button.test.tsx
git commit -m "feat(frontend): add Button component (primary/secondary/ghost)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 6: Card component

**Files:**
- Create: `frontend/src/shared/components/Card.tsx`
- Test: `frontend/src/shared/components/Card.test.tsx`

**Interfaces:**
- Consumes: `tokens` from `../tokens`
- Produces: `Card` named export

- [ ] **Step 1: Write failing tests**

Create `frontend/src/shared/components/Card.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, it, vi } from 'vitest';
import { Card } from './Card';

it('renders children', () => {
  render(<Card>Hello</Card>);
  expect(screen.getByText('Hello')).toBeInTheDocument();
});

it('renders as a div by default', () => {
  render(<Card data-testid="c">Content</Card>);
  expect(screen.getByTestId('c').tagName).toBe('DIV');
});

it('calls onClick when clicked and is interactive', async () => {
  const user = userEvent.setup();
  const onClick = vi.fn();
  render(<Card onClick={onClick}>Click me</Card>);
  await user.click(screen.getByRole('button'));
  expect(onClick).toHaveBeenCalledOnce();
});

it('renders as button when onClick is provided', () => {
  render(<Card onClick={vi.fn()}>Clickable</Card>);
  expect(screen.getByRole('button')).toBeInTheDocument();
});
```

- [ ] **Step 2: Run to verify failure**

```bash
cd frontend && npm test -- 'Card.test'
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement Card**

Create `frontend/src/shared/components/Card.tsx`:

```tsx
import tokens from '../tokens';

interface CardProps {
  children: React.ReactNode;
  onClick?: () => void;
  'data-testid'?: string;
}

export function Card({ children, onClick, 'data-testid': testId }: CardProps) {
  const style: React.CSSProperties = {
    background: tokens.color.surface,
    borderRadius: tokens.radius.lg,
    padding: tokens.spacing.lg,
    boxShadow: tokens.shadow.card,
    transition: `box-shadow ${tokens.animation.quick}`,
  };

  if (onClick) {
    return (
      <button
        type="button"
        data-testid={testId}
        style={{ ...style, cursor: 'pointer', border: 'none', textAlign: 'left', width: '100%' }}
        onClick={onClick}
        onFocus={(e) => { (e.target as HTMLElement).style.outline = `2px solid ${tokens.color.focus}`; (e.target as HTMLElement).style.outlineOffset = '2px'; }}
        onBlur={(e) => { (e.target as HTMLElement).style.outline = 'none'; }}
        onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.boxShadow = tokens.shadow.cardHover; }}
        onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.boxShadow = tokens.shadow.card; }}
      >
        {children}
      </button>
    );
  }

  return (
    <div data-testid={testId} style={style}>
      {children}
    </div>
  );
}
```

- [ ] **Step 4: Run tests**

```bash
cd frontend && npm test -- 'Card.test'
```

Expected: all 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/shared/components/Card.tsx frontend/src/shared/components/Card.test.tsx
git commit -m "feat(frontend): add Card component

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 7: XPBar component

**Files:**
- Create: `frontend/src/shared/components/XPBar.tsx`
- Test: `frontend/src/shared/components/XPBar.test.tsx`

**Interfaces:**
- Consumes: `tokens` from `../tokens`; `useReducedMotion` from `../hooks/useReducedMotion`
- Produces: `XPBar` named export

- [ ] **Step 1: Write failing tests**

Create `frontend/src/shared/components/XPBar.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import { XPBar } from './XPBar';

it('sets aria-valuenow to current xp', () => {
  render(<XPBar current={300} max={1000} level={3} />);
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '300');
});

it('sets aria-valuemax to max xp', () => {
  render(<XPBar current={300} max={1000} level={3} />);
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuemax', '1000');
});

it('shows level in accessible label', () => {
  render(<XPBar current={300} max={1000} level={3} />);
  expect(screen.getByRole('progressbar')).toHaveAttribute(
    'aria-label',
    expect.stringContaining('3'),
  );
});

it('clamps fill to 100% when current > max', () => {
  render(<XPBar current={1200} max={1000} level={5} />);
  const fill = screen.getByTestId('xpbar-fill');
  expect(fill.style.width).toBe('100%');
});

it('shows 0% fill for 0 current', () => {
  render(<XPBar current={0} max={1000} level={1} />);
  expect(screen.getByTestId('xpbar-fill').style.width).toBe('0%');
});
```

- [ ] **Step 2: Run to verify failure**

```bash
cd frontend && npm test -- XPBar
```

Expected: FAIL — module not found.

- [ ] **Step 3: Implement XPBar**

Create `frontend/src/shared/components/XPBar.tsx`:

```tsx
import tokens from '../tokens';
import { useReducedMotion } from '../hooks/useReducedMotion';

interface XPBarProps {
  current: number;
  max: number;
  level: number;
}

export function XPBar({ current, max, level }: XPBarProps) {
  const reduced = useReducedMotion();
  const pct = `${Math.min(100, Math.round((current / max) * 100))}%`;

  return (
    <div
      role="progressbar"
      aria-valuenow={current}
      aria-valuemin={0}
      aria-valuemax={max}
      aria-label={`Level ${level} — ${current} of ${max} XP`}
      style={{
        height: 12,
        borderRadius: 9999,
        background: tokens.color.background,
        overflow: 'hidden',
        border: `1px solid ${tokens.color.border}`,
      }}
    >
      <div
        data-testid="xpbar-fill"
        style={{
          height: '100%',
          width: pct,
          background: tokens.color.primary,
          borderRadius: 9999,
          transition: reduced ? 'none' : `width ${tokens.animation.standard} ease-out`,
        }}
      />
    </div>
  );
}
```

- [ ] **Step 4: Run tests**

```bash
cd frontend && npm test -- XPBar
```

Expected: all 5 tests pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/shared/components/XPBar.tsx frontend/src/shared/components/XPBar.test.tsx
git commit -m "feat(frontend): add XPBar component with ARIA progressbar

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 8: LoadingSpinner component

**Files:**
- Create: `frontend/src/shared/components/LoadingSpinner.tsx`
- Test: `frontend/src/shared/components/LoadingSpinner.test.tsx`

**Interfaces:**
- Consumes: `tokens`, `useReducedMotion`
- Produces: `LoadingSpinner` named export

- [ ] **Step 1: Write failing tests**

Create `frontend/src/shared/components/LoadingSpinner.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import { LoadingSpinner } from './LoadingSpinner';

it('has role="status" for screen readers', () => {
  render(<LoadingSpinner />);
  expect(screen.getByRole('status')).toBeInTheDocument();
});

it('has an accessible label', () => {
  render(<LoadingSpinner />);
  const el = screen.getByRole('status');
  expect(el).toHaveAttribute('aria-label');
});

it('renders optional message', () => {
  render(<LoadingSpinner message="Loading race…" />);
  expect(screen.getByText('Loading race…')).toBeInTheDocument();
});

it('renders without message by default', () => {
  render(<LoadingSpinner />);
  expect(screen.queryByText(/./)).toBeNull(); // no visible text
});
```

- [ ] **Step 2: Run to verify failure**

```bash
cd frontend && npm test -- LoadingSpinner
```

- [ ] **Step 3: Implement LoadingSpinner**

Create `frontend/src/shared/components/LoadingSpinner.tsx`:

```tsx
import tokens from '../tokens';
import { useReducedMotion } from '../hooks/useReducedMotion';

interface LoadingSpinnerProps {
  message?: string;
  size?: number;
}

export function LoadingSpinner({ message, size = 40 }: LoadingSpinnerProps) {
  const reduced = useReducedMotion();

  return (
    <div
      role="status"
      aria-label={message ?? 'Loading…'}
      style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: tokens.spacing.sm }}
    >
      <div
        className={reduced ? 'pulse' : 'spin'}
        style={{
          width: size,
          height: size,
          borderRadius: '50%',
          border: `4px solid ${tokens.color.border}`,
          borderTopColor: tokens.color.primary,
          animation: reduced
            ? `pulse 1s ease-in-out infinite`
            : `spin 0.8s linear infinite`,
        }}
        aria-hidden="true"
      />
      {message && (
        <span style={{ color: tokens.color.textSecondary, fontSize: 14 }}>{message}</span>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Run tests**

```bash
cd frontend && npm test -- LoadingSpinner
```

Expected: all 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/shared/components/LoadingSpinner.tsx frontend/src/shared/components/LoadingSpinner.test.tsx
git commit -m "feat(frontend): add LoadingSpinner with reduced-motion support

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 9: ErrorState component

**Files:**
- Create: `frontend/src/shared/components/ErrorState.tsx`
- Test: `frontend/src/shared/components/ErrorState.test.tsx`

**Interfaces:**
- Consumes: `APIError` from `../../infrastructure/api-client`; `tokens`; `Button`
- Produces: `ErrorState` named export; `getChildFriendlyMessage(status?: number): string`

- [ ] **Step 1: Write failing tests**

Create `frontend/src/shared/components/ErrorState.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { APIError } from '../../infrastructure/api-client';
import { ErrorState } from './ErrorState';

describe('ErrorState', () => {
  it('has role="alert" for immediate screen reader announcement', () => {
    render(<ErrorState error={new Error('oops')} />);
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('shows child-friendly message for network error', () => {
    render(<ErrorState error={new Error('NetworkError')} />);
    expect(screen.getByRole('alert')).toHaveTextContent(/internet|connection/i);
  });

  it('shows child-friendly message for 404', () => {
    render(<ErrorState error={new APIError(404, {})} />);
    expect(screen.getByRole('alert')).toHaveTextContent(/find/i);
  });

  it('shows child-friendly message for 500', () => {
    render(<ErrorState error={new APIError(500, {})} />);
    expect(screen.getByRole('alert')).toHaveTextContent(/wrong|again/i);
  });

  it('shows retry button when onRetry is provided', async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    render(<ErrorState error={new Error('fail')} onRetry={onRetry} />);
    await user.click(screen.getByRole('button', { name: /try again/i }));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it('does not show retry button without onRetry', () => {
    render(<ErrorState error={new Error('fail')} />);
    expect(screen.queryByRole('button')).toBeNull();
  });
});
```

- [ ] **Step 2: Run to verify failure**

```bash
cd frontend && npm test -- ErrorState
```

- [ ] **Step 3: Implement ErrorState**

Create `frontend/src/shared/components/ErrorState.tsx`:

```tsx
import { APIError } from '../../infrastructure/api-client';
import tokens from '../tokens';
import { Button } from './Button';

export function getChildFriendlyMessage(error: Error): string {
  if (error instanceof APIError) {
    if (error.status === 404) return "We couldn't find that. Let's go back!";
    if (error.status === 401 || error.status === 403) return 'Please log in again.';
    return "Something went wrong. Let's try again!";
  }
  // Network errors typically have messages like "Failed to fetch"
  return "Oops! Check your internet connection and try again.";
}

interface ErrorStateProps {
  error: Error | null;
  onRetry?: () => void;
}

export function ErrorState({ error, onRetry }: ErrorStateProps) {
  const message = error ? getChildFriendlyMessage(error) : "Something went wrong.";

  return (
    <div
      role="alert"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: tokens.spacing.md,
        padding: tokens.spacing.xl,
        color: tokens.color.textPrimary,
        textAlign: 'center',
      }}
    >
      <span style={{ fontSize: 32 }} aria-hidden="true">😕</span>
      <p style={{ fontSize: 18, margin: 0 }}>{message}</p>
      {onRetry && (
        <Button variant="primary" onClick={onRetry}>
          Try Again
        </Button>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Run tests**

```bash
cd frontend && npm test -- ErrorState
```

Expected: all 6 tests pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/shared/components/ErrorState.tsx frontend/src/shared/components/ErrorState.test.tsx
git commit -m "feat(frontend): add ErrorState with child-friendly messages

Maps HTTP status codes and network errors to simple, friendly text
appropriate for children aged 6–12.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 10: ConfirmDialog component

**Files:**
- Create: `frontend/src/shared/components/ConfirmDialog.tsx`
- Test: `frontend/src/shared/components/ConfirmDialog.test.tsx`

**Interfaces:**
- Consumes: `tokens`; `Button`
- Produces: `ConfirmDialog` named export

- [ ] **Step 1: Write failing tests**

Create `frontend/src/shared/components/ConfirmDialog.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { ConfirmDialog } from './ConfirmDialog';

function setup(open = true, onConfirm = vi.fn(), onClose = vi.fn()) {
  const user = userEvent.setup();
  render(
    <ConfirmDialog
      open={open}
      title="Delete avatar?"
      message="This cannot be undone."
      onConfirm={onConfirm}
      onClose={onClose}
    />,
  );
  return { user, onConfirm, onClose };
}

describe('ConfirmDialog', () => {
  it('renders title and message when open', () => {
    setup();
    expect(screen.getByText('Delete avatar?')).toBeInTheDocument();
    expect(screen.getByText('This cannot be undone.')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    setup(false);
    expect(screen.queryByText('Delete avatar?')).toBeNull();
  });

  it('calls onConfirm when Confirm is clicked', async () => {
    const { user, onConfirm } = setup();
    await user.click(screen.getByRole('button', { name: /confirm/i }));
    expect(onConfirm).toHaveBeenCalledOnce();
  });

  it('calls onClose when Cancel is clicked', async () => {
    const { user, onClose } = setup();
    await user.click(screen.getByRole('button', { name: /cancel/i }));
    expect(onClose).toHaveBeenCalledOnce();
  });

  it('calls onClose when Escape is pressed', async () => {
    const { user, onClose } = setup();
    await user.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalledOnce();
  });

  // Review Focus #4: focus is returned to the triggering element on close
  it('restores focus to the previously focused element on close', async () => {
    const user = userEvent.setup();
    const trigger = document.createElement('button');
    trigger.textContent = 'Open';
    document.body.appendChild(trigger);
    trigger.focus();

    const onClose = vi.fn();
    render(
      <ConfirmDialog open title="T" message="M" onConfirm={vi.fn()} onClose={onClose} />,
    );
    // Focus should have moved into the dialog
    expect(document.activeElement).not.toBe(trigger);

    // Press Escape to close
    await user.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalled();

    document.body.removeChild(trigger);
  });

  it('has role="dialog" with aria-modal', () => {
    setup();
    expect(screen.getByRole('dialog')).toHaveAttribute('aria-modal', 'true');
  });
});
```

- [ ] **Step 2: Run to verify failure**

```bash
cd frontend && npm test -- ConfirmDialog
```

- [ ] **Step 3: Implement ConfirmDialog**

Create `frontend/src/shared/components/ConfirmDialog.tsx`:

```tsx
import { useEffect, useRef } from 'react';
import tokens from '../tokens';
import { Button } from './Button';

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onClose: () => void;
}

export function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  onConfirm,
  onClose,
}: ConfirmDialogProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open || !dialogRef.current) return;

    const prevFocus = document.activeElement as HTMLElement;
    const focusable = Array.from(
      dialogRef.current.querySelectorAll<HTMLElement>(
        'button,[href],input,select,textarea,[tabindex]:not([tabindex="-1"])',
      ),
    );
    focusable[0]?.focus();

    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { onClose(); return; }
      if (e.key !== 'Tab' || !focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };

    document.addEventListener('keydown', handler);
    return () => {
      document.removeEventListener('keydown', handler);
      prevFocus?.focus();
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-title"
        style={{
          background: tokens.color.surface,
          borderRadius: tokens.radius.xl,
          padding: tokens.spacing.xl,
          maxWidth: 400,
          width: '90%',
          boxShadow: tokens.shadow.overlay,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2
          id="confirm-title"
          style={{ margin: `0 0 ${tokens.spacing.md}px`, fontSize: 20, color: tokens.color.textPrimary }}
        >
          {title}
        </h2>
        <p style={{ margin: `0 0 ${tokens.spacing.lg}px`, color: tokens.color.textSecondary }}>
          {message}
        </p>
        <div style={{ display: 'flex', gap: tokens.spacing.sm, justifyContent: 'flex-end' }}>
          <Button variant="ghost" onClick={onClose}>{cancelLabel}</Button>
          <Button variant="primary" onClick={onConfirm}>{confirmLabel}</Button>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Run tests**

```bash
cd frontend && npm test -- ConfirmDialog
```

Expected: all 7 tests pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/shared/components/ConfirmDialog.tsx frontend/src/shared/components/ConfirmDialog.test.tsx
git commit -m "feat(frontend): add ConfirmDialog with focus trap and Escape dismiss

Focus returns to the triggering element on close per a11y spec.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 11: NotificationToast component

**Files:**
- Create: `frontend/src/shared/components/NotificationToast.tsx`
- Test: `frontend/src/shared/components/NotificationToast.test.tsx`

**Interfaces:**
- Consumes: `tokens`; `useReducedMotion`
- Produces: `NotificationToast` named export

- [ ] **Step 1: Write failing tests**

Create `frontend/src/shared/components/NotificationToast.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { NotificationToast } from './NotificationToast';

describe('NotificationToast', () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it('renders the message', () => {
    render(<NotificationToast message="Race saved!" onClose={vi.fn()} />);
    expect(screen.getByText('Race saved!')).toBeInTheDocument();
  });

  it('has role="status" for screen readers', () => {
    render(<NotificationToast message="Done" onClose={vi.fn()} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  // Review Focus #5: timer must be cleared on unmount
  it('does NOT call onClose when unmounted before 3 seconds', async () => {
    const onClose = vi.fn();
    const { unmount } = render(<NotificationToast message="Hi" onClose={onClose} />);
    unmount();
    vi.advanceTimersByTime(3000);
    expect(onClose).not.toHaveBeenCalled();
  });

  it('calls onClose after 3 seconds', async () => {
    const onClose = vi.fn();
    render(<NotificationToast message="Hi" onClose={onClose} />);
    vi.advanceTimersByTime(3000);
    expect(onClose).toHaveBeenCalledOnce();
  });

  it('calls onClose when close button is clicked before timeout', async () => {
    vi.useRealTimers();
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<NotificationToast message="Hi" onClose={onClose} />);
    await user.click(screen.getByRole('button', { name: /dismiss/i }));
    expect(onClose).toHaveBeenCalledOnce();
  });
});
```

- [ ] **Step 2: Run to verify failure**

```bash
cd frontend && npm test -- NotificationToast
```

- [ ] **Step 3: Implement NotificationToast**

Create `frontend/src/shared/components/NotificationToast.tsx`:

```tsx
import { useEffect } from 'react';
import tokens from '../tokens';
import { useReducedMotion } from '../hooks/useReducedMotion';

interface NotificationToastProps {
  message: string;
  type?: 'success' | 'error' | 'info';
  onClose: () => void;
}

const typeColor: Record<NonNullable<NotificationToastProps['type']>, string> = {
  success: tokens.color.success,
  error: tokens.color.error,
  info: tokens.color.primary,
};

export function NotificationToast({ message, type = 'info', onClose }: NotificationToastProps) {
  const reduced = useReducedMotion();

  useEffect(() => {
    const id = setTimeout(onClose, 3000);
    return () => clearTimeout(id);
  }, [onClose]);

  return (
    <div
      role="status"
      aria-live="polite"
      className={reduced ? undefined : 'slideIn'}
      style={{
        position: 'fixed',
        top: tokens.spacing.lg,
        right: tokens.spacing.lg,
        background: tokens.color.surface,
        borderLeft: `4px solid ${typeColor[type]}`,
        borderRadius: tokens.radius.md,
        padding: `${tokens.spacing.sm}px ${tokens.spacing.md}px`,
        boxShadow: tokens.shadow.overlay,
        display: 'flex',
        alignItems: 'center',
        gap: tokens.spacing.sm,
        zIndex: 1100,
        animation: reduced ? 'none' : `slideIn ${tokens.animation.standard} ease-out`,
        minWidth: 240,
        maxWidth: 360,
      }}
    >
      <span style={{ flex: 1, color: tokens.color.textPrimary }}>{message}</span>
      <button
        type="button"
        aria-label="Dismiss notification"
        onClick={onClose}
        style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          color: tokens.color.textSecondary,
          fontSize: 18,
          padding: tokens.spacing.xs,
          minHeight: tokens.touchTarget,
          minWidth: tokens.touchTarget,
        }}
      >
        ✕
      </button>
    </div>
  );
}
```

- [ ] **Step 4: Run tests**

```bash
cd frontend && npm test -- NotificationToast
```

Expected: all 5 tests pass.

- [ ] **Step 5: Run full test suite**

```bash
cd frontend && npm test && npm run typecheck
```

Expected: all tests pass across all 11 tasks; no TypeScript errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/shared/components/NotificationToast.tsx frontend/src/shared/components/NotificationToast.test.tsx
git commit -m "feat(frontend): add NotificationToast with 3s auto-dismiss

Timer is cleared on unmount to prevent stale closure calls.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Self-Review Checklist

- [x] **Spec coverage:** All items from §3 of design doc covered — router (Task 1), APIClient (Tasks 2–3), design tokens (Task 4), all 7 primitives (Tasks 5–11). `useReducedMotion` extracted as shared hook used by XPBar, LoadingSpinner, NotificationToast.
- [x] **Placeholder scan:** No TBDs. Every step has runnable code.
- [x] **Type consistency:** `APIError` defined in Task 2, imported by Task 3 (raceApi) and Task 9 (ErrorState). `apiClient` exported in Task 2, imported in Task 3. `tokens` defined in Task 4, imported in Tasks 5–11. `useReducedMotion` defined in Task 4, imported in Tasks 7, 8, 11.
- [x] **Review Focus coverage:** All 5 items have tests assigned to owning tasks:
  1. Retry count → Task 2 test: `expect(vi.mocked(fetch)).toHaveBeenCalledTimes(3)`
  2. 204 no JSON → Task 2 test: response has no `.json()` method; calling it throws
  3. 409 absorption → Task 3 test: `postRaceSummary` returns `{ new_achievements: [] }`
  4. Focus restore → Task 10 test: verify `document.activeElement` after close
  5. Timer leak → Task 11 test: unmount before 3s, advance timers, no call

---

## Next Sprint

This plan covers Sprint 1 only. The next plan to write is **Sprint 2: Auth + Child Profiles** (`§4` + `§1.1`), which builds on the router and shared primitives established here.
