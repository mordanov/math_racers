# Sprint 11: Artwork Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire all remaining artwork assets into the game — fix two wrong path references and add three illustrations to pages that currently have no artwork.

**Architecture:** Pure one-liner and JSX additions. No new components, no new hooks, no abstraction. Assets are already served via Vite `publicDir: "../assets"` so the paths just work.

**Tech Stack:** React JSX, inline styles, Vite static asset serving.

**Spec:** `docs/superpowers/specs/2026-10-09-sprint-11-artwork-design.md`

## Global Constraints

- No new npm dependencies
- No new components — only add `<img>` tags and fix `url(...)` strings inside existing files
- `alt=""` + `aria-hidden="true"` on all decorative images (these are visual-only illustrations)
- All image paths are absolute from the Vite public root: `/artwork/<filename>`
- No new tests — existing suites must stay green; tests do not assert on `backgroundImage` or `<img>` src

## Review Focus

1. Path typo: `/artwork/` prefix is required on all new `src` and `url(...)` values. A missing slash or extra segment serves a 404 silently — the image just does not appear.
2. `aria-hidden="true"` and `alt=""` must co-exist on each decorative `<img>`. Missing one is not a blocker at runtime but fails accessibility audit.
3. `AvatarCreatorPage` generation waiting state: confirm the image is added inside the waiting branch, not outside it. The spec says "between the loading spinner/heading and the status text" — placing it outside the conditional renders on every step.
4. `LoadingSpinner` renders in multiple places; adding the artwork there affects every loading screen simultaneously, which is intentional — but verify that no existing test renders `LoadingSpinner` in a way that would break on the new `<img>`.
5. `ResultsScreenPage` achievements section: the `<img>` should appear once per results render, not inside a `.map()`. Adding it inside the toast list would duplicate it per achievement.

---

### Task 1: Fix wrong artwork path references

**Files:**
- Modify: `frontend/src/pages/HomePage.tsx`
- Modify: `frontend/src/pages/RaceScreenPage.tsx`

**Interfaces:**
- Consumes: nothing — standalone one-line edits
- Produces: correct background images at `/artwork/mainmenu.png` and `/artwork/stadium.png`

- [ ] **Step 1: Locate and verify the wrong paths**

```bash
grep -n "mainmenu\|stadium" frontend/src/pages/HomePage.tsx frontend/src/pages/RaceScreenPage.tsx
```

Expected: two matches — one `url(/mainmenu.png)` in `HomePage.tsx` and one `url(/stadium.png)` in `RaceScreenPage.tsx`.

- [ ] **Step 2: Fix `HomePage.tsx`**

Change `url(/mainmenu.png)` → `url(/artwork/mainmenu.png)`.

The line looks like:
```tsx
backgroundImage: 'url(/mainmenu.png)',
```
Change to:
```tsx
backgroundImage: 'url(/artwork/mainmenu.png)',
```

- [ ] **Step 3: Fix `RaceScreenPage.tsx`**

Change `url(/stadium.png)` → `url(/artwork/stadium.png)`.

The line looks like:
```tsx
backgroundImage: 'url(/stadium.png)',
```
Change to:
```tsx
backgroundImage: 'url(/artwork/stadium.png)',
```

- [ ] **Step 4: Verify no other wrong paths remain**

```bash
grep -rn "url(/mainmenu\|url(/stadium\|url(/loading\|url(/achievements\|url(/avatar_generation" frontend/src/
```

Expected: zero matches (all paths now use the `/artwork/` prefix).

- [ ] **Step 5: Run full test suite**

```bash
cd frontend && pnpm test
```
Expected: green (no tests assert on `backgroundImage`).

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/HomePage.tsx frontend/src/pages/RaceScreenPage.tsx
git commit -m "fix(artwork): correct background image paths to /artwork/ prefix

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 2: Wire `avatar_generation.jpeg` into `AvatarCreatorPage`

**Files:**
- Modify: `frontend/src/pages/AvatarCreatorPage.tsx`

**Interfaces:**
- Consumes: nothing — additive JSX change inside the generation waiting state
- Produces: decorative illustration visible while AI generates the avatar portrait

- [ ] **Step 1: Locate the generation waiting state in `AvatarCreatorPage.tsx`**

```bash
grep -n "loading\|generating\|waiting\|LoadingSpinner\|step.*5\|5.*step" frontend/src/pages/AvatarCreatorPage.tsx | head -30
```

