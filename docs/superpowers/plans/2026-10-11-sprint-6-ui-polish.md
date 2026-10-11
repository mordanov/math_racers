# Sprint 6 UI Polish — Kid-Friendly Visual Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the adult-neutral visual design with a warm, chunky, kid-friendly theme (coral primary, rounded shapes, 3D buttons, bigger type) without touching any app logic, routes, or component interfaces.

**Architecture:** All styling flows through `tokens.ts` — changing it cascades app-wide. Five additional pages have hardcoded font sizes / pixel values that bypass tokens and must be patched directly. `Button.tsx` gets React hover/press state to drive the 3D press effect via inline styles (matching the codebase's existing pattern of no CSS modules).

**Tech Stack:** React 18, TypeScript, Vite, inline styles via `tokens.ts`, Vitest + Testing Library

**Spec:** `docs/superpowers/specs/2026-10-11-sprint-6-ui-polish-design.md`

## Global Constraints

- Do NOT change any `data-testid`, `aria-*` attribute, or ARIA role.
- Do NOT change any component prop interface or export shape.
- Do NOT add new dependencies.
- Do NOT touch engine, hooks, routing, API clients, or test files.
- `Button` must keep `minHeight: tokens.touchTarget` (44px) — existing test asserts `>= 44`.
- `ghost` and `secondary` button variants must have solid (non-transparent) backgrounds.
- New CSS keyframes must include `prefers-reduced-motion` guards matching the existing pattern in `animations.css`.
- Run `npm run fmt:check && npm run typecheck && npm run test` in `frontend/` after every task before committing.

## Review Focus

1. **Contrast: coral (#FF6B35) as `secondary` border/text color on white** — must remain legible; verify in browser that secondary button text reads clearly at small sizes.
2. **Buttons on artwork backgrounds** — `secondary` (white bg) and `ghost` (rgba white) on `mainmenu.png` (HomePage) and `stadium.png` (RaceScreen) must be readable; verified visually, not by unit tests.
3. **Timer bar warning color** — changed from muted gold `#F0AD4E` to bright yellow `#FFD60A`; on the cream background (`#FFF8F0`) this may lose contrast. Verify the yellow band reads as "caution" not "invisible" in RaceScreen. *(Task 4, Step 5)*
4. **Hover/press effects on touch devices** — `onMouseEnter`/`onMouseDown` don't fire on touch; new visual effects are desktop-only. Not a regression (didn't exist before) but call it out in manual QA.
5. **Reduced-motion guards** — `bounce`, `pop`, `wiggle` are new keyframes; forgetting their guard silently violates user accessibility preferences. *(Task 2, Step 2)*

---

## File Map

| File | Action | What changes |
|------|--------|-------------|
| `frontend/src/shared/tokens.ts` | Modify | New color palette, bumped radii, longer durations, new `fontSize` object |
| `frontend/src/shared/animations.css` | Modify | Add `bounce`, `pop`, `wiggle` keyframes + reduced-motion guards |
| `frontend/src/shared/components/Button.tsx` | Modify | Hover/press state, 3D shadow, solid variant backgrounds, bigger padding/font |
| `frontend/src/pages/HomePage.tsx` | Modify | Title font size → `tokens.fontSize.hero`, add text shadow |
| `frontend/src/pages/RaceScreenPage.tsx` | Modify | Track height 24→32, ball size 20→28, problem font → `tokens.fontSize.hero` |
| `frontend/src/pages/ResultsScreenPage.tsx` | Modify | Level-up font → `tokens.fontSize.xxl`, badge size 64→80 |
| `frontend/src/pages/LoginPage.tsx` | Modify | Heading font size 28 → `tokens.fontSize.xl` |
| `frontend/src/pages/RegisterPage.tsx` | Modify | Heading font size 28 → `tokens.fontSize.xl` |

---

## Task 1: Update Design Tokens

**Files:**
- Modify: `frontend/src/shared/tokens.ts`

**Interfaces:**
- Produces: `tokens.fontSize` object (`base`, `lg`, `xl`, `xxl`, `hero`) — consumed by Tasks 3 and 4
- Produces: updated `tokens.color.*`, `tokens.radius.*`, `tokens.animation.*` — consumed by all components passively

- [ ] **Step 1: Replace the tokens file**

Replace the entire file with:

```ts
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
    sm: 12,
    md: 20,
    lg: 32,
    xl: 44,
  },
  animation: {
    micro: '120ms',
    quick: '150ms',
    standard: '300ms',
    expressive: '500ms',
  },
  fontSize: {
    base: 18,
    lg: 20,
    xl: 24,
    xxl: 32,
    hero: 48,
  },
  color: {
    primary: '#FF6B35',
    primaryHover: '#E85C28',
    primaryActive: '#CC4F1E',
    success: '#2DC653',
    warning: '#FFD60A',
    error: '#FF4D6D',
    focus: '#4CC9F0',
    background: '#FFF8F0',
    surface: '#FFFFFF',
    textPrimary: '#1A1209',
    textSecondary: '#6B6560',
    textOnPrimary: '#FFFFFF',
    border: '#FFD6B3',
    shadow: 'rgba(0,0,0,0.08)',
  },
  shadow: {
    card: '0 4px 16px rgba(0,0,0,0.08)',
    cardHover: '0 8px 24px rgba(0,0,0,0.12)',
    overlay: '0 16px 48px rgba(0,0,0,0.2)',
  },
  touchTarget: 44,
} as const;

export default tokens;
```

- [ ] **Step 2: Type-check and run tests**

```bash
cd frontend && npm run typecheck && npm run test
```

Expected: all tests pass. If TypeScript complains about `tokens.fontSize` being used before Task 3/4 (it won't — new key is additive), that's a type narrowing issue; check callers.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/shared/tokens.ts
git commit -m "style(tokens): kid-friendly palette, radii, durations, and font sizes"
```

---

## Task 2: Add Kid Animation Keyframes

**Files:**
- Modify: `frontend/src/shared/animations.css`

**Interfaces:**
- Produces: `.bounce`, `.pop`, `.wiggle` CSS class names — available globally (file imported in `main.tsx`)

- [ ] **Step 1: Add keyframes and reduced-motion guards**

Append to the end of `frontend/src/shared/animations.css` (after the existing `@media (prefers-reduced-motion: reduce)` block):

```css
@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

@keyframes pop {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.15);
  }
  100% {
    transform: scale(1);
  }
}

