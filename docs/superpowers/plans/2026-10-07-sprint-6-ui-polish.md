# Sprint 6 — UI Polish & Asset Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire up audio/image assets, add offline detection, and complete the remaining UI polish items required by `spec-ui-implementation.md`.

**Architecture:** All tasks are additive to existing pages; no routes or shared components are replaced. Audio uses HTMLAudioElement managed via a React hook. Static assets are served from Vite's `publicDir` (project-root `assets/`). Offline detection uses `navigator.onLine` + a lightweight network probe.

**Tech Stack:** React 18, Vite, TypeScript, HTMLAudioElement, navigator.onLine, vitest + react-testing-library

**Spec:** `docs/ui/spec-ui-implementation.md` (also `docs/art/ui-style.md` for design tokens)

## Global Constraints

- All tokens come from `src/shared/tokens.ts`; no hardcoded colours or radii.
- `prefers-reduced-motion` must disable non-essential animations (existing `animations.css`).
- `Array.from({ length: n }, () => v)` not `Array(n).fill(v)`.
- Use `vi.hoisted(() => vi.fn())` for module-level mock functions in Vitest.
- Never `eslint-disable-next-line react-hooks/exhaustive-deps` (plugin not in CI).
- Run `pnpm prettier --write`, `pnpm eslint src`, `pnpm tsc --noEmit` before committing.

## Review Focus

1. **Audio plays after hot-reload / HMR**: AudioManager creates a new HTMLAudioElement on each render without a `useRef` — audio may double-play.
2. **Offline probe fires on every render instead of once**: `useOffline`'s probe must be called in a `useEffect`, not unconditionally.
3. **Race Setup shows duel/championship modes while offline**: Only Training Mode should be available; other modes should be hidden/disabled.
4. **Settings volume changes don't affect already-playing music**: The audio manager must react to `localStorage` changes, not just read on mount.
5. **AvatarCard `onSelect` version renders achievement names > 24 chars without truncation**: Truncation must be applied to the display string in both the `<button>` and `<div>` variants.

---

### Task 1: Vite publicDir — serve root assets/

**Files:**
- Modify: `frontend/vite.config.ts`
- Test: inline — no separate test file needed (verified by dev server response)

**Interfaces:**
- Produces: `/audio/music_menu_1.wav`, `/audio/music_menu_2.wav`, `/audio/music_race_1.wav`, `/audio/music_race_2.wav`, `/audio/music_victory_1.wav`, `/audio/music_victory_2.wav`, `/achievements/1-6.png`, `/mainmenu.png`, `/loading.png`, `/stadium.png`, `/avatar_generation.jpeg` all served from `/`

- [ ] **Step 1: Update vite.config.ts to add publicDir**

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  publicDir: "../assets",
  plugins: [react()],
  test: {
    environment: "happy-dom",
    passWithNoTests: true,
    globals: true,
    setupFiles: ["./src/test-setup.ts"],
  },
});
```

- [ ] **Step 2: Verify paths are resolvable**

Run: `cd frontend && pnpm tsc --noEmit`
Expected: 0 errors (no TypeScript changes)

- [ ] **Step 3: Commit**

```bash
git add frontend/vite.config.ts
git commit -m "chore: serve root assets/ as Vite publicDir

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 2: useAudioManager hook

**Files:**
- Create: `frontend/src/shared/hooks/useAudioManager.ts`
- Create: `frontend/src/shared/hooks/useAudioManager.test.ts`

**Interfaces:**
- Produces:
  ```typescript
  type MusicTrack = 'menu' | 'race' | 'victory';

  interface AudioManager {
    playMusic(track: MusicTrack): void;
    stopMusic(): void;
  }

  export function useAudioManager(): AudioManager
  ```
- Track → file mapping (randomly picks between two tracks for menu and race):
  - `menu`: randomly `/audio/music_menu_1.wav` or `/audio/music_menu_2.wav`
  - `race`: randomly `/audio/music_race_1.wav` or `/audio/music_race_2.wav`
  - `victory`: randomly `/audio/music_victory_1.wav` or `/audio/music_victory_2.wav`
