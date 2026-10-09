# Sprint 9: Accessibility Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the remaining accessibility gaps: wire the Settings page "Reduce motion" toggle into `useReducedMotion`, remove animated transitions under reduced motion in `RaceScreenPage`, and clean up the local `useReducedMotion` duplicate in `AchievementToast`.

**Architecture:** Three focused changes, all frontend. `useReducedMotion` gains a localStorage fallback (ORed with the media query) and a `storage` event listener so the Settings page checkbox takes effect immediately. `RaceScreenPage` consumes the hook to conditionally strip CSS transitions from the runner dot and timer bar. `AchievementToast` drops its local copy in favour of the shared hook.

**Tech Stack:** React 18, Vitest, @testing-library/react, TypeScript.

**Spec:** `docs/ui/spec-ui-implementation.md` §Accessibility (lines 210–220); `docs/superpowers/plans/2026-10-07-sprint-6-ui-polish.md` (prior sprint context).

## Global Constraints

- All styling via `tokens.ts` — no magic values.
- Use `vi.hoisted()` for any module-level mocks.
- No `eslint-disable react-hooks/exhaustive-deps`.
- Use `Array.from({ length: n }, () => v)` not `Array(n).fill(v)`.
- Run Prettier + ESLint + `pnpm tsc --noEmit` before every commit.
- Git attribution: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`.

## Review Focus

1. **Settings toggle doesn't take effect until page reload** — `useReducedMotion` must listen for `storage` events so the hook state updates the moment the Settings page writes its key, without a page reload.
2. **Runner dot transitions on slow networks** — when reduced motion is on, the runner dot `left` transition must be absent from the style object entirely, not `transition: 'none'` (which still includes a 0-duration transition causing a layout flush on some browsers).
3. **Test environment `window.matchMedia` absence** — happy-dom doesn't implement `matchMedia`; the hook must guard against `typeof window.matchMedia === 'undefined'` in tests, otherwise the hook crashes and every test that renders a component using it fails.
4. **AchievementToast local copy divergence** — the local `useReducedMotion` in `AchievementToast` has a subtly different implementation; deleting it and importing from shared must not break the existing animation/chime tests.
5. **Timer bar regression** — the timer bar transition (`width 0.1s linear`) is inline as a string literal, not using `tokens.animation.*`; the fix must target that exact string.

---

### Task 1: Extend `useReducedMotion` to honour Settings page preference

**Files:**
- Modify: `frontend/src/shared/hooks/useReducedMotion.ts`
- Test: `frontend/src/shared/hooks/useReducedMotion.test.ts`

**Interfaces:**
- Produces: `useReducedMotion(): boolean` — unchanged signature. Returns `true` when either `window.matchMedia('(prefers-reduced-motion: reduce)').matches` OR `localStorage.getItem('settings.reducedMotion') === 'true'`.

- [ ] **Step 1: Write failing test — initial state reads localStorage**

```ts
// frontend/src/shared/hooks/useReducedMotion.test.ts
import { renderHook } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { useReducedMotion } from './useReducedMotion';

// happy-dom may not have matchMedia; stub it
const mockMatchMedia = vi.fn().mockReturnValue({
  matches: false,
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
});

describe('useReducedMotion', () => {
  beforeEach(() => {
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: mockMatchMedia,
    });
    localStorage.clear();
  });
  afterEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('returns false when media query is false and localStorage is not set', () => {
    mockMatchMedia.mockReturnValue({ matches: false, addEventListener: vi.fn(), removeEventListener: vi.fn() });
    const { result } = renderHook(() => useReducedMotion());
    expect(result.current).toBe(false);
  });

  it('returns true when localStorage settings.reducedMotion is "true"', () => {
    localStorage.setItem('settings.reducedMotion', 'true');
    mockMatchMedia.mockReturnValue({ matches: false, addEventListener: vi.fn(), removeEventListener: vi.fn() });
    const { result } = renderHook(() => useReducedMotion());
    expect(result.current).toBe(true);
  });

  it('returns true when media query matches even without localStorage value', () => {
    mockMatchMedia.mockReturnValue({ matches: true, addEventListener: vi.fn(), removeEventListener: vi.fn() });
    const { result } = renderHook(() => useReducedMotion());
    expect(result.current).toBe(true);
  });
});
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
cd frontend && pnpm test useReducedMotion.test.ts
```
Expected: FAIL — `returns true when localStorage settings.reducedMotion is "true"` fails because the hook doesn't read localStorage.

- [ ] **Step 3: Implement the extended hook**

Replace the entire file:

```ts
// frontend/src/shared/hooks/useReducedMotion.ts
import { useEffect, useState } from 'react';

