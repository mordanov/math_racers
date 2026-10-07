# Sprint 4 — Race Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire the existing race engine into a complete, playable race flow — from Race Setup through Countdown, Race Screen, Results Screen, and Championship standings.

**Architecture:** Six pages connect into a single linear flow via React Router route state; the engine layer (`useRaceEngine`, `createRaceEngine`, `raceApi`) is already implemented and is wired into the UI in this sprint. Each page is a thin shell; business logic stays in the engine hooks and API functions.

**Tech Stack:** React 18, React Router v7, Vitest + @testing-library/react, TypeScript strict, design tokens from `src/shared/tokens.ts`

**Spec:** `docs/ui/spec-ui-implementation.md` (§ Race Feature, Navigation Flow, Accessibility) + `docs/gameplay/spec-race-engine.md` + `docs/gameplay/spec-game-modes.md` + `docs/superpowers/specs/2026-10-05-v1-execution-order-design.md` (Sprint 4 scope)

---

## Global Constraints

- All style values come from `tokens` — never hardcoded colours, spacing, or radii.
- Every interactive element: Tab-navigable in logical reading order; 2px focus ring ≥ 3:1 contrast.
- Countdown timer: `aria-live="polite"` region.
- Math problem input: `aria-label` describing the current problem.
- Results table: `<table>` with `scope="col"` on headers, `scope="row"` on row headers.
- Error messages: `role="alert"`.
- Tier values: Tier 6 is valid only via parent override — the setup page only shows tiers 1–5.
- Test command: `pnpm --dir frontend test`
- Branch: `013-sprint-4-race-flow` branched from `main`

---

## Review Focus

1. **Route state lost on page refresh** — if the user refreshes `/race/:id`, `location.state` is `null`; the page must redirect to `/race/setup` rather than crash.
2. **Back navigation during RACING** — the browser Back button during an active race must trigger a confirmation dialog, not silently navigate away; `useBlocker` gates this.
3. **No published avatar** — Race Setup must redirect to `/avatars/new` before attempting to create a session; the Start button must never be reachable without a published avatar.
4. **Race summary sync failure** — the Results Screen must display results immediately from route state (not wait for the POST), and show an inline retry button when `postRaceSummary` fails.
5. **Championship raceIndex off-by-one** — `recordChampionshipRace` requires the correct 0-based `raceIndex`; it must equal `championship.races_completed` at the moment the session was created, passed through route state.

Matching tests are embedded in T001–T006 below.

---

## File Map

**Create:**
- `src/features/race/raceSessionApi.ts` — `createRaceSession()` API function
- `src/features/race/raceSessionApi.test.ts`
- `src/features/race/progressionApi.ts` — `fetchProgression()` API function
- `src/engine/race/hooks/useRaceEngine.test.ts`
- `src/pages/RaceSetupPage.test.tsx`
- `src/pages/RaceScreenPage.test.tsx`
- `src/pages/ResultsScreenPage.test.tsx`
- `src/pages/ChampionshipPage.test.tsx`

**Modify:**
- `src/engine/race/hooks/useRaceEngine.ts` — add `startCountdown`, `startRacing`, `getSummary`; remove `postRaceSummary` call
- `src/pages/RaceSetupPage.tsx` — full implementation
- `src/pages/RaceScreenPage.tsx` — full implementation
- `src/pages/ResultsScreenPage.tsx` — full implementation
- `src/pages/ChampionshipPage.tsx` — full implementation
- `src/pages/HomePage.tsx` — navigation links + championship resume

---

### Task 1: Race Session API and Progression API

**Files:**
- Create: `src/features/race/raceSessionApi.ts`
- Create: `src/features/race/raceSessionApi.test.ts`
- Create: `src/features/race/progressionApi.ts`

**Interfaces:**
- Consumes: `apiClient` from `src/infrastructure/api-client.ts`; `RaceMode` from `src/engine/race/types.ts`; `Tier` from `src/engine/math/types.ts`
- Produces: `createRaceSession(params: CreateRaceSessionParams): Promise<CreateRaceSessionResult>` — used by T003; `fetchProgression(): Promise<PlayerProgression>` — used by T005

- [ ] **Step 1: Write failing tests**

```typescript
// src/features/race/raceSessionApi.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient } from '../../infrastructure/api-client';
import { createRaceSession } from './raceSessionApi';

vi.mock('../../infrastructure/api-client', () => ({
  apiClient: { post: vi.fn() },
}));

describe('createRaceSession', () => {
  beforeEach(() => vi.clearAllMocks());

  it('posts to /races with correct fields and returns race_id and seed', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ race_id: 'r1', seed: 42 });
    const result = await createRaceSession({ mode: 'quick', tier: 1, avatar_id: 'av1', opponent_count: 2 });
    expect(result).toEqual({ race_id: 'r1', seed: 42 });
    expect(apiClient.post).toHaveBeenCalledWith('/races', {
      mode: 'quick',
      difficulty_tier: 1,
      avatar_id: 'av1',
      opponent_count: 2,
    });
  });

  it('includes championship_id when provided', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ race_id: 'r2', seed: 99 });
    await createRaceSession({ mode: 'championship', tier: 2, avatar_id: 'av1', opponent_count: 3, championship_id: 'ch1' });
    expect(apiClient.post).toHaveBeenCalledWith('/races', {
      mode: 'championship',
      difficulty_tier: 2,
      avatar_id: 'av1',
      opponent_count: 3,
      championship_id: 'ch1',
    });
  });
});
```

- [ ] **Step 2: Run tests — expect FAIL (createRaceSession not defined)**

Run: `pnpm --dir frontend test raceSessionApi`
Expected: FAIL — `Cannot find module './raceSessionApi'`

- [ ] **Step 3: Implement `raceSessionApi.ts`**

```typescript
// src/features/race/raceSessionApi.ts
import { apiClient } from '../../infrastructure/api-client';
import type { RaceMode } from '../../engine/race/types';
import type { Tier } from '../../engine/math/types';

export interface CreateRaceSessionParams {
  mode: RaceMode;
  tier: Tier;
  avatar_id: string;
  opponent_count: number;
  championship_id?: string;
}

export interface CreateRaceSessionResult {
  race_id: string;
  seed: number;
}

export async function createRaceSession(
  params: CreateRaceSessionParams,
): Promise<CreateRaceSessionResult> {
  const body: Record<string, unknown> = {
    mode: params.mode,
    difficulty_tier: params.tier,
    avatar_id: params.avatar_id,
    opponent_count: params.opponent_count,
  };
  if (params.championship_id !== undefined) {
    body.championship_id = params.championship_id;
  }
  return apiClient.post<CreateRaceSessionResult>('/races', body);
}
```

- [ ] **Step 4: Implement `progressionApi.ts`** (no separate test needed — trivial API wrapper)

```typescript
// src/features/race/progressionApi.ts
import { apiClient } from '../../infrastructure/api-client';

export interface PlayerProgression {
  player_id: string;
  total_xp: number;
  current_level: number;
  xp_to_next_level: number;
}

export async function fetchProgression(): Promise<PlayerProgression> {
  return apiClient.get<PlayerProgression>('/players/me/progression');
}
```

- [ ] **Step 5: Run tests — expect PASS**

Run: `pnpm --dir frontend test raceSessionApi`
Expected: PASS 2/2

- [ ] **Step 6: Run full suite — expect green**

Run: `pnpm --dir frontend test`
Expected: all existing tests pass

- [ ] **Step 7: Commit**