- Reads volume from localStorage keys `settings.masterVolume` (0–100), `settings.musicVolume` (0–100)
  - effective volume = `(master / 100) * (music / 100)`, default 1.0 if key absent
- Music loops: `audio.loop = true`
- Victory music: does NOT loop (`audio.loop = false`)
- `stopMusic()` pauses and resets `currentTime = 0`
- `play()` may throw (browser autoplay policy) — catch and swallow silently
- The hook uses `useRef` for the HTMLAudioElement to avoid creating duplicates

- [ ] **Step 1: Write failing test**

```typescript
// frontend/src/shared/hooks/useAudioManager.test.ts
import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAudioManager } from './useAudioManager';

const mockAudio = {
  play: vi.fn().mockResolvedValue(undefined),
  pause: vi.fn(),
  loop: false,
  volume: 1,
  currentTime: 0,
  src: '',
};

vi.mock('./useAudioManager', async (importOriginal) => {
  // We test the real implementation, not a mock
  return importOriginal();
});

// Mock HTMLAudioElement globally
beforeEach(() => {
  vi.spyOn(window, 'Audio' as keyof Window).mockImplementation(
    () => mockAudio as unknown as HTMLAudioElement,
  );
  mockAudio.play.mockResolvedValue(undefined);
  mockAudio.loop = false;
  mockAudio.volume = 1;
  mockAudio.currentTime = 0;
  mockAudio.src = '';
});

describe('useAudioManager', () => {
  it('plays music and sets loop=true for menu track', async () => {
    const { result } = renderHook(() => useAudioManager());
    await act(async () => {
      result.current.playMusic('menu');
    });
    expect(mockAudio.play).toHaveBeenCalled();
    expect(mockAudio.loop).toBe(true);
  });

  it('does not loop victory music', async () => {
    const { result } = renderHook(() => useAudioManager());
    await act(async () => {
      result.current.playMusic('victory');
    });
    expect(mockAudio.loop).toBe(false);
  });

  it('stops music on stopMusic()', async () => {
    const { result } = renderHook(() => useAudioManager());
    await act(async () => {
      result.current.playMusic('race');
      result.current.stopMusic();
    });
    expect(mockAudio.pause).toHaveBeenCalled();
    expect(mockAudio.currentTime).toBe(0);
  });

  it('applies volume from localStorage', async () => {
    localStorage.setItem('settings.masterVolume', '50');
    localStorage.setItem('settings.musicVolume', '80');
    const { result } = renderHook(() => useAudioManager());
    await act(async () => {
      result.current.playMusic('menu');
    });
    // 0.5 * 0.8 = 0.4
    expect(mockAudio.volume).toBeCloseTo(0.4, 2);
    localStorage.removeItem('settings.masterVolume');
    localStorage.removeItem('settings.musicVolume');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && pnpm test src/shared/hooks/useAudioManager.test.ts`
Expected: FAIL — `useAudioManager` not found

- [ ] **Step 3: Implement useAudioManager**

```typescript
// frontend/src/shared/hooks/useAudioManager.ts
import { useCallback, useRef } from 'react';

export type MusicTrack = 'menu' | 'race' | 'victory';

const TRACK_FILES: Record<MusicTrack, string[]> = {
  menu: ['/audio/music_menu_1.wav', '/audio/music_menu_2.wav'],
  race: ['/audio/music_race_1.wav', '/audio/music_race_2.wav'],
  victory: ['/audio/music_victory_1.wav', '/audio/music_victory_2.wav'],
};

function readVolume(): number {
  try {
    const master = parseInt(localStorage.getItem('settings.masterVolume') ?? '100', 10);
    const music = parseInt(localStorage.getItem('settings.musicVolume') ?? '100', 10);
    return (master / 100) * (music / 100);
  } catch {
    return 1;
  }
}

export function useAudioManager() {
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const stopMusic = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
  }, []);

  const playMusic = useCallback(
    (track: MusicTrack) => {
      stopMusic();
      const files = TRACK_FILES[track];
      const file = files[Math.floor(Math.random() * files.length)];
      const audio = new Audio(file);
      audio.loop = track !== 'victory';
      audio.volume = readVolume();
      audioRef.current = audio;
      audio.play().catch(() => {
        // Autoplay blocked — silently ignore
      });
    },
    [stopMusic],
  );

  return { playMusic, stopMusic };
}
```