Read the relevant section (~line 400) to confirm where the spinner/status text is rendered for the waiting state (Step 5 of the avatar creation flow). The target insertion point is between the heading/spinner and the status text.

- [ ] **Step 2: Add the illustration image**

In the generation waiting state JSX, add the `<img>` between the spinner (or heading) and the status text paragraph:

```tsx
<img
  src="/artwork/avatar_generation.jpeg"
  alt=""
  aria-hidden="true"
  style={{ width: 240, borderRadius: tokens.radius.lg, objectFit: 'cover', display: 'block', margin: '0 auto' }}
/>
```

Ensure `tokens` is already imported in this file (it will be — all pages use the design tokens). If `tokens.radius.lg` is not the correct token path in this codebase, substitute the equivalent (read the tokens file if unsure: `frontend/src/shared/design/tokens.ts` or similar).

- [ ] **Step 3: Confirm the image is inside the conditional branch**

Read the surrounding JSX to verify the `<img>` is rendered only when the generation waiting state is active, not on every step of the avatar creator.

- [ ] **Step 4: Run test suite**

```bash
cd frontend && pnpm test AvatarCreatorPage
```
Expected: green (no tests assert on img src).

Full suite:
```bash
cd frontend && pnpm test
```
Expected: green.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/AvatarCreatorPage.tsx
git commit -m "feat(artwork): add generation illustration to AvatarCreatorPage waiting state

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 3: Wire `loading.png` into `LoadingSpinner`

**Files:**
- Modify: `frontend/src/shared/components/LoadingSpinner.tsx`

**Interfaces:**
- Consumes: nothing — additive JSX change
- Produces: artwork illustration visible on all loading screens

- [ ] **Step 1: Read `LoadingSpinner.tsx`**

```bash
cat -n frontend/src/shared/components/LoadingSpinner.tsx
```

Understand the current structure: where the spinner element is, and where to add the image (above or alongside the spinner).

- [ ] **Step 2: Add the artwork image**

Add the `<img>` above the existing spinner element (or as the primary visual if the spinner is only a CSS animation):

```tsx
<img
  src="/artwork/loading.png"
  alt=""
  aria-hidden="true"
  style={{ width: 160, display: 'block', margin: '0 auto 16px' }}
/>
```

Keep the existing spinner element — the image supplements it, not replaces it.

- [ ] **Step 3: Run test suite**

```bash
cd frontend && pnpm test LoadingSpinner
```
Expected: green.

Full suite:
```bash
cd frontend && pnpm test
```
Expected: green. If any test snapshot breaks, update the snapshot.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/shared/components/LoadingSpinner.tsx
git commit -m "feat(artwork): add loading illustration to LoadingSpinner component

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 4: Wire `achievements.png` into `ResultsScreenPage`

**Files:**
- Modify: `frontend/src/pages/ResultsScreenPage.tsx`

**Interfaces:**
- Consumes: nothing — additive JSX change
- Produces: decorative banner above the achievements section in the results screen

- [ ] **Step 1: Locate the achievements section in `ResultsScreenPage.tsx`**

```bash
grep -n "achievement\|AchievementToast\|trophy\|badge" frontend/src/pages/ResultsScreenPage.tsx | head -20
```

Read the surrounding JSX to find the section header or container that holds the achievements list/toasts. The image goes above this section, outside any `.map()` loop.

- [ ] **Step 2: Add the banner image**

Above the achievements section container (but inside the results page content area), add:

```tsx
<img
  src="/artwork/achievements.png"
  alt=""
  aria-hidden="true"
  style={{ width: '100%', maxWidth: 640, borderRadius: tokens.radius.lg, display: 'block', margin: '0 auto 12px' }}
/>
```

Verify `tokens` is imported (it will be). If `tokens.radius.lg` differs from what this file uses, match the existing pattern.

- [ ] **Step 3: Confirm the image appears exactly once**

Read the surrounding JSX to confirm the `<img>` is not inside a `.map()` or conditional that would render it multiple times or conditionally.

- [ ] **Step 4: Run test suite**

```bash
cd frontend && pnpm test ResultsScreenPage
```
Expected: green.

Full suite:
```bash
cd frontend && pnpm test
```
Expected: green.

- [ ] **Step 5: Run type check + lint**

```bash
cd frontend && pnpm tsc --noEmit && pnpm lint
```
Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/ResultsScreenPage.tsx
git commit -m "feat(artwork): add achievements banner to ResultsScreenPage

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```