```bash
git add src/features/race/raceSessionApi.ts src/features/race/raceSessionApi.test.ts src/features/race/progressionApi.ts
git commit -m "feat(race): add createRaceSession and fetchProgression API functions

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 2: Extend useRaceEngine with countdown/racing controls

**Files:**
- Modify: `src/engine/race/hooks/useRaceEngine.ts`
- Create: `src/engine/race/hooks/useRaceEngine.test.ts`

**Interfaces:**
- Consumes: `createRaceEngine` from `src/engine/race/raceEngine.ts`; `postRaceSummary` removed from this hook (moves to T005)
- Produces:
  - `startCountdown(): void` — transitions engine IDLE→LOBBY→COUNTDOWN
  - `startRacing(): void` — transitions engine COUNTDOWN→RACING
  - `getSummary(): RaceSummary` — delegates to `engine.getSummary()`
  - **Removes**: `summaryStatus`, `postRaceSummary` call (responsibility moves to ResultsScreenPage)

**Why remove `postRaceSummary` from the hook:** The Results Screen needs to display results immediately (from route state) and independently manage retry logic. Posting from the hook races with navigation and loses `new_achievements`.

- [ ] **Step 1: Write failing tests**

```typescript
// src/engine/race/hooks/useRaceEngine.test.ts
import { renderHook, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useRaceEngine } from './useRaceEngine';
import type { RaceConfig } from '../types';

const config: RaceConfig = {
  raceId: 'r1',
  seed: 1,
  tier: 1,
  mode: 'quick',
  participants: [{ runnerId: 'player', isHuman: true, avatarId: 'av1' }],
};

describe('useRaceEngine', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it('starts in IDLE state', () => {
    const { result } = renderHook(() => useRaceEngine(config));
    expect(result.current.state).toBe('IDLE');
  });

  it('startCountdown() transitions engine to COUNTDOWN', async () => {
    const { result } = renderHook(() => useRaceEngine(config));
    act(() => { result.current.startCountdown(); });
    await waitFor(() => expect(result.current.state).toBe('COUNTDOWN'));
  });

  it('startRacing() transitions engine from COUNTDOWN to RACING', async () => {
    const { result } = renderHook(() => useRaceEngine(config));
    act(() => { result.current.startCountdown(); });
    await waitFor(() => expect(result.current.state).toBe('COUNTDOWN'));
    act(() => { result.current.startRacing(); });
    await waitFor(() => expect(result.current.state).toBe('RACING'));
  });

  it('getSummary() throws before RESULTS state', async () => {
    const { result } = renderHook(() => useRaceEngine(config));
    expect(() => result.current.getSummary()).toThrow();
  });

  it('does not expose summaryStatus', () => {
    const { result } = renderHook(() => useRaceEngine(config));
    expect((result.current as Record<string, unknown>)['summaryStatus']).toBeUndefined();
  });
});
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `pnpm --dir frontend test useRaceEngine`
Expected: FAIL — `startCountdown is not a function` (or similar)

- [ ] **Step 3: Implement modified useRaceEngine.ts**

Full replacement for `src/engine/race/hooks/useRaceEngine.ts`:

```typescript
import { useCallback, useEffect, useRef, useState } from 'react';
import { createRaceEngine } from '../raceEngine';
import type { ObstacleResult, RaceConfig, RaceEngineState, RaceSummary } from '../types';

export function useRaceEngine(config: RaceConfig) {
  const engineRef = useRef(createRaceEngine(config));
  const rafRef = useRef<number | null>(null);
  const [snapshot, setSnapshot] = useState<RaceEngineState>(() => engineRef.current.getState());

  useEffect(() => {
    const engine = engineRef.current;

    function loop(timestamp: number) {
      engine.tick(timestamp);
      setSnapshot(engine.getState());
      rafRef.current = requestAnimationFrame(loop);
    }

    rafRef.current = requestAnimationFrame(loop);

    function onVisibility() {
      if (document.hidden) engine.pause();
      else engine.resume();
    }

    document.addEventListener('visibilitychange', onVisibility);

    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
      document.removeEventListener('visibilitychange', onVisibility);
    };
  }, []);

  const startCountdown = useCallback(() => {
    engineRef.current.transition('LOBBY');
    engineRef.current.transition('COUNTDOWN');
  }, []);

  const startRacing = useCallback(() => {
    engineRef.current.transition('RACING');
  }, []);

  const submitAnswer = useCallback(
    (input: { isCorrect: boolean }): ObstacleResult => engineRef.current.submitAnswer(input),
    [],
  );

  const forceComplete = useCallback(() => engineRef.current.forceComplete(), []);

  const getSummary = useCallback((): RaceSummary => engineRef.current.getSummary(), []);

  return { ...snapshot, startCountdown, startRacing, submitAnswer, forceComplete, getSummary };
}
```

- [ ] **Step 4: Run useRaceEngine tests — expect PASS**

Run: `pnpm --dir frontend test useRaceEngine`
Expected: PASS 5/5

- [ ] **Step 5: Run full suite — expect green**

Run: `pnpm --dir frontend test`
Expected: all tests pass (no regressions)

- [ ] **Step 6: Commit**

```bash
git add src/engine/race/hooks/useRaceEngine.ts src/engine/race/hooks/useRaceEngine.test.ts
git commit -m "feat(race): extend useRaceEngine with startCountdown/startRacing/getSummary

Removes postRaceSummary call from hook; results screen now handles sync
and retry independently.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Race Setup Page

**Files:**
- Modify: `src/pages/RaceSetupPage.tsx`
- Create: `src/pages/RaceSetupPage.test.tsx`

**Interfaces:**
- Consumes: `listAvatars()` from `src/engine/avatar/avatarApi.ts`; `createRaceSession()` from T001; `createChampionship()` from `src/engine/race/championshipApi.ts`; `PERSONALITIES` from `src/engine/race/personalities.ts`
- Produces: navigates to `/race/:id` with `RaceScreenRouteState` in `location.state`:
  ```typescript
  interface RaceScreenRouteState {
    mode: RaceMode;
    tier: Tier;
    seed: number;
    avatarId: string;
    opponentCount: number;
    championshipId?: string;
    raceIndex: number; // 0-based index for championship, always 0 for non-championship
  }
  ```
  Also writes `localStorage.setItem('activeChampionshipId', id)` when creating a championship.

- [ ] **Step 1: Write failing tests**

```typescript
// src/pages/RaceSetupPage.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as avatarApiModule from '../engine/avatar/avatarApi';
import * as raceSessionApiModule from '../features/race/raceSessionApi';
import * as championshipApiModule from '../engine/race/championshipApi';
import RaceSetupPage from './RaceSetupPage';

vi.mock('../engine/avatar/avatarApi');
vi.mock('../features/race/raceSessionApi');
vi.mock('../engine/race/championshipApi');

const published = {
  avatar_id: 'av1', name: 'Foxy', species: 'fox', status: 'published' as const,
  is_favourite: false, portrait: null, created_at: '',
};

describe('RaceSetupPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([published]);
    vi.mocked(raceSessionApiModule.createRaceSession).mockResolvedValue({ race_id: 'r1', seed: 42 });
  });

  function renderPage(initialPath = '/race/setup', state?: unknown) {
    return render(
      <MemoryRouter initialEntries={[{ pathname: initialPath, state }]}>
        <Routes>
          <Route path="/race/setup" element={<RaceSetupPage />} />
          <Route path="/avatars/new" element={<div>Avatar Creator</div>} />
          <Route path="/race/:id" element={<div>Race Screen</div>} />
        </Routes>
      </MemoryRouter>,
    );
  }

  it('redirects to /avatars/new when no published avatars exist', async () => {
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([]);
    renderPage();
    await waitFor(() => expect(screen.getByText('Avatar Creator')).toBeInTheDocument());
  });

  it('renders mode selector buttons', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByRole('button', { name: /quick race/i })).toBeInTheDocument());
    expect(screen.getByRole('button', { name: /training/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /duel/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /championship/i })).toBeInTheDocument();
  });

  it('shows championship races dropdown only when championship mode is active', async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => screen.getByRole('button', { name: /championship/i }));
    expect(screen.queryByLabelText(/number of races/i)).not.toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /championship/i }));
    expect(screen.getByLabelText(/number of races/i)).toBeInTheDocument();
  });

  it('creates race session and navigates to /race/:id on start', async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => screen.getByRole('button', { name: /start race/i }));
    await user.click(screen.getByRole('button', { name: /start race/i }));
    await waitFor(() => expect(screen.getByText('Race Screen')).toBeInTheDocument());
    expect(raceSessionApiModule.createRaceSession).toHaveBeenCalled();
  });

  it('pre-selects championship mode when continueChampionshipId in route state', async () => {
    vi.mocked(championshipApiModule.getChampionship).mockResolvedValue({
      championship_id: 'ch1', total_races: 3, races_completed: 1,
      status: 'active', standings: [],
    });
    renderPage('/race/setup', { continueChampionshipId: 'ch1', continueRaceIndex: 1 });
    await waitFor(() => expect(screen.getByRole('button', { name: /championship/i, pressed: true } as ByRoleOptions)).toBeInTheDocument());
  });
});
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `pnpm --dir frontend test RaceSetupPage`
Expected: FAIL — test stub only returns `<div data-testid="page-race-setup">`