- [ ] **Step 4: Run tests and verify pass**

Run: `cd frontend && pnpm test src/shared/hooks/useAudioManager.test.ts`
Expected: PASS 4/4

- [ ] **Step 5: Run full suite**

Run: `cd frontend && pnpm test`
Expected: All pass

- [ ] **Step 6: Commit**

```bash
git add frontend/src/shared/hooks/useAudioManager.ts frontend/src/shared/hooks/useAudioManager.test.ts
git commit -m "feat(audio): add useAudioManager hook for music playback

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Wire music to pages

**Files:**
- Modify: `frontend/src/pages/HomePage.tsx`
- Modify: `frontend/src/pages/RaceScreenPage.tsx`
- Modify: `frontend/src/pages/ResultsScreenPage.tsx`
- Modify: `frontend/src/router.test.tsx` (add mocks for useAudioManager)

**Interfaces:**
- Consumes: `useAudioManager` from `../shared/hooks/useAudioManager`
- Rules:
  - HomePage: call `playMusic('menu')` on mount; `stopMusic()` on unmount
  - RaceScreenPage `RaceScreen` component: call `playMusic('race')` when `state === 'RACING'`; stop on unmount
  - ResultsScreenPage `ResultsScreen`: call `playMusic('victory')` on mount; stop on unmount
  - router.test.tsx: mock `../../shared/hooks/useAudioManager` to prevent audio in tests

- [ ] **Step 1: Write failing tests**

```typescript
// Add to frontend/src/pages/HomePage.tsx test — create HomePageAudio.test.tsx
// frontend/src/pages/HomePageAudio.test.tsx
import { render } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

const mockPlayMusic = vi.hoisted(() => vi.fn());
const mockStopMusic = vi.hoisted(() => vi.fn());

vi.mock('../shared/hooks/useAudioManager', () => ({
  useAudioManager: () => ({ playMusic: mockPlayMusic, stopMusic: mockStopMusic }),
}));

vi.mock('../engine/race/championshipApi', () => ({
  getChampionship: () => Promise.reject(new Error('no')),
}));

import HomePage from './HomePage';

beforeEach(() => {
  mockPlayMusic.mockClear();
  mockStopMusic.mockClear();
});

