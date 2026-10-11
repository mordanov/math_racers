# Sprint 6 — UI Polish: Kid-Friendly Visual Redesign

**Date:** 2026-10-11  
**Audience:** Children aged 5–10 (primary), parents (secondary)  
**Scope:** Visual-only — no logic, routing, component interfaces, or tests changed

---

## Goals

Transform the current clean-but-bland adult UI into a warm, energetic, kid-friendly experience:
- Chunky rounded shapes, warm saturated colors, large touch targets
- Buttons always readable against any background (including artwork backgrounds)
- Expressive but not overwhelming animations
- Preserve every existing `data-testid`, `aria-*`, and component interface

---

## 1. Design Tokens (`src/shared/tokens.ts`)

Single source of truth for all visual styling. Changes here cascade app-wide.

### Colors

| Token | Old | New | Rationale |
|-------|-----|-----|-----------|
| `primary` | `#4A90D9` | `#FF6B35` | Warm coral — energetic, inviting for kids |
| `primaryHover` | `#3A7BC8` | `#E85C28` | Darker coral |
| `primaryActive` | `#2E6AAD` | `#CC4F1E` | Used for 3D button shadow |
| `success` | `#5CB85C` | `#2DC653` | Vivid green for correct answers |
| `warning` | `#F0AD4E` | `#FFD60A` | Sunny yellow for timer |
| `error` | `#D9534F` | `#FF4D6D` | Pink-red for wrong answers |
| `background` | `#FEFAF3` | `#FFF8F0` | Warm cream |
| `surface` | `#FFFFFF` | `#FFFFFF` | Cards — unchanged |
| `border` | `#E8E2D9` | `#FFD6B3` | Soft peach outline |
| `focus` | `#60A5FA` | `#4CC9F0` | Sky-blue focus ring |

All other color tokens (`textPrimary`, `textSecondary`, `textOnPrimary`, `shadow`) unchanged.

### Spacing

Unchanged — existing scale works well for touch targets.

### Border Radius

| Token | Old | New |
|-------|-----|-----|
| `sm` | 8 | 12 |
| `md` | 16 | 20 |
| `lg` | 24 | 32 |
| `xl` | 32 | 44 |

### Animation Durations

| Token | Old | New |
|-------|-----|-----|
| `micro` | 100ms | 120ms |
| `standard` | 250ms | 300ms |
| `expressive` | 400ms | 500ms |

### Font Sizes (new object)

Add `fontSize` to the token object:

```ts
fontSize: {
  base: 18,
  lg: 20,
  xl: 24,
  xxl: 32,
  hero: 48,
}
```

Used by Button and key pages to replace magic numbers.

---

## 2. Animations (`src/shared/animations.css`)

Add three new keyframes for kid-friendly feedback:

```css
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

@keyframes pop {
  0% { transform: scale(1); }
  50% { transform: scale(1.15); }
  100% { transform: scale(1); }
}

@keyframes wiggle {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-6deg); }
  75% { transform: rotate(6deg); }
}
```

Add `prefers-reduced-motion` guards for all three (matching existing pattern).

---

## 3. Button (`src/shared/components/Button.tsx`)

**No interface changes.** Visual changes only — all three variants get solid backgrounds.

### Primary
- Background: `tokens.color.primary` (coral)
- Box shadow: `0 6px 0 tokens.color.primaryActive` — 3D press look
- Hover: `transform: translateY(-2px)`, shadow `0 8px 0 primaryActive`
- Active/press: `transform: translateY(4px)`, shadow `0 2px 0 primaryActive`
- Font size: `tokens.fontSize.base` (18px)
- Font weight: 800
- Letter spacing: `0.02em`
- Border radius: `tokens.radius.lg` (32px)
- Padding: `tokens.spacing.md` vertical, `tokens.spacing.xl` horizontal

### Secondary
- Background: `tokens.color.surface` (white) — **no longer transparent**
- Border: `3px solid tokens.color.primary`
- Color: `tokens.color.primary`
- Hover: same `translateY(-2px)` lift, background `#FFF0EA` (light coral tint)
- Same font/radius/padding as primary

### Ghost
- Background: `rgba(255,255,255,0.9)` — **no longer fully transparent**
- No border
- Color: `tokens.color.textPrimary`
- Hover: background `tokens.color.surface`

### Transition
Add `transform` and `box-shadow` to the existing transition string.

---

## 4. Key Pages (hardcoded value fixes)

Only pages with hardcoded font sizes / colors that bypass tokens are touched.

### `HomePage.tsx`
- Title `fontSize: 40` → `tokens.fontSize.hero`
- Add `textShadow: '2px 2px 0 rgba(0,0,0,0.15)'` to title for legibility on background image

### `RaceScreenPage.tsx`
- Problem card `fontSize: 48` → `tokens.fontSize.hero` (same value, now token-driven)
- Progress track height `24 → 32` for thicker, more visible lanes
- Runner ball diameter `20 → 28` for easier visual tracking
- Countdown digit `fontSize: 96` — intentionally kept as magic number (dramatic effect)

### `ResultsScreenPage.tsx`
- Level-up banner font: `28 → tokens.fontSize.xxl` (32px)
- Achievement badge size: `64 → 80px` — easier to celebrate

### `LoginPage.tsx` / `RegisterPage.tsx`
- Heading `fontSize: 28 → tokens.fontSize.xl` (24px) — adult context, slightly calmer
- Input border-radius: `tokens.radius.sm` → `tokens.radius.md` (follows new token values automatically)
- No special treatment beyond token inheritance

---

## Non-Changes (explicit)

The following are **not** touched:
- All `data-testid` attributes
- All `aria-*` attributes and roles
- Component props/interfaces
- Engine, hooks, routing, API clients
- `ParentDashboardPage` — inherits token changes passively, no direct edits
- `ChildProfileSelectPage`, `AvatarCreatorPage`, `AvatarGalleryPage`, `ChampionshipPage`, `StatisticsPage`, `SettingsPage` — inherit token changes passively

---

## Testing

No new tests required — this is pure styling with no behavioral change.  
Existing tests remain valid: they test IDs, roles, and text content, none of which change.  
Visual verification: run dev server and walk through HomePage → RaceScreen → Results after implementation.