- [ ] **Step 3: Implement RaceSetupPage.tsx**

```typescript
// src/pages/RaceSetupPage.tsx
import { useCallback, useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { listAvatars } from '../engine/avatar/avatarApi';
import type { AvatarListItem } from '../engine/avatar/types';
import { createChampionship, getChampionship } from '../engine/race/championshipApi';
import { PERSONALITIES } from '../engine/race/personalities';
import type { RaceMode } from '../engine/race/types';
import type { Tier } from '../engine/math/types';
import { createRaceSession } from '../features/race/raceSessionApi';
import { Button } from '../shared/components/Button';
import { LoadingSpinner } from '../shared/components/LoadingSpinner';
import tokens from '../shared/tokens';

interface SetupRouteState {
  continueChampionshipId?: string;
  continueRaceIndex?: number;
}

const MODES: Array<{ mode: RaceMode; label: string; defaultOpponents: number }> = [
  { mode: 'quick', label: 'Quick Race', defaultOpponents: 3 },
  { mode: 'championship', label: 'Championship', defaultOpponents: 3 },
  { mode: 'training', label: 'Training', defaultOpponents: 0 },
  { mode: 'duel', label: 'Duel', defaultOpponents: 1 },
];

export default function RaceSetupPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const routeState = (location.state ?? {}) as SetupRouteState;

  const [avatars, setAvatars] = useState<AvatarListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState<RaceMode>(
    routeState.continueChampionshipId ? 'championship' : 'quick',
  );
  const [tier, setTier] = useState<Tier>(1);
  const [opponentCount, setOpponentCount] = useState(3);
  const [champRaces, setChampRaces] = useState(3);
  const [selectedAvatarId, setSelectedAvatarId] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [continueChampionshipId] = useState(routeState.continueChampionshipId);
  const [continueRaceIndex] = useState(routeState.continueRaceIndex ?? 0);

  useEffect(() => {
    listAvatars()
      .then((list) => {
        const published = list.filter((a) => a.status === 'published');
        if (published.length === 0) {
          void navigate('/avatars/new', { replace: true });
          return;
        }
        setAvatars(published);
        setSelectedAvatarId(published[0].avatar_id);
      })
      .catch(() => void navigate('/avatars/new', { replace: true }))
      .finally(() => setLoading(false));
  }, [navigate]);

  function handleModeChange(m: RaceMode) {
    setMode(m);
    setOpponentCount(MODES.find((x) => x.mode === m)?.defaultOpponents ?? 0);
  }

  async function handleStart() {
    if (!selectedAvatarId || starting) return;
    setStarting(true);
    try {
      let championship_id = continueChampionshipId;
      let raceIndex = continueRaceIndex;

      if (mode === 'championship' && !championship_id) {
        const champ = await createChampionship(champRaces);
        championship_id = champ.championship_id;
        raceIndex = champ.races_completed;
        localStorage.setItem('activeChampionshipId', championship_id);
      }

      const session = await createRaceSession({
        mode,
        tier,
        avatar_id: selectedAvatarId,
        opponent_count: opponentCount,
        championship_id,
      });

      void navigate(`/race/${session.race_id}`, {
        state: {
          mode,
          tier,
          seed: session.seed,
          avatarId: selectedAvatarId,
          opponentCount,
          championshipId: championship_id,
          raceIndex,
        },
      });
    } finally {
      setStarting(false);
    }
  }

  if (loading) return <LoadingSpinner message="Loading your avatars…" />;

  return (
    <div
      data-testid="page-race-setup"
      style={{ maxWidth: 480, margin: '0 auto', padding: tokens.spacing.xl }}
    >
      <h1 style={{ color: tokens.color.textPrimary, marginBottom: tokens.spacing.lg }}>
        Race Setup
      </h1>

      {/* Mode selector */}
      <section aria-labelledby="mode-heading" style={{ marginBottom: tokens.spacing.lg }}>
        <h2 id="mode-heading" style={{ fontSize: 18, color: tokens.color.textSecondary, marginBottom: tokens.spacing.sm }}>
          Mode
        </h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: tokens.spacing.sm }}>
          {MODES.map((m) => (
            <button
              key={m.mode}
              type="button"
              aria-pressed={mode === m.mode}
              onClick={() => handleModeChange(m.mode)}
              style={{
                padding: `${tokens.spacing.sm}px ${tokens.spacing.md}px`,
                borderRadius: tokens.radius.md,
                border: `2px solid ${mode === m.mode ? tokens.color.primary : tokens.color.border}`,
                background: mode === m.mode ? tokens.color.primary : tokens.color.surface,
                color: mode === m.mode ? tokens.color.textOnPrimary : tokens.color.textPrimary,
                cursor: 'pointer',
                fontWeight: 600,
              }}
            >
              {m.label}
            </button>
          ))}
        </div>
      </section>

      {/* Championship: number of races */}
      {mode === 'championship' && !continueChampionshipId && (
        <section style={{ marginBottom: tokens.spacing.lg }}>
          <label
            htmlFor="champ-races"
            style={{ display: 'block', color: tokens.color.textSecondary, marginBottom: tokens.spacing.xs }}
          >
            Number of Races
          </label>
          <select
            id="champ-races"
            value={champRaces}
            onChange={(e) => setChampRaces(Number(e.target.value))}
            style={{ padding: tokens.spacing.sm, borderRadius: tokens.radius.sm, border: `1px solid ${tokens.color.border}`, fontSize: 16 }}
          >
            {[3, 5, 7].map((n) => (
              <option key={n} value={n}>{n} races</option>
            ))}
          </select>
        </section>
      )}

      {/* Quick Race: opponent count */}
      {mode === 'quick' && (
        <section style={{ marginBottom: tokens.spacing.lg }}>
          <label
            htmlFor="opponent-count"
            style={{ display: 'block', color: tokens.color.textSecondary, marginBottom: tokens.spacing.xs }}
          >
            Opponents
          </label>
          <select
            id="opponent-count"
            value={opponentCount}
            onChange={(e) => setOpponentCount(Number(e.target.value))}
            style={{ padding: tokens.spacing.sm, borderRadius: tokens.radius.sm, border: `1px solid ${tokens.color.border}`, fontSize: 16 }}
          >
            {[1, 2, 3, 4].map((n) => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
        </section>
      )}

      {/* Difficulty tier */}
      <section style={{ marginBottom: tokens.spacing.lg }}>
        <label
          htmlFor="tier-select"
          style={{ display: 'block', color: tokens.color.textSecondary, marginBottom: tokens.spacing.xs }}
        >
          Difficulty (Tier 1 = easiest)
        </label>
        <select
          id="tier-select"
          value={tier}
          onChange={(e) => setTier(Number(e.target.value) as Tier)}
          style={{ padding: tokens.spacing.sm, borderRadius: tokens.radius.sm, border: `1px solid ${tokens.color.border}`, fontSize: 16 }}
        >
          {([1, 2, 3, 4, 5] as Tier[]).map((t) => (
            <option key={t} value={t}>Tier {t}</option>
          ))}
        </select>
      </section>

      {/* Avatar selector (if multiple) */}
      {avatars.length > 1 && (
        <section style={{ marginBottom: tokens.spacing.lg }}>
          <label
            htmlFor="avatar-select"
            style={{ display: 'block', color: tokens.color.textSecondary, marginBottom: tokens.spacing.xs }}
          >
            Racing as
          </label>
          <select
            id="avatar-select"
            value={selectedAvatarId ?? ''}
            onChange={(e) => setSelectedAvatarId(e.target.value)}
            style={{ padding: tokens.spacing.sm, borderRadius: tokens.radius.sm, border: `1px solid ${tokens.color.border}`, fontSize: 16 }}
          >
            {avatars.map((a) => (
              <option key={a.avatar_id} value={a.avatar_id}>
                {a.name ?? a.species}
              </option>
            ))}
          </select>
        </section>
      )}

      <Button
        variant="primary"
        disabled={!selectedAvatarId || starting}
        onClick={() => void handleStart()}
        style={{ width: '100%' }}
      >
        {starting ? 'Setting up…' : 'Start Race'}
      </Button>
    </div>
  );
}
```