describe('HomePage audio', () => {
  it('plays menu music on mount', () => {
    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    );
    expect(mockPlayMusic).toHaveBeenCalledWith('menu');
  });

  it('stops music on unmount', () => {
    const { unmount } = render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    );
    unmount();
    expect(mockStopMusic).toHaveBeenCalled();
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd frontend && pnpm test src/pages/HomePageAudio.test.tsx`
Expected: FAIL — mockPlayMusic not called (HomePage doesn't use audio yet)

- [ ] **Step 3: Wire audio to HomePage**

Add to `HomePage.tsx`:
```typescript
import { useAudioManager } from '../shared/hooks/useAudioManager';

// Inside HomePage component, at top:
const { playMusic, stopMusic } = useAudioManager();

useEffect(() => {
  playMusic('menu');
  return () => stopMusic();
}, []); // playMusic/stopMusic are stable callbacks
```

- [ ] **Step 4: Wire audio to RaceScreenPage (RaceScreen component)**

In `RaceScreen` component, add after the existing `useEffect` hooks:
```typescript
import { useAudioManager } from '../../shared/hooks/useAudioManager';

const { playMusic, stopMusic } = useAudioManager();

useEffect(() => {
  if (state === 'RACING') {
    playMusic('race');
  }
  return () => {
    if (state === 'RACING') stopMusic();
  };
}, [state]); // intentional: only start/stop on state change
```

- [ ] **Step 5: Wire audio to ResultsScreenPage (ResultsScreen component)**

In `ResultsScreen` component:
```typescript
import { useAudioManager } from '../../shared/hooks/useAudioManager';

const { playMusic, stopMusic } = useAudioManager();

useEffect(() => {
  playMusic('victory');
  return () => stopMusic();
}, []); // stable refs
```

- [ ] **Step 6: Add useAudioManager mock to router.test.tsx**

In `router.test.tsx` add alongside the existing `vi.mock` calls:
```typescript
vi.mock('./shared/hooks/useAudioManager', () => ({
  useAudioManager: () => ({ playMusic: vi.fn(), stopMusic: vi.fn() }),
}));
```

- [ ] **Step 7: Run tests**

Run: `cd frontend && pnpm test src/pages/HomePageAudio.test.tsx`
Expected: PASS 2/2

Run: `cd frontend && pnpm test`
Expected: All pass

- [ ] **Step 8: Commit**

```bash
git add frontend/src/pages/HomePage.tsx frontend/src/pages/RaceScreenPage.tsx frontend/src/pages/ResultsScreenPage.tsx frontend/src/pages/HomePageAudio.test.tsx frontend/src/router.test.tsx
git commit -m "feat(audio): wire music playback to Home, Race, and Results pages

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 4: Background images on key pages

**Files:**
- Modify: `frontend/src/pages/HomePage.tsx`
- Modify: `frontend/src/shared/components/LoadingSpinner.tsx`
- Modify: `frontend/src/pages/RaceScreenPage.tsx`

**Interfaces:**
- Consumes: `/mainmenu.png`, `/loading.png`, `/stadium.png` (served from publicDir)
- No new tests needed — visual-only changes; existing page tests should still pass

- [ ] **Step 1: Add mainmenu.png to HomePage background**

In HomePage, wrap the content div with a full-bleed background:
```tsx
// Outer wrapper gets the background image
<div
  data-testid="page-home"
  style={{
    minHeight: '100vh',
    backgroundImage: 'url(/mainmenu.png)',
    backgroundSize: 'cover',
    backgroundPosition: 'center',
    backgroundRepeat: 'no-repeat',
  }}
>
  <div style={{ maxWidth: 480, margin: '0 auto', padding: tokens.spacing.xl, textAlign: 'center' }}>
    {/* existing content */}
  </div>
</div>
```

- [ ] **Step 2: Add loading image to LoadingSpinner**

Modify `LoadingSpinner.tsx` to show `/loading.png` if the `useImage` approach is too complex — use a simple `<img>` alongside the spinner:
```tsx
// frontend/src/shared/components/LoadingSpinner.tsx
// Replace the existing spinner with the loading image + text:
<div
  style={{
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: tokens.spacing.md,
    padding: tokens.spacing.xl,
  }}
>
  <img
    src="/loading.png"
    alt=""
    aria-hidden="true"
    style={{ width: 120, height: 'auto' }}
  />
  {message && (
    <p style={{ color: tokens.color.textSecondary, margin: 0 }}>{message}</p>
  )}
</div>
```

- [ ] **Step 3: Add stadium background to RaceScreen**

In `RaceScreen` component's outermost container, add background:
```tsx
style={{
  maxWidth: 640,
  margin: '0 auto',
  padding: tokens.spacing.xl,
  backgroundImage: 'url(/stadium.png)',
  backgroundSize: 'cover',
  backgroundPosition: 'center bottom',
  backgroundRepeat: 'no-repeat',
  minHeight: '100vh',
}}
```

- [ ] **Step 4: Run full suite to ensure no regressions**

Run: `cd frontend && pnpm test`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/HomePage.tsx frontend/src/shared/components/LoadingSpinner.tsx frontend/src/pages/RaceScreenPage.tsx
git commit -m "feat(ui): add background images to Home, Loading, and Race pages

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 5: Achievement badge images in Results

**Files:**
- Create: `frontend/src/features/achievements/achievementBadges.ts`
- Modify: `frontend/src/pages/ResultsScreenPage.tsx`

**Interfaces:**
- Achievement badge files at these paths (from publicDir):
  - `/achievements/1-6.png` — achievements for ids: first_race, perfect_race (generic levels 1-6)
  - `/achievements/7-8.png` — level 7-8
  - `/achievements/champion.png` — champion
  - `/achievements/first_race.png` — first race
  - `/achievements/hidden_speedster.png` — hidden speedster
  - `/achievements/level_10.png` — level 10
  - `/achievements/level_20.png` — level 20
  - `/achievements/level_5.png` — level 5
  - `/achievements/perfect_race.png` — perfect race
  - `/achievements/podium_finisher.png` — podium finisher
- Produces:
  ```typescript
  export function getBadgeUrl(achievementId: string): string
  ```
  - Returns `/achievements/<id>.png` if a known match; falls back to `/achievements/1-6.png`

- [ ] **Step 1: Write failing test**

```typescript
// frontend/src/features/achievements/achievementBadges.test.ts
import { describe, it, expect } from 'vitest';
import { getBadgeUrl } from './achievementBadges';

describe('getBadgeUrl', () => {
  it('returns correct path for known achievement id', () => {
    expect(getBadgeUrl('first_race')).toBe('/achievements/first_race.png');
  });

  it('returns correct path for level_10', () => {
    expect(getBadgeUrl('level_10')).toBe('/achievements/level_10.png');
  });

  it('falls back to 1-6.png for unknown achievement', () => {
    expect(getBadgeUrl('unknown_achievement_xyz')).toBe('/achievements/1-6.png');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && pnpm test src/features/achievements/achievementBadges.test.ts`
Expected: FAIL — module not found

- [ ] **Step 3: Implement achievementBadges.ts**

```typescript
// frontend/src/features/achievements/achievementBadges.ts
const KNOWN_BADGE_IDS = new Set([
  '1-6',
  '7-8',
  'champion',
  'first_race',
  'hidden_speedster',
  'level_10',
  'level_20',
  'level_5',
  'perfect_race',
  'podium_finisher',
]);

export function getBadgeUrl(achievementId: string): string {
  const id = KNOWN_BADGE_IDS.has(achievementId) ? achievementId : '1-6';
  return `/achievements/${id}.png`;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd frontend && pnpm test src/features/achievements/achievementBadges.test.ts`
Expected: PASS 3/3

- [ ] **Step 5: Update ResultsScreenPage to show badge images**

Replace the plain toast in `ResultsScreenPage.tsx` with a badge display. After the `achievements` state is populated, render a row of badges above the table:

```tsx
import { getBadgeUrl } from '../features/achievements/achievementBadges';

{/* After level-up banner, before table: */}
{achievements.length > 0 && (
  <div
    style={{
      display: 'flex',
      gap: tokens.spacing.md,
      flexWrap: 'wrap',
      marginBottom: tokens.spacing.lg,
    }}
  >
    {achievements.map((a) => (
      <div key={a.id} style={{ textAlign: 'center' }}>
        <img
          src={getBadgeUrl(a.id)}
          alt={a.title}
          style={{ width: 64, height: 64, borderRadius: '50%' }}
        />
        <div style={{ fontSize: 12, color: tokens.color.textSecondary, marginTop: tokens.spacing.xs }}>
          {a.title}
        </div>
      </div>
    ))}
  </div>
)}
```

Keep the existing `NotificationToast` for each achievement (provides screen-reader announcement too).

- [ ] **Step 6: Run full suite**

Run: `cd frontend && pnpm test`
Expected: All pass

- [ ] **Step 7: Commit**

```bash
git add frontend/src/features/achievements/achievementBadges.ts frontend/src/features/achievements/achievementBadges.test.ts frontend/src/pages/ResultsScreenPage.tsx
git commit -m "feat(achievements): display badge images in results screen

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 6: Offline detection and page degradation

**Files:**
- Create: `frontend/src/shared/hooks/useOffline.ts`
- Create: `frontend/src/shared/hooks/useOffline.test.ts`
- Modify: `frontend/src/pages/AvatarCreatorPage.tsx`
- Modify: `frontend/src/pages/ParentDashboardPage.tsx`
- Modify: `frontend/src/pages/RaceSetupPage.tsx`

**Interfaces:**
- Produces:
  ```typescript
  export function useOffline(): boolean
  // Returns true when the browser cannot reach the network
  ```
- Mechanism: `navigator.onLine` + subscribes to `online`/`offline` window events
- Consumes:
  - `AvatarCreatorPage`: if offline, show "Internet required to create avatars" with back button; skip all API calls
  - `ParentDashboardPage`: if offline, show "Internet required to view parent dashboard"; skip all API calls
  - `RaceSetupPage`: if offline, hide all modes except 'training'; the existing `mode` state defaults to 'quick', so when offline set it to 'training' and disable the other mode buttons

- [ ] **Step 1: Write failing test for useOffline**

```typescript
// frontend/src/shared/hooks/useOffline.test.ts
import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { useOffline } from './useOffline';

describe('useOffline', () => {
  let originalOnLine: boolean;

  beforeEach(() => {
    originalOnLine = navigator.onLine;
  });

  afterEach(() => {
    Object.defineProperty(navigator, 'onLine', { value: originalOnLine, configurable: true });
  });

  it('returns false when navigator.onLine is true', () => {
    Object.defineProperty(navigator, 'onLine', { value: true, configurable: true });
    const { result } = renderHook(() => useOffline());
    expect(result.current).toBe(false);
  });

  it('returns true when navigator.onLine is false', () => {
    Object.defineProperty(navigator, 'onLine', { value: false, configurable: true });
    const { result } = renderHook(() => useOffline());
    expect(result.current).toBe(true);
  });

  it('updates when offline event fires', () => {
    Object.defineProperty(navigator, 'onLine', { value: true, configurable: true });
    const { result } = renderHook(() => useOffline());
    expect(result.current).toBe(false);
    act(() => {
      Object.defineProperty(navigator, 'onLine', { value: false, configurable: true });
      window.dispatchEvent(new Event('offline'));
    });
    expect(result.current).toBe(true);
  });

  it('updates when online event fires', () => {
    Object.defineProperty(navigator, 'onLine', { value: false, configurable: true });
    const { result } = renderHook(() => useOffline());
    expect(result.current).toBe(true);
    act(() => {
      Object.defineProperty(navigator, 'onLine', { value: true, configurable: true });
      window.dispatchEvent(new Event('online'));
    });
    expect(result.current).toBe(false);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && pnpm test src/shared/hooks/useOffline.test.ts`
Expected: FAIL — `useOffline` not found

- [ ] **Step 3: Implement useOffline**

```typescript
// frontend/src/shared/hooks/useOffline.ts
import { useEffect, useState } from 'react';

export function useOffline(): boolean {
  const [offline, setOffline] = useState(!navigator.onLine);

  useEffect(() => {
    const handleOffline = () => setOffline(true);
    const handleOnline = () => setOffline(false);
    window.addEventListener('offline', handleOffline);
    window.addEventListener('online', handleOnline);
    return () => {
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('online', handleOnline);
    };
  }, []);

  return offline;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd frontend && pnpm test src/shared/hooks/useOffline.test.ts`
Expected: PASS 4/4

- [ ] **Step 5: Add offline guard to AvatarCreatorPage**

At the top of the `AvatarCreatorPage` component (before the wizard state):
```tsx
import { useOffline } from '../shared/hooks/useOffline';

// Inside the component:
const isOffline = useOffline();

if (isOffline) {
  return (
    <div
      data-testid="page-avatar-creator"
      role="alert"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: tokens.spacing.lg,
        padding: tokens.spacing.xl,
        textAlign: 'center',
      }}
    >
      <p style={{ fontSize: 20, color: tokens.color.textPrimary }}>
        Internet required to create avatars.
      </p>
      <Button variant="secondary" onClick={() => void navigate(-1)}>
        Go Back
      </Button>
    </div>
  );
}
```

- [ ] **Step 6: Add offline guard to ParentDashboardPage**

At the top of the `ParentDashboardPage` component (before API calls):
```tsx
import { useOffline } from '../shared/hooks/useOffline';

const isOffline = useOffline();

if (isOffline) {
  return (
    <div
      data-testid="page-parent-dashboard"
      role="alert"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: tokens.spacing.lg,
        padding: tokens.spacing.xl,
        textAlign: 'center',
      }}
    >
      <p style={{ fontSize: 20, color: tokens.color.textPrimary }}>
        Internet required to view parent dashboard.
      </p>
      <Button variant="secondary" onClick={() => void navigate(-1)}>
        Go Back
      </Button>
    </div>
  );
}
```

- [ ] **Step 7: Add offline mode restriction to RaceSetupPage**

In `RaceSetupPage.tsx`:
```tsx
import { useOffline } from '../shared/hooks/useOffline';

// Inside component:
const isOffline = useOffline();

// In the useEffect that sets initial mode, add:
useEffect(() => {
  if (isOffline) setMode('training');
}, [isOffline]);

// When rendering mode buttons, disable non-training modes when offline:
{MODES.map(({ mode: m, label }) => (
  <Button
    key={m}
    variant={mode === m ? 'primary' : 'secondary'}
    disabled={isOffline && m !== 'training'}
    onClick={() => handleModeChange(m)}
  >
    {label}
    {isOffline && m !== 'training' ? ' (offline)' : ''}
  </Button>
))}
```

- [ ] **Step 8: Run full suite**

Run: `cd frontend && pnpm test`
Expected: All pass

- [ ] **Step 9: Run type-check**

Run: `cd frontend && pnpm tsc --noEmit`
Expected: 0 errors

- [ ] **Step 10: Commit**

```bash
git add frontend/src/shared/hooks/useOffline.ts frontend/src/shared/hooks/useOffline.test.ts frontend/src/pages/AvatarCreatorPage.tsx frontend/src/pages/ParentDashboardPage.tsx frontend/src/pages/RaceSetupPage.tsx
git commit -m "feat(offline): detect offline state; disable creator/dashboard; training-only race setup

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 7: Avatar name truncation and AvatarCard display name

**Files:**
- Modify: `frontend/src/features/avatar/AvatarCard.tsx`
- Modify: `frontend/src/features/avatar/AvatarCard.test.tsx`

**Interfaces:**
- Spec requires: truncate display at 24 characters with ellipsis; full name stored in backend
- `displayName` in `AvatarCard` is currently `avatar.name ?? avatar.species`
- Change: truncate `displayName` at 24 chars for the visible label; use the full name in `title` attribute for tooltip

- [ ] **Step 1: Write failing test**

```typescript
// Add to frontend/src/features/avatar/AvatarCard.test.tsx
it('truncates long avatar names at 24 characters with ellipsis', () => {
  const longName = 'A'.repeat(30);
  const { getByText } = render(
    <AvatarCard
      avatar={{
        avatar_id: '1',
        name: longName,
        species: 'fox',
        status: 'published',
        is_favourite: false,
        portrait: null,
        created_at: '2024-01-01',
      }}
    />,
  );
  expect(getByText(longName.slice(0, 24) + '…')).toBeInTheDocument();
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && pnpm test src/features/avatar/AvatarCard.test.tsx`
Expected: FAIL — long name renders without truncation

- [ ] **Step 3: Implement name truncation in AvatarCard**

Change the `displayName` line:
```typescript
const rawName = avatar.name ?? avatar.species;
const displayName = rawName.length > 24 ? rawName.slice(0, 24) + '…' : rawName;
```

Add `title={rawName}` to the name `<div>`:
```tsx
<div
  title={rawName}
  style={{ fontWeight: 600, color: tokens.color.textPrimary, overflow: 'hidden', whiteSpace: 'nowrap' }}
>
  {displayName}
</div>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd frontend && pnpm test src/features/avatar/AvatarCard.test.tsx`
Expected: All pass

- [ ] **Step 5: Run full suite**

Run: `cd frontend && pnpm test`
Expected: All pass

- [ ] **Step 6: Run pre-commit checks**

Run: `cd frontend && pnpm prettier --write src && pnpm eslint src && pnpm tsc --noEmit`
Expected: 0 errors, 0 warnings

- [ ] **Step 7: Commit**

```bash
git add frontend/src/features/avatar/AvatarCard.tsx frontend/src/features/avatar/AvatarCard.test.tsx
git commit -m "feat(avatar): truncate display names longer than 24 characters

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## Final Notes

After all tasks, run the full suite one final time and do a whole-branch review.