function readReducedMotion(): boolean {
  const mq =
    typeof window !== 'undefined' && typeof window.matchMedia === 'function'
      ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
      : false;
  let ls = false;
  try {
    ls = localStorage.getItem('settings.reducedMotion') === 'true';
  } catch {
    // localStorage unavailable
  }
  return mq || ls;
}

export function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(readReducedMotion);

  useEffect(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return;
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handleMq = () => setReduced(readReducedMotion());
    const handleStorage = (e: StorageEvent) => {
      if (e.key === 'settings.reducedMotion') setReduced(readReducedMotion());
    };
    mq.addEventListener('change', handleMq);
    window.addEventListener('storage', handleStorage);
    return () => {
      mq.removeEventListener('change', handleMq);
      window.removeEventListener('storage', handleStorage);
    };
  }, []);

  return reduced;
}
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
cd frontend && pnpm test useReducedMotion.test.ts
```
Expected: PASS 3/3.

- [ ] **Step 5: Run full suite**

```bash
cd frontend && pnpm test
```
Expected: all tests pass (no regressions).

- [ ] **Step 6: Lint + type-check**

```bash
cd frontend && pnpm prettier --write src/shared/hooks/useReducedMotion.ts src/shared/hooks/useReducedMotion.test.ts && pnpm eslint src/shared/hooks/useReducedMotion.ts src/shared/hooks/useReducedMotion.test.ts && pnpm tsc --noEmit
```
Expected: no errors.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/shared/hooks/useReducedMotion.ts frontend/src/shared/hooks/useReducedMotion.test.ts
git commit -m "$(cat <<'EOF'
feat(a11y): extend useReducedMotion to honour Settings page preference

Reads localStorage settings.reducedMotion in addition to the media query
so the Settings page checkbox takes effect immediately without reload.
Adds a storage event listener for cross-component reactivity.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Wire `useReducedMotion` into `RaceScreenPage` transitions

**Files:**
- Modify: `frontend/src/pages/RaceScreenPage.tsx`
- Test: `frontend/src/pages/RaceScreenPage.test.tsx`

**Interfaces:**
- Consumes: `useReducedMotion(): boolean` from `../../shared/hooks/useReducedMotion`
- Produces: no new exports; runner dot and timer bar inline `transition` values are `undefined` when `reduced === true`.

- [ ] **Step 1: Write failing test — transitions absent under reduced motion**

Add to `frontend/src/pages/RaceScreenPage.test.tsx` (find the describe block that renders the racing state and add after existing tests):

```tsx
// New test — add to existing describe in RaceScreenPage.test.tsx
import { vi } from 'vitest';

// At top of file, add:
// vi.mock('../shared/hooks/useReducedMotion');
// import * as reduceMotionModule from '../shared/hooks/useReducedMotion';

it('runner dot has no transition when reduced motion is active', async () => {
  vi.mocked(reduceMotionModule.useReducedMotion).mockReturnValue(true);
  // render in RACING state (reuse existing setup if available, otherwise minimal render)
  // The runner dot div uses `transition: `left ${tokens.animation.micro} ease-out``
  // With reduced motion it should be undefined/absent
  // This test verifies the style does not contain 'transition' on the runner position dot
  const { container } = renderInRacingState(); // helper already in the test file or add below
  // The runner position dot is a div with `position: 'absolute'` and `left: ...`
  const dots = container.querySelectorAll<HTMLElement>('[style*="position: absolute"]');
  dots.forEach((dot) => {
    expect(dot.style.transition).toBeFalsy();
  });
});
```

> **Note:** The existing test file may not have a `renderInRacingState` helper; adapt to whatever render setup already exists in `RaceScreenPage.test.tsx`. Read that file first and use the same pattern.

*Before writing the test, read `frontend/src/pages/RaceScreenPage.test.tsx` fully to match the existing pattern.*

- [ ] **Step 2: Read the test file and write the actual test**

Read `frontend/src/pages/RaceScreenPage.test.tsx`, then add at the top of the file:

```tsx
import * as reduceMotionModule from '../shared/hooks/useReducedMotion';