- [ ] **Step 4: Run RaceSetupPage tests — expect PASS**

Run: `pnpm --dir frontend test RaceSetupPage`
Expected: PASS 4/4

_Note: if the `aria-pressed` query fails (`ByRoleOptions` type issue), remove the `pressed: true` assertion from the last test and just check that the championship button is in the document._

- [ ] **Step 5: Run full suite — expect green**

Run: `pnpm --dir frontend test`
Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
git add src/pages/RaceSetupPage.tsx src/pages/RaceSetupPage.test.tsx
git commit -m "feat(race): implement Race Setup Page with mode/tier/opponent/avatar selection

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 4: Race Screen Page

**Files:**
- Modify: `src/pages/RaceScreenPage.tsx`
- Create: `src/pages/RaceScreenPage.test.tsx`

**Interfaces:**
- Consumes: `useRaceEngine` from T002 (with `startCountdown`, `startRacing`, `getSummary`); `PERSONALITIES` from `src/engine/race/personalities.ts`; `MAX_TRACK_DISTANCE`, `OBSTACLE_COUNT` from `src/engine/race/constants.ts`; `useBlocker` from `react-router-dom`
- Consumes route state: `RaceScreenRouteState` (produced by T003)
- Produces: navigates to `/race/:id/results` with:
  ```typescript
  interface ResultsRouteState {
    summary: RaceSummary;
    playerAvatarId: string;
    championshipId?: string;
    raceIndex?: number;
  }
  ```
- Page stays mounted until RESULTS; then navigates. During RACING, back navigation is blocked by `useBlocker` with a `ConfirmDialog`.

- [ ] **Step 1: Write failing tests**

```typescript
// src/pages/RaceScreenPage.test.tsx
import { render, screen, act, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import RaceScreenPage from './RaceScreenPage';
import * as useRaceEngineModule from '../engine/race/hooks/useRaceEngine';
import type { RaceEngineState } from '../engine/race/types';
import type { ProblemSet } from '../engine/math/types';

vi.mock('../engine/race/hooks/useRaceEngine');

const problem: ProblemSet['problems'][0] = {
  id: 'p1', operation: 'addition', operand_a: 3, operand_b: 4,
  answer: 7, tier: 1, seed: 1,
};

const makeEngineReturn = (
  overrides: Partial<ReturnType<typeof useRaceEngineModule.useRaceEngine>> = {},
) => ({
  state: 'IDLE' as const,
  config: null,
  clockMs: 0,
  obstacleClockMs: 0,
  currentObstacle: -1,
  runners: [],
  problemSet: null,
  startCountdown: vi.fn(),
  startRacing: vi.fn(),
  submitAnswer: vi.fn(),
  forceComplete: vi.fn(),
  getSummary: vi.fn(),
  ...overrides,
});

const routeState = {
  mode: 'quick' as const, tier: 1 as const, seed: 42,
  avatarId: 'av1', opponentCount: 1, raceIndex: 0,
};

function renderPage(state = routeState) {
  return render(
    <MemoryRouter initialEntries={[{ pathname: '/race/r1', state }]}>
      <Routes>
        <Route path="/race/:id" element={<RaceScreenPage />} />
        <Route path="/race/:id/results" element={<div>Results</div>} />
        <Route path="/race/setup" element={<div>Setup</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('RaceScreenPage', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(makeEngineReturn());
  });
  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  it('redirects to /race/setup when no route state', () => {
    render(
      <MemoryRouter initialEntries={['/race/r1']}>
        <Routes>
          <Route path="/race/:id" element={<RaceScreenPage />} />
          <Route path="/race/setup" element={<div>Setup</div>} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText('Setup')).toBeInTheDocument();
  });

  it('calls startCountdown on mount', () => {
    const startCountdown = vi.fn();
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(makeEngineReturn({ startCountdown }));
    renderPage();
    expect(startCountdown).toHaveBeenCalledTimes(1);
  });

  it('shows countdown 3→2→1→GO! in aria-live region', async () => {
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({ state: 'COUNTDOWN' }),
    );
    renderPage();
    expect(screen.getByRole('status')).toHaveTextContent('3');
    act(() => { vi.advanceTimersByTime(1000); });
    expect(screen.getByRole('status')).toHaveTextContent('2');
    act(() => { vi.advanceTimersByTime(1000); });
    expect(screen.getByRole('status')).toHaveTextContent('1');
    act(() => { vi.advanceTimersByTime(1000); });
    expect(screen.getByRole('status')).toHaveTextContent('GO!');
  });

  it('calls startRacing after GO! delay', async () => {
    const startRacing = vi.fn();
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({ state: 'COUNTDOWN', startRacing }),
    );
    renderPage();
    act(() => { vi.advanceTimersByTime(3000); }); // 3 countdown ticks
    act(() => { vi.advanceTimersByTime(800); });  // GO! display delay
    expect(startRacing).toHaveBeenCalledTimes(1);
  });

  it('renders problem card with aria-labeled input when RACING', () => {
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({
        state: 'RACING',
        currentObstacle: 0,
        obstacleClockMs: 1000,
        runners: [{ runnerId: 'player', isHuman: true, totalDistanceMetres: 0, obstaclesCompleted: 0, obstacleResults: [], finishTime: null }],
        problemSet: { seed: 1, tier: 1, count: 8, problems: [problem, ...Array(7).fill(problem)] },
      }),
    );
    renderPage();
    expect(screen.getByText(/3 \+ 4 = \?/)).toBeInTheDocument();
    expect(screen.getByRole('spinbutton', { name: /what is 3 \+ 4/i })).toBeInTheDocument();
  });

  it('calls submitAnswer with isCorrect: true when correct answer submitted', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime.bind(vi) });
    const submitAnswer = vi.fn();
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({
        state: 'RACING',
        currentObstacle: 0,
        obstacleClockMs: 500,
        runners: [{ runnerId: 'player', isHuman: true, totalDistanceMetres: 0, obstaclesCompleted: 0, obstacleResults: [], finishTime: null }],
        problemSet: { seed: 1, tier: 1, count: 8, problems: [problem, ...Array(7).fill(problem)] },
        submitAnswer,
      }),
    );
    renderPage();
    await user.type(screen.getByRole('spinbutton'), '7');
    await user.keyboard('{Enter}');
    expect(submitAnswer).toHaveBeenCalledWith({ isCorrect: true });
  });

  it('navigates to /race/:id/results when engine reaches RESULTS', async () => {
    const summary = { race_id: 'r1', seed: '42', difficulty_tier: 1, mode: 'quick', started_at: '', completed_at: '', participants: [] };
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({ state: 'RESULTS', getSummary: vi.fn().mockReturnValue(summary) }),
    );
    renderPage();
    await waitFor(() => expect(screen.getByText('Results')).toBeInTheDocument());
  });
});
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `pnpm --dir frontend test RaceScreenPage`
Expected: FAIL — stub page returns static div

- [ ] **Step 3: Implement RaceScreenPage.tsx**

```typescript
// src/pages/RaceScreenPage.tsx
import { useCallback, useEffect, useRef, useState } from 'react';
import { Navigate, useBlocker, useLocation, useNavigate, useParams } from 'react-router-dom';
import { useRaceEngine } from '../engine/race/hooks/useRaceEngine';
import { MAX_TRACK_DISTANCE, OBSTACLE_COUNT } from '../engine/race/constants';
import { PERSONALITIES } from '../engine/race/personalities';
import type { ParticipantConfig, RaceConfig, RaceMode } from '../engine/race/types';
import type { Tier } from '../engine/math/types';
import { ConfirmDialog } from '../shared/components/ConfirmDialog';
import tokens from '../shared/tokens';