@keyframes wiggle {
  0%,
  100% {
    transform: rotate(0deg);
  }
  25% {
    transform: rotate(-6deg);
  }
  75% {
    transform: rotate(6deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .bounce {
    animation: none !important;
  }
  .pop {
    animation: none !important;
  }
  .wiggle {
    animation: none !important;
  }
}
```

- [ ] **Step 2: Verify reduced-motion guards are present**

Open `frontend/src/shared/animations.css` and confirm the file now has exactly two `@media (prefers-reduced-motion: reduce)` blocks — the original (spin/pulse/slideIn) and the new one (bounce/pop/wiggle). If you accidentally merged them into one block, that's fine as long as all six class names appear inside it.

- [ ] **Step 3: Run tests**

```bash
cd frontend && npm run test
```

Expected: all pass (no tests reference CSS keyframes directly).

- [ ] **Step 4: Commit**

```bash
git add frontend/src/shared/animations.css
git commit -m "style(animations): add bounce, pop, wiggle keyframes for kid UI"
```

---

## Task 3: Update Button Component

**Files:**
- Modify: `frontend/src/shared/components/Button.tsx`
- Test: `frontend/src/shared/components/Button.test.tsx` (read — do not modify)

**Interfaces:**
- Consumes: `tokens.fontSize.base` (18) from Task 1, `tokens.radius.lg` (32), `tokens.color.primaryActive` ('#CC4F1E'), `tokens.color.surface`, `tokens.animation.micro`
- Produces: same `Button` export with identical props interface — no breaking changes

- [ ] **Step 1: Read the existing Button test**

Open `frontend/src/shared/components/Button.test.tsx` and note:
- The `'has minimum touch target size'` test checks `parseInt(btn.style.minHeight) >= 44`. Keep `minHeight: tokens.touchTarget` (44) in the base style.
- The `'fires ui_hover sfx on mouse enter when playSound is true'` test uses `user.hover()` which fires `mouseenter`. The new `onMouseEnter` handler must still call `playSfx('ui_hover')` when `playSound` is true.

Do not modify the test file.

- [ ] **Step 2: Replace Button.tsx**

Replace the entire file with:

```tsx
import { useState } from 'react';
import { useSfxPlayer } from '../hooks/useSfxPlayer';
import tokens from '../tokens';

interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  type?: 'button' | 'submit' | 'reset';
  'aria-label'?: string;
  playSound?: boolean;
}

const baseStyle: React.CSSProperties = {
  borderRadius: tokens.radius.lg,
  padding: `${tokens.spacing.md}px ${tokens.spacing.xl}px`,
  minHeight: tokens.touchTarget,
  minWidth: tokens.touchTarget,
  fontSize: tokens.fontSize.base,
  fontWeight: 800,
  letterSpacing: '0.02em',
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: tokens.spacing.xs,
  outline: 'none',
  position: 'relative',
  transition: `opacity ${tokens.animation.micro}, transform ${tokens.animation.micro}, box-shadow ${tokens.animation.micro}`,
};

const variantBase: Record<ButtonProps['variant'], React.CSSProperties> = {
  primary: {
    background: tokens.color.primary,
    color: tokens.color.textOnPrimary,
    border: 'none',
    boxShadow: `0 6px 0 ${tokens.color.primaryActive}`,
  },
  secondary: {
    background: tokens.color.surface,
    color: tokens.color.primary,
    border: `3px solid ${tokens.color.primary}`,
    boxShadow: 'none',
  },
  ghost: {
    background: 'rgba(255,255,255,0.9)',
    color: tokens.color.textPrimary,
    border: 'none',
    boxShadow: 'none',
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
  playSound = false,
}: ButtonProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [isPressed, setIsPressed] = useState(false);
  const isInert = disabled || loading;
  const { playSfx } = useSfxPlayer();

  let interactionStyle: React.CSSProperties = {};
  if (!isInert && isPressed && variant === 'primary') {
    interactionStyle = {
      transform: 'translateY(4px)',
      boxShadow: `0 2px 0 ${tokens.color.primaryActive}`,
    };
  } else if (!isInert && isHovered) {
    if (variant === 'primary') {
      interactionStyle = {
        transform: 'translateY(-2px)',
        boxShadow: `0 8px 0 ${tokens.color.primaryActive}`,
      };
    } else if (variant === 'secondary') {
      interactionStyle = { transform: 'translateY(-2px)', background: '#FFF0EA' };
    } else if (variant === 'ghost') {
      interactionStyle = { background: tokens.color.surface };
    }
  }

  const style: React.CSSProperties = {
    ...baseStyle,
    ...variantBase[variant],
    ...interactionStyle,
    cursor: isInert ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.4 : 1,
  };

  return (
    <button
      type={type}
      style={style}
      disabled={isInert}
      onClick={
        isInert
          ? undefined
          : () => {
              if (playSound) playSfx('ui_click');
              onClick?.();
            }
      }
      onMouseEnter={
        isInert
          ? undefined
          : () => {
              setIsHovered(true);
              if (playSound) playSfx('ui_hover');
            }
      }
      onMouseLeave={isInert ? undefined : () => { setIsHovered(false); setIsPressed(false); }}
      onMouseDown={isInert ? undefined : () => setIsPressed(true)}
      onMouseUp={isInert ? undefined : () => setIsPressed(false)}
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

- [ ] **Step 3: Run Button tests**

```bash
cd frontend && npm run test -- --reporter=verbose src/shared/components/Button.test.tsx
```

Expected: all 9 tests pass. If `'has minimum touch target size'` fails, you accidentally removed `minHeight: tokens.touchTarget` from `baseStyle` — add it back.

- [ ] **Step 4: Run full test suite**

```bash
cd frontend && npm run fmt:check && npm run typecheck && npm run test
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/shared/components/Button.tsx
git commit -m "style(button): 3D press effect, solid variant backgrounds, kid-friendly sizing"
```

---

## Task 4: Fix Hardcoded Values on Key Pages

**Files:**
- Modify: `frontend/src/pages/HomePage.tsx`
- Modify: `frontend/src/pages/RaceScreenPage.tsx`
- Modify: `frontend/src/pages/ResultsScreenPage.tsx`
- Modify: `frontend/src/pages/LoginPage.tsx`
- Modify: `frontend/src/pages/RegisterPage.tsx`

**Interfaces:**
- Consumes: `tokens.fontSize.hero` (48), `tokens.fontSize.xxl` (32), `tokens.fontSize.xl` (24) from Task 1

**Note:** Each page change below is a targeted surgical edit — only the specific lines listed change. Everything else in each file stays as-is.

- [ ] **Step 1: Update HomePage — title font size and text shadow**

In `frontend/src/pages/HomePage.tsx`, find the `<h1>` style block:

```tsx
          fontSize: 40,
          fontWeight: 900,
          color: tokens.color.textPrimary,
          marginBottom: tokens.spacing.xl,
```

Change to:

```tsx
          fontSize: tokens.fontSize.hero,
          fontWeight: 900,
          color: tokens.color.textPrimary,
          marginBottom: tokens.spacing.xl,
          textShadow: '2px 2px 0 rgba(0,0,0,0.15)',
```

- [ ] **Step 2: Update RaceScreenPage — track height, ball size, problem font**

In `frontend/src/pages/RaceScreenPage.tsx`, make three targeted edits:

**Edit 1** — track lane height (in the progress bar `div` inside `runners.map`):
```tsx
              height: 24,
```
→
```tsx
              height: 32,
```

**Edit 2** — runner ball size (the dot `div` inside that same lane):
```tsx
                  width: 20,
                  height: 20,
```
→
```tsx
                  width: 28,
                  height: 28,
```

**Edit 3** — problem text font size (the `<p>` with the math equation):
```tsx
            fontSize: 48,
```
→
```tsx
            fontSize: tokens.fontSize.hero,
```

- [ ] **Step 3: Update ResultsScreenPage — level-up font and badge size**

In `frontend/src/pages/ResultsScreenPage.tsx`, make two targeted edits:

**Edit 1** — Level Up banner `<p>` (the big "Level Up!" text):
```tsx
          <p style={{ fontSize: 28, fontWeight: 900, margin: 0 }}>Level Up!</p>
```
→
```tsx
          <p style={{ fontSize: tokens.fontSize.xxl, fontWeight: 900, margin: 0 }}>Level Up!</p>
```

**Edit 2** — achievement badge image dimensions:
```tsx
              style={{ width: 64, height: 64, borderRadius: '50%' }}
```
→
```tsx
              style={{ width: 80, height: 80, borderRadius: '50%' }}
```

- [ ] **Step 4: Update LoginPage — heading font size**

In `frontend/src/pages/LoginPage.tsx`, find the `<h1>` style:
```tsx
            fontSize: 28,
            fontWeight: 700,
```
→
```tsx
            fontSize: tokens.fontSize.xl,
            fontWeight: 700,
```

- [ ] **Step 5: Update RegisterPage — heading font size**

In `frontend/src/pages/RegisterPage.tsx`, find the `<h1>` style:
```tsx
            fontSize: 28,
            fontWeight: 700,
```
→
```tsx
            fontSize: tokens.fontSize.xl,
            fontWeight: 700,
```

**Review Focus item:** While in RegisterPage, check that the `warning` color (`#FFD60A`) in RaceScreenPage's timer bar is visible. Open the dev server and navigate to a race; the yellow timer bar segment must read as a distinct "caution" warning against the cream background. If it washes out, change `tokens.color.warning` to `#F0A500` (darker amber) in `tokens.ts` — it's a token, one-line fix.

- [ ] **Step 6: Run all tests**

```bash
cd frontend && npm run fmt:check && npm run typecheck && npm run test
```

Expected: all pass. These pages have test files (`HomePage` has no test, but others like `RaceScreenPage.test.tsx` check `data-testid` and roles — all preserved).

- [ ] **Step 7: Commit**

```bash
git add \
  frontend/src/pages/HomePage.tsx \
  frontend/src/pages/RaceScreenPage.tsx \
  frontend/src/pages/ResultsScreenPage.tsx \
  frontend/src/pages/LoginPage.tsx \
  frontend/src/pages/RegisterPage.tsx
git commit -m "style(pages): replace hardcoded font sizes/dimensions with design tokens"
```

---

## Final Verification

- [ ] **Start the dev server and walk the golden path:**

```bash
cd frontend && npm run dev
```

1. `/login` — card readable, coral button present, heading not oversized
2. `/` (HomePage) — "Math Racers" title large and bold against background art
3. Start a race → RaceScreen — countdown legible, progress tracks thick, problem card readable, timer bar yellow/pink-red as time runs
4. Finish race → Results — "Level Up!" banner (if triggered) and achievement badges prominent
5. Check a secondary button (e.g., "My Avatars" on HomePage) — white background, coral border, readable on the artwork background

- [ ] **Final commit push**

```bash
git log --oneline -5
```

Confirm all 4 task commits are present, then proceed with PR or branch merge per project workflow.