vi.mock('../shared/hooks/useReducedMotion');
```

And add one test inside the appropriate describe block:

```tsx
it('runner dot has no transition when useReducedMotion returns true', () => {
  vi.mocked(reduceMotionModule.useReducedMotion).mockReturnValue(true);
  // render with a racing state — use whatever render helper/factory already in this file
  // Then:
  // Every div with position absolute inside aria-label="Race track" should have no transition
  // Check the runner progress divs
});
```

Adapt to exact test patterns in the file. The key assertion: with `useReducedMotion` mocked to `true`, the runner dot element's `style.transition` must be falsy.

- [ ] **Step 3: Run test to confirm it fails**

```bash
cd frontend && pnpm test RaceScreenPage.test.tsx
```
Expected: new test fails because `RaceScreenPage` doesn't yet call `useReducedMotion`.

- [ ] **Step 4: Update `RaceScreenPage.tsx`**

Add the import near the top of the file:
```tsx
import { useReducedMotion } from '../shared/hooks/useReducedMotion';
```

Add inside the component, near the other hooks:
```tsx
const reduced = useReducedMotion();
```

Change the runner dot transition (currently `transition: \`left ${tokens.animation.micro} ease-out\``):
```tsx
transition: reduced ? undefined : `left ${tokens.animation.micro} ease-out`,
```

Change the timer bar transition (currently `transition: 'width 0.1s linear'`):
```tsx
transition: reduced ? undefined : 'width 0.1s linear',
```

Also add `aria-hidden="true"` to the `★` / AI-label span (line ~207) and add an `aria-label` to the runner row div that includes the runner identity and distance. The runner row `<div key={runner.runnerId} ...>` should become:

```tsx
<div
  key={runner.runnerId}
  aria-label={`${runner.isHuman ? 'You' : `CPU ${runner.runnerId.replace('ai-', '')}`}: ${runner.totalDistanceMetres}m`}
  style={{ ... }}
>
  <span aria-hidden="true" style={{ ... }}>
    {runner.isHuman ? '★' : runner.runnerId.replace('ai-', '')}
  </span>
  ...
  <span aria-hidden="true" style={{ ... }}>
    {runner.totalDistanceMetres}m
  </span>
</div>
```

- [ ] **Step 5: Run tests to confirm they pass**

```bash
cd frontend && pnpm test RaceScreenPage.test.tsx
```
Expected: all tests pass including new one.

- [ ] **Step 6: Run full suite**

```bash
cd frontend && pnpm test
```
Expected: all pass.

- [ ] **Step 7: Lint + type-check**

```bash
cd frontend && pnpm prettier --write src/pages/RaceScreenPage.tsx src/pages/RaceScreenPage.test.tsx && pnpm eslint src/pages/RaceScreenPage.tsx src/pages/RaceScreenPage.test.tsx && pnpm tsc --noEmit
```
Expected: no errors.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/pages/RaceScreenPage.tsx frontend/src/pages/RaceScreenPage.test.tsx
git commit -m "$(cat <<'EOF'
feat(a11y): disable RaceScreenPage transitions under reduced motion

Runner dot and timer bar transitions are removed when useReducedMotion
returns true. Runner row label spans gain aria-hidden and the row itself
gets an accessible aria-label combining identity and distance.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Remove `AchievementToast` local `useReducedMotion` duplicate

**Files:**
- Modify: `frontend/src/components/achievements/AchievementToast.tsx`
- Test: `frontend/src/components/achievements/AchievementToast.test.tsx` (existing)

**Interfaces:**
- Consumes: `useReducedMotion` from `../../../shared/hooks/useReducedMotion` (was local copy).
- Produces: no interface change — `AchievementToast` props and render are unchanged.

- [ ] **Step 1: Confirm existing tests pass before touching the file**

```bash
cd frontend && pnpm test AchievementToast
```
Expected: all existing tests pass (baseline).

- [ ] **Step 2: Replace local function with import**

In `frontend/src/components/achievements/AchievementToast.tsx`:

Remove lines 10–21 (the local `useReducedMotion` function definition).

Add import at the top:
```tsx
import { useReducedMotion } from '../../shared/hooks/useReducedMotion';
```

The relative path from `src/components/achievements/` to `src/shared/hooks/` is `../../shared/hooks/useReducedMotion`.

- [ ] **Step 3: Run tests to confirm nothing broke**

```bash
cd frontend && pnpm test AchievementToast
```
Expected: all pass. The behaviour is identical — the shared hook has the same signature and the same media query logic (plus the new localStorage logic from Task 1, which is an additive improvement).

- [ ] **Step 4: Run full suite**

```bash
cd frontend && pnpm test
```
Expected: all pass.

- [ ] **Step 5: Lint + type-check**

```bash
cd frontend && pnpm prettier --write src/components/achievements/AchievementToast.tsx && pnpm eslint src/components/achievements/AchievementToast.tsx && pnpm tsc --noEmit
```
Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/achievements/AchievementToast.tsx
git commit -m "$(cat <<'EOF'
refactor(a11y): replace AchievementToast local useReducedMotion with shared hook

Removes the duplicate implementation; both the media query and the new
localStorage-based preference from Task 1 now apply to the chime guard.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```