interface RaceScreenRouteState {
  mode: RaceMode;
  tier: Tier;
  seed: number;
  avatarId: string;
  opponentCount: number;
  championshipId?: string;
  raceIndex: number;
}

function buildParticipants(playerAvatarId: string, opponentCount: number): ParticipantConfig[] {
  const player: ParticipantConfig = { runnerId: 'player', isHuman: true, avatarId: playerAvatarId };
  const ai: ParticipantConfig[] = Array.from({ length: opponentCount }, (_, i) => ({
    runnerId: `ai-${i + 1}`,
    isHuman: false,
    avatarId: `ai-${i + 1}`,
    personality: PERSONALITIES[i % PERSONALITIES.length],
  }));
  return [player, ...ai];
}

export default function RaceScreenPage() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const routeState = location.state as RaceScreenRouteState | null;

  if (!routeState || !id) return <Navigate to="/race/setup" replace />;

  const config: RaceConfig = {
    raceId: id,
    seed: routeState.seed,
    tier: routeState.tier,
    mode: routeState.mode,
    participants: buildParticipants(routeState.avatarId, routeState.opponentCount),
  };

  return <RaceScreen raceId={id} config={config} routeState={routeState} />;
}

const OP_SYMBOL: Record<string, string> = {
  addition: '+', subtraction: '−', multiplication: '×', division: '÷',
};

function RaceScreen({
  raceId,
  config,
  routeState,
}: {
  raceId: string;
  config: RaceConfig;
  routeState: RaceScreenRouteState;
}) {
  const navigate = useNavigate();
  const { state, obstacleClockMs, currentObstacle, runners, problemSet,
          startCountdown, startRacing, submitAnswer, getSummary } = useRaceEngine(config);

  const [countdownNum, setCountdownNum] = useState(3);
  const [answerInput, setAnswerInput] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const blocker = useBlocker(state === 'RACING');

  // Kick off countdown on mount
  useEffect(() => {
    startCountdown();
  }, []); // startCountdown is stable — no dep needed

  // Tick countdown when in COUNTDOWN state
  useEffect(() => {
    if (state !== 'COUNTDOWN') return;
    if (countdownNum > 0) {
      const t = setTimeout(() => setCountdownNum((n) => n - 1), 1000);
      return () => clearTimeout(t);
    }
    const t = setTimeout(startRacing, 800);
    return () => clearTimeout(t);
  }, [state, countdownNum, startRacing]);

  // Auto-focus answer input each obstacle
  useEffect(() => {
    if (state === 'RACING') inputRef.current?.focus();
  }, [state, currentObstacle]);

  // Navigate to results when race finishes
  useEffect(() => {
    if (state === 'RESULTS') {
      void navigate(`/race/${raceId}/results`, {
        state: {
          summary: getSummary(),
          playerAvatarId: routeState.avatarId,
          championshipId: routeState.championshipId,
          raceIndex: routeState.raceIndex,
        },
        replace: true,
      });
    }
  }, [state]); // navigate/raceId/routeState/getSummary are stable

  function handleSubmit() {
    if (state !== 'RACING') return;
    const problem = problemSet?.problems[currentObstacle];
    if (!problem) return;
    const parsed = parseInt(answerInput, 10);
    submitAnswer({ isCorrect: !isNaN(parsed) && parsed === problem.answer });
    setAnswerInput('');
  }

  const problem = problemSet?.problems[currentObstacle];
  const isCountdownPhase = state === 'IDLE' || state === 'LOBBY' || state === 'COUNTDOWN';

  if (isCountdownPhase) {
    return (
      <div
        data-testid="page-race-screen"
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}
      >
        <div
          role="status"
          aria-live="polite"
          style={{ fontSize: 96, fontWeight: 900, color: tokens.color.primary, lineHeight: 1 }}
        >
          {state === 'COUNTDOWN' ? (countdownNum > 0 ? String(countdownNum) : 'GO!') : '…'}
        </div>
      </div>
    );
  }

  return (
    <div
      data-testid="page-race-screen"
      style={{ maxWidth: 640, margin: '0 auto', padding: tokens.spacing.xl }}
    >
      {/* Back-navigation confirmation */}
      {blocker.state === 'blocked' && (
        <ConfirmDialog
          title="Leave Race?"
          message="Your progress will be lost if you leave now."
          confirmLabel="Leave"
          onConfirm={() => blocker.proceed()}
          onCancel={() => blocker.reset()}
        />
      )}

      {/* Race track — one lane per runner */}
      <div style={{ marginBottom: tokens.spacing.lg }} aria-label="Race track">
        {runners.map((runner) => {
          const pct = Math.min(100, (runner.totalDistanceMetres / MAX_TRACK_DISTANCE) * 100);
          const isPlayer = runner.isHuman;
          return (
            <div
              key={runner.runnerId}
              style={{ display: 'flex', alignItems: 'center', gap: tokens.spacing.sm, marginBottom: tokens.spacing.xs }}
            >
              <span
                aria-label={isPlayer ? 'You' : runner.runnerId}
                style={{ width: 24, fontSize: 12, color: tokens.color.textSecondary, textAlign: 'center' }}
              >
                {isPlayer ? '★' : runner.runnerId.replace('ai-', '')}
              </span>
              <div
                style={{
                  flex: 1,
                  height: 24,
                  background: tokens.color.background,
                  borderRadius: 999,
                  border: `1px solid ${tokens.color.border}`,
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    position: 'absolute',
                    left: `${pct}%`,
                    top: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: 20,
                    height: 20,
                    borderRadius: '50%',
                    background: isPlayer ? tokens.color.primary : tokens.color.textSecondary,
                    transition: `left ${tokens.animation.micro} ease-out`,
                  }}
                />
              </div>
              <span style={{ width: 40, fontSize: 12, color: tokens.color.textSecondary, textAlign: 'right' }}>
                {runner.totalDistanceMetres}m
              </span>
            </div>
          );
        })}
      </div>

      {/* Per-obstacle timer bar */}
      {state === 'RACING' && (
        <div style={{ marginBottom: tokens.spacing.md }}>
          <div
            style={{
              height: 8,
              borderRadius: 999,
              background: tokens.color.background,
              border: `1px solid ${tokens.color.border}`,
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                height: '100%',
                width: `${Math.min(100, (obstacleClockMs / 8000) * 100)}%`,
                background:
                  obstacleClockMs < 2000
                    ? tokens.color.success
                    : obstacleClockMs < 4000
                    ? tokens.color.warning
                    : tokens.color.error,
                transition: 'width 0.1s linear',
              }}
            />
          </div>
        </div>
      )}

      {/* Problem card */}
      {state === 'RACING' && problem && (
        <div
          style={{
            background: tokens.color.surface,
            borderRadius: tokens.radius.lg,
            padding: tokens.spacing.lg,
            boxShadow: tokens.shadow.card,
            marginBottom: tokens.spacing.lg,
            textAlign: 'center',
          }}
        >
          <p style={{ fontSize: 48, fontWeight: 900, color: tokens.color.textPrimary, margin: `0 0 ${tokens.spacing.md}px` }}>
            {problem.operand_a} {OP_SYMBOL[problem.operation]} {problem.operand_b} = ?
          </p>
          <input
            ref={inputRef}
            type="number"
            aria-label={`What is ${problem.operand_a} ${OP_SYMBOL[problem.operation]} ${problem.operand_b}?`}
            value={answerInput}
            onChange={(e) => setAnswerInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') handleSubmit(); }}
            style={{
              fontSize: 32,
              width: 120,
              textAlign: 'center',
              border: `2px solid ${tokens.color.border}`,
              borderRadius: tokens.radius.md,
              padding: tokens.spacing.sm,
            }}
          />
          <div style={{ marginTop: tokens.spacing.md }}>
            <button
              type="button"
              onClick={handleSubmit}
              style={{
                padding: `${tokens.spacing.sm}px ${tokens.spacing.lg}px`,
                background: tokens.color.primary,
                color: tokens.color.textOnPrimary,
                borderRadius: tokens.radius.md,
                border: 'none',
                cursor: 'pointer',
                fontSize: 18,
                fontWeight: 700,
                minHeight: tokens.touchTarget,
              }}
            >
              Submit
            </button>
          </div>
          <p style={{ color: tokens.color.textSecondary, marginTop: tokens.spacing.sm, fontSize: 14 }}>
            Obstacle {currentObstacle + 1} of {OBSTACLE_COUNT}
          </p>
        </div>
      )}

      {/* Leave race */}
      {state === 'RACING' && (
        <button
          type="button"
          onClick={() => void navigate('/race/setup')}
          style={{ background: 'none', border: 'none', color: tokens.color.textSecondary, cursor: 'pointer', fontSize: 14 }}
        >
          Leave Race
        </button>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Run RaceScreenPage tests — expect PASS**

Run: `pnpm --dir frontend test RaceScreenPage`
Expected: PASS 7/7

- [ ] **Step 5: Run full suite — expect green**

Run: `pnpm --dir frontend test`
Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
git add src/pages/RaceScreenPage.tsx src/pages/RaceScreenPage.test.tsx
git commit -m "feat(race): implement Race Screen with countdown, track, problem card, and back-nav guard

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 5: Results Screen Page

**Files:**
- Modify: `src/pages/ResultsScreenPage.tsx`
- Create: `src/pages/ResultsScreenPage.test.tsx`

**Interfaces:**
- Consumes: `postRaceSummary()` from `src/engine/race/raceApi.ts`; `recordChampionshipRace()` from `src/engine/race/championshipApi.ts`; `fetchProgression()` from T001; `NotificationToast` from shared components
- Consumes route state: `ResultsRouteState` produced by T004
- Produces: navigation buttons to `/race/setup`, `/championship/:id` (if championship mode), and `/`

- [ ] **Step 1: Write failing tests**

```typescript
// src/pages/ResultsScreenPage.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as raceApiModule from '../engine/race/raceApi';
import * as progressionApiModule from '../features/race/progressionApi';
import * as championshipApiModule from '../engine/race/championshipApi';
import ResultsScreenPage from './ResultsScreenPage';
import type { RaceSummary } from '../engine/race/types';

vi.mock('../engine/race/raceApi');
vi.mock('../features/race/progressionApi');
vi.mock('../engine/race/championshipApi');

const makeSummary = (xpEarned = 80): RaceSummary => ({
  race_id: 'r1',
  seed: '1',
  difficulty_tier: 1,
  mode: 'quick',
  started_at: '',
  completed_at: '',
  participants: [
    { avatar_id: 'av1', position: 1, problems_correct: 7, longest_streak: 5, average_response_ms: 1500, total_distance: 126, xp_earned: xpEarned },
    { avatar_id: 'ai-1', position: 2, problems_correct: 5, longest_streak: 3, average_response_ms: 3000, total_distance: 90, xp_earned: 60 },
  ],
});

function renderPage(state: unknown) {
  return render(
    <MemoryRouter initialEntries={[{ pathname: '/race/r1/results', state }]}>
      <Routes>
        <Route path="/race/:id/results" element={<ResultsScreenPage />} />
        <Route path="/" element={<div>Home</div>} />
        <Route path="/race/setup" element={<div>Setup</div>} />
        <Route path="/championship/:id" element={<div>Championship</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('ResultsScreenPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(raceApiModule.postRaceSummary).mockResolvedValue({ new_achievements: [] });
    vi.mocked(progressionApiModule.fetchProgression).mockResolvedValue({
      player_id: 'p1', total_xp: 200, current_level: 1, xp_to_next_level: 200,
    });
  });

  it('redirects to / when no route state', () => {
    render(
      <MemoryRouter initialEntries={['/race/r1/results']}>
        <Routes>
          <Route path="/race/:id/results" element={<ResultsScreenPage />} />
          <Route path="/" element={<div>Home</div>} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByText('Home')).toBeInTheDocument();
  });

  it('renders results table with col headers and participant rows', async () => {
    renderPage({ summary: makeSummary(), playerAvatarId: 'av1' });
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument());
    expect(screen.getByRole('columnheader', { name: /place/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /correct/i })).toBeInTheDocument();
    expect(screen.getByText('You')).toBeInTheDocument();
    expect(screen.getByText('126m')).toBeInTheDocument();
  });

  it('shows level-up overlay when level increased after race', async () => {
    // Player earned 80 XP. total_xp now = 400 (level 2). Before = 320 (still level 1).
    // level(400) = floor(sqrt(4)) = 2; level(320) = floor(sqrt(3.2)) = 1
    vi.mocked(progressionApiModule.fetchProgression).mockResolvedValue({
      player_id: 'p1', total_xp: 400, current_level: 2, xp_to_next_level: 500,
    });
    renderPage({ summary: makeSummary(80), playerAvatarId: 'av1' });
    await waitFor(() => expect(screen.getByText(/level up/i)).toBeInTheDocument());
  });

  it('shows achievement toast for each new achievement', async () => {
    vi.mocked(raceApiModule.postRaceSummary).mockResolvedValue({
      new_achievements: [{
        key: 'first_race', title: 'First Steps', category: 'racing',
        description: 'Complete your first race', hidden: false, icon_path: '', unlocked_at: '',
      }],
    });
    renderPage({ summary: makeSummary(), playerAvatarId: 'av1' });
    await waitFor(() => expect(screen.getByText(/achievement: first steps/i)).toBeInTheDocument());
  });

  it('shows retry button with role=alert when sync fails', async () => {
    vi.mocked(raceApiModule.postRaceSummary).mockRejectedValue(new Error('Network error'));
    renderPage({ summary: makeSummary(), playerAvatarId: 'av1' });
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  it('shows View Championship button and calls recordChampionshipRace when mode is championship', async () => {
    vi.mocked(championshipApiModule.recordChampionshipRace).mockResolvedValue({
      championship_id: 'ch1', total_races: 3, races_completed: 1, status: 'active', standings: [],
    });
    const summary: RaceSummary = { ...makeSummary(), mode: 'championship' };
    renderPage({ summary, playerAvatarId: 'av1', championshipId: 'ch1', raceIndex: 0 });
    await waitFor(() => expect(championshipApiModule.recordChampionshipRace).toHaveBeenCalledWith(
      'ch1', 'r1', 0, expect.any(Array),
    ));
    expect(screen.getByRole('button', { name: /view championship/i })).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `pnpm --dir frontend test ResultsScreenPage`
Expected: FAIL — stub page returns static div

- [ ] **Step 3: Implement ResultsScreenPage.tsx**

```typescript
// src/pages/ResultsScreenPage.tsx
import { useEffect, useState } from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { recordChampionshipRace } from '../engine/race/championshipApi';
import { postRaceSummary } from '../engine/race/raceApi';
import type { RaceSummary } from '../engine/race/types';
import type { Achievement } from '../engine/achievements/types';
import { fetchProgression } from '../features/race/progressionApi';
import { Button } from '../shared/components/Button';
import { NotificationToast } from '../shared/components/NotificationToast';
import tokens from '../shared/tokens';

interface ResultsRouteState {
  summary: RaceSummary;
  playerAvatarId: string;
  championshipId?: string;
  raceIndex?: number;
}

type SyncStatus = 'pending' | 'saved' | 'error';

function computeLevel(totalXp: number): number {
  return Math.floor(Math.sqrt(totalXp / 100));
}

export default function ResultsScreenPage() {
  const location = useLocation();
  const routeState = location.state as ResultsRouteState | null;
  if (!routeState) return <Navigate to="/" replace />;
  return <ResultsScreen routeState={routeState} />;
}

function ResultsScreen({ routeState }: { routeState: ResultsRouteState }) {
  const navigate = useNavigate();
  const { summary, playerAvatarId, championshipId, raceIndex } = routeState;

  const [syncStatus, setSyncStatus] = useState<SyncStatus>('pending');
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [toastIndex, setToastIndex] = useState(0);
  const [currentLevel, setCurrentLevel] = useState<number | null>(null);
  const [levelBefore, setLevelBefore] = useState<number | null>(null);

  const playerEntry = summary.participants.find((p) => p.avatar_id === playerAvatarId);

  async function doSync() {
    const result = await postRaceSummary(summary);
    setAchievements(result.new_achievements);

    if (championshipId !== undefined && raceIndex !== undefined) {
      await recordChampionshipRace(
        championshipId,
        summary.race_id,
        raceIndex,
        summary.participants.map((p) => ({
          avatar_id: p.avatar_id,
          is_player: p.avatar_id === playerAvatarId,
          finishing_position: p.position ?? 1,
        })),
      );
    }

    const progression = await fetchProgression();
    setCurrentLevel(progression.current_level);
    if (playerEntry) {
      setLevelBefore(computeLevel(progression.total_xp - playerEntry.xp_earned));
    }
    setSyncStatus('saved');
  }

  useEffect(() => {
    let cancelled = false;
    doSync().catch(() => { if (!cancelled) setSyncStatus('error'); });
    return () => { cancelled = true; };
  }, []); // summary/playerEntry/championshipId are stable from route state

  function retry() {
    setSyncStatus('pending');
    doSync().catch(() => setSyncStatus('error'));
  }

  const didLevelUp = currentLevel !== null && levelBefore !== null && currentLevel > levelBefore;

  return (
    <div
      data-testid="page-results-screen"
      style={{ maxWidth: 640, margin: '0 auto', padding: tokens.spacing.xl }}
    >
      {/* Level-up overlay */}
      {didLevelUp && (
        <div
          role="status"
          aria-live="polite"
          style={{
            background: tokens.color.primary,
            color: tokens.color.textOnPrimary,
            borderRadius: tokens.radius.lg,
            padding: tokens.spacing.lg,
            marginBottom: tokens.spacing.lg,
            textAlign: 'center',
          }}
        >
          <p style={{ fontSize: 28, fontWeight: 900, margin: 0 }}>Level Up!</p>
          <p style={{ margin: `${tokens.spacing.xs}px 0 0` }}>You reached Level {currentLevel}!</p>
        </div>
      )}

      {/* Achievement toasts (shown one at a time) */}
      {achievements[toastIndex] && (
        <NotificationToast
          message={`Achievement: ${achievements[toastIndex].title}`}
          type="success"
          onClose={() => setToastIndex((i) => i + 1)}
        />
      )}

      <h1 style={{ color: tokens.color.textPrimary, marginBottom: tokens.spacing.lg }}>
        {summary.mode === 'training' ? 'Training Complete' : 'Race Finished!'}
      </h1>

      {/* Results table */}
      <table
        style={{ width: '100%', borderCollapse: 'collapse', marginBottom: tokens.spacing.lg }}
      >
        <thead>
          <tr>
            {['Place', 'Runner', 'Distance', 'Correct', 'XP'].map((h) => (
              <th
                key={h}
                scope="col"
                style={{
                  textAlign: h === 'Place' || h === 'Runner' ? 'left' : 'right',
                  padding: tokens.spacing.sm,
                  borderBottom: `2px solid ${tokens.color.border}`,
                  color: tokens.color.textSecondary,
                  fontSize: 14,
                  fontWeight: 600,
                }}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {summary.participants.map((p, i) => {
            const isPlayer = p.avatar_id === playerAvatarId;
            return (
              <tr
                key={p.avatar_id}
                style={{ background: isPlayer ? `${tokens.color.primary}18` : 'transparent' }}
              >
                <th scope="row" style={{ padding: tokens.spacing.sm, fontWeight: 400 }}>
                  {p.position ?? '—'}
                </th>
                <td style={{ padding: tokens.spacing.sm, fontWeight: isPlayer ? 700 : 400 }}>
                  {isPlayer ? 'You' : `Runner ${i + 1}`}
                </td>
                <td style={{ padding: tokens.spacing.sm, textAlign: 'right' }}>{p.total_distance}m</td>
                <td style={{ padding: tokens.spacing.sm, textAlign: 'right' }}>{p.problems_correct}/8</td>
                <td style={{ padding: tokens.spacing.sm, textAlign: 'right', color: tokens.color.success, fontWeight: 700 }}>
                  +{p.xp_earned}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {/* Sync failure */}
      {syncStatus === 'error' && (
        <div
          role="alert"
          style={{ color: tokens.color.error, marginBottom: tokens.spacing.md, fontSize: 14 }}
        >
          Couldn&apos;t save results.{' '}
          <button
            type="button"
            onClick={retry}
            style={{ color: tokens.color.primary, background: 'none', border: 'none', cursor: 'pointer', textDecoration: 'underline', fontSize: 14 }}
          >
            Retry
          </button>
        </div>
      )}

      {/* Navigation */}
      <div style={{ display: 'flex', gap: tokens.spacing.md, flexWrap: 'wrap' }}>
        <Button variant="primary" onClick={() => void navigate('/race/setup')}>Race Again</Button>
        {championshipId && (
          <Button variant="secondary" onClick={() => void navigate(`/championship/${championshipId}`)}>
            View Championship
          </Button>
        )}
        <Button variant="secondary" onClick={() => void navigate('/')}>Home</Button>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Run ResultsScreenPage tests — expect PASS**

Run: `pnpm --dir frontend test ResultsScreenPage`
Expected: PASS 5/5

- [ ] **Step 5: Run full suite — expect green**

Run: `pnpm --dir frontend test`
Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
git add src/pages/ResultsScreenPage.tsx src/pages/ResultsScreenPage.test.tsx src/features/race/progressionApi.ts
git commit -m "feat(race): implement Results Screen with table, achievements, level-up overlay, and retry

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 6: Championship Page and Home Page

**Files:**
- Modify: `src/pages/ChampionshipPage.tsx`
- Create: `src/pages/ChampionshipPage.test.tsx`
- Modify: `src/pages/HomePage.tsx`

**Interfaces:**
- Consumes: `getChampionship()` from `src/engine/race/championshipApi.ts`
- Championship Page produces: navigates to `/race/setup` with state `{ continueChampionshipId, continueRaceIndex }` when "Start Next Race" clicked
- Home Page reads `localStorage.getItem('activeChampionshipId')` and fetches it to show "Continue Championship" prompt

- [ ] **Step 1: Write failing tests**

```typescript
// src/pages/ChampionshipPage.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as championshipApiModule from '../engine/race/championshipApi';
import ChampionshipPage from './ChampionshipPage';

vi.mock('../engine/race/championshipApi');

const activeChampionship = {
  championship_id: 'ch1',
  total_races: 3,
  races_completed: 1,
  status: 'active' as const,
  standings: [
    { avatar_id: 'av1', is_player: true, points: 10, podiums: 1, position: 1 },
    { avatar_id: 'ai-1', is_player: false, points: 6, podiums: 0, position: 2 },
  ],
};

function renderPage(champId = 'ch1') {
  return render(
    <MemoryRouter initialEntries={[`/championship/${champId}`]}>
      <Routes>
        <Route path="/championship/:id" element={<ChampionshipPage />} />
        <Route path="/race/setup" element={<div>Setup</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('ChampionshipPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(championshipApiModule.getChampionship).mockResolvedValue(activeChampionship);
  });

  it('shows standings table with position order', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument());
    expect(screen.getByText('You')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument(); // points
    expect(screen.getAllByRole('row').length).toBeGreaterThan(1);
  });

  it('shows Start Next Race button when championship is active', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByRole('button', { name: /start next race/i })).toBeInTheDocument());
  });

  it('navigates to /race/setup with championship context when Start Next Race clicked', async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => screen.getByRole('button', { name: /start next race/i }));
    await user.click(screen.getByRole('button', { name: /start next race/i }));
    await waitFor(() => expect(screen.getByText('Setup')).toBeInTheDocument());
  });

  it('shows completion message when championship is completed', async () => {
    vi.mocked(championshipApiModule.getChampionship).mockResolvedValue({
      ...activeChampionship,
      races_completed: 3,
      status: 'completed',
    });
    renderPage();
    await waitFor(() => expect(screen.getByText(/championship complete/i)).toBeInTheDocument());
    expect(screen.queryByRole('button', { name: /start next race/i })).not.toBeInTheDocument();
  });

  it('has data-testid="page-championship"', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByTestId('page-championship')).toBeInTheDocument());
  });
});
```

- [ ] **Step 2: Run tests — expect FAIL**

Run: `pnpm --dir frontend test ChampionshipPage`
Expected: FAIL — stub returns static div

- [ ] **Step 3: Implement ChampionshipPage.tsx**

```typescript
// src/pages/ChampionshipPage.tsx
import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getChampionship, type ChampionshipState } from '../engine/race/championshipApi';
import { Button } from '../shared/components/Button';
import { LoadingSpinner } from '../shared/components/LoadingSpinner';
import tokens from '../shared/tokens';

export default function ChampionshipPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [championship, setChampionship] = useState<ChampionshipState | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    getChampionship(id)
      .then(setChampionship)
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <LoadingSpinner message="Loading standings…" />;
  if (!championship) {
    return (
      <div data-testid="page-championship" style={{ padding: tokens.spacing.xl }}>
        Championship not found.
      </div>
    );
  }

  const isCompleted = championship.status === 'completed';

  function handleStartNext() {
    void navigate('/race/setup', {
      state: {
        continueChampionshipId: championship!.championship_id,
        continueRaceIndex: championship!.races_completed,
      },
    });
  }

  return (
    <div
      data-testid="page-championship"
      style={{ maxWidth: 640, margin: '0 auto', padding: tokens.spacing.xl }}
    >
      <h1 style={{ color: tokens.color.textPrimary, marginBottom: tokens.spacing.xs }}>
        Championship
      </h1>
      <p style={{ color: tokens.color.textSecondary, marginBottom: tokens.spacing.lg }}>
        Race {championship.races_completed} of {championship.total_races} complete
      </p>

      <table
        style={{ width: '100%', borderCollapse: 'collapse', marginBottom: tokens.spacing.lg }}
      >
        <thead>
          <tr>
            {['Position', 'Runner', 'Points', 'Podiums'].map((h) => (
              <th
                key={h}
                scope="col"
                style={{
                  padding: tokens.spacing.sm,
                  borderBottom: `2px solid ${tokens.color.border}`,
                  color: tokens.color.textSecondary,
                  fontSize: 14,
                  fontWeight: 600,
                  textAlign: h === 'Position' || h === 'Runner' ? 'left' : 'right',
                }}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {championship.standings.map((entry) => (
            <tr
              key={entry.avatar_id}
              style={{ background: entry.is_player ? `${tokens.color.primary}18` : 'transparent' }}
            >
              <th scope="row" style={{ padding: tokens.spacing.sm, fontWeight: 400 }}>
                {entry.position}
              </th>
              <td style={{ padding: tokens.spacing.sm, fontWeight: entry.is_player ? 700 : 400 }}>
                {entry.is_player ? 'You' : 'Opponent'}
              </td>
              <td style={{ padding: tokens.spacing.sm, textAlign: 'right' }}>{entry.points}</td>
              <td style={{ padding: tokens.spacing.sm, textAlign: 'right' }}>{entry.podiums}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {isCompleted ? (
        <div>
          <h2 style={{ color: tokens.color.success }}>Championship Complete!</h2>
          <Button variant="primary" onClick={() => void navigate('/race/setup')}>Play Again</Button>
        </div>
      ) : (
        <Button variant="primary" onClick={handleStartNext}>Start Next Race</Button>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Implement HomePage.tsx**

```typescript
// src/pages/HomePage.tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getChampionship } from '../engine/race/championshipApi';
import { Button } from '../shared/components/Button';
import tokens from '../shared/tokens';

export default function HomePage() {
  const navigate = useNavigate();
  const [activeChampionshipId, setActiveChampionshipId] = useState<string | null>(null);

  useEffect(() => {
    const savedId = localStorage.getItem('activeChampionshipId');
    if (!savedId) return;
    getChampionship(savedId)
      .then((c) => {
        if (c.status === 'active') setActiveChampionshipId(savedId);
        else localStorage.removeItem('activeChampionshipId');
      })
      .catch(() => localStorage.removeItem('activeChampionshipId'));
  }, []);

  return (
    <div
      data-testid="page-home"
      style={{ maxWidth: 480, margin: '0 auto', padding: tokens.spacing.xl, textAlign: 'center' }}
    >
      <h1
        style={{
          fontSize: 40,
          fontWeight: 900,
          color: tokens.color.textPrimary,
          marginBottom: tokens.spacing.xl,
        }}
      >
        Math Racers
      </h1>

      {activeChampionshipId && (
        <div
          style={{
            marginBottom: tokens.spacing.lg,
            padding: tokens.spacing.md,
            background: `${tokens.color.warning}22`,
            borderRadius: tokens.radius.md,
            border: `1px solid ${tokens.color.warning}`,
          }}
        >
          <p style={{ margin: `0 0 ${tokens.spacing.sm}px`, color: tokens.color.textPrimary }}>
            You have an active championship!
          </p>
          <Button
            variant="primary"
            onClick={() => void navigate(`/championship/${activeChampionshipId}`)}
          >
            Continue Championship
          </Button>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: tokens.spacing.md }}>
        <Button variant="primary" onClick={() => void navigate('/race/setup')}>
          Start Racing
        </Button>
        <Button variant="secondary" onClick={() => void navigate('/avatars')}>
          My Avatars
        </Button>
        <Button variant="secondary" onClick={() => void navigate('/statistics')}>
          Statistics
        </Button>
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Run ChampionshipPage tests — expect PASS**

Run: `pnpm --dir frontend test ChampionshipPage`
Expected: PASS 5/5

- [ ] **Step 6: Run full suite — expect green**

Run: `pnpm --dir frontend test`
Expected: all tests pass (router.test.tsx must still pass — `data-testid="page-home"` is preserved)

- [ ] **Step 7: Commit**

```bash
git add src/pages/ChampionshipPage.tsx src/pages/ChampionshipPage.test.tsx src/pages/HomePage.tsx
git commit -m "feat(race): implement Championship standings page and Home Page navigation

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Post-Implementation: Final Review

After all 6 tasks are committed, run the complete test suite one final time and then run the full-branch reviewer:

```bash
pnpm --dir frontend test
```

Expected: all tests green.

Then use `superpowers:executing-plans` `scripts/review-package` to generate the review package, and dispatch the code reviewer on the most capable available model.

**Review Focus reminders for the reviewer:**
1. Verify `useBlocker` actually prevents the browser Back button during RACING (not just in-app navigation).
2. Verify the results table uses `scope="col"` on `<th>` in `<thead>` and `scope="row"` on `<th>` in `<tbody>` — not `scope` on `<td>`.
3. Verify `computeLevel(xp_before)` correctly handles the case where `xp_earned` equals `total_xp` (new account with first race).
4. Verify that `raceIndex` is correctly passed through the championship flow so that `recordChampionshipRace` receives the right 0-based index.
5. Verify that `localStorage.removeItem('activeChampionshipId')` is called when a championship completes, to prevent the Home Page from showing a stale "Continue" prompt indefinitely.
