# Sprint 8: Auth Page Styling + Avatar Gallery Completion

**Date:** 2026-10-07
**Branch:** `worktree-014-sprint-6-ui-polish`
**Status:** Approved design — ready for implementation planning

---

## Problem Statement

Two areas of the frontend are functional but unpolished or incomplete:

1. **Auth pages (LoginPage, RegisterPage, ChildProfileSelectPage)** are wired to real APIs and navigate correctly, but render raw HTML with no token-based styling. They look broken next to the rest of the app and do not match the card + centered-form layout established by the design system.

2. **Avatar Gallery (AvatarGalleryPage / AvatarCard / useAvatarGallery)** is styled but read-only. Users cannot mark an avatar as a favourite, rename it, regenerate its portrait, or delete it. The gallery also exposes `/parent` without a role check — any authenticated user can reach it.

This sprint makes the auth pages look right and gives the gallery its full set of interactions.

---

## Section 1: Auth Page Styling + Parent Guard

### Layout

All three auth pages use a full-page centred-card layout:

```
page background: tokens.color.background
  ↓
centred column (max-width 420px, auto horizontal margin)
  ↓
Card (surface, radius.lg, shadow.card, spacing.lg padding)
  ↓
  title (h1, textPrimary)
  form / content
  navigation link(s) at bottom
```

### LoginPage

- `<Card>` wrapping the form content
- Styled `<label>` + `<input>` for email and password (full-width, border: `tokens.color.border`, borderRadius: `tokens.radius.sm`, padding: `tokens.spacing.sm`)
- Error message uses `tokens.color.error`
- `Button variant="primary"` (already present, just needs to be inside the card layout)
- Link to `/register` below the form: "Don't have an account? Register" (`tokens.color.primary`, no underline)

### RegisterPage

- Same `<Card>` structure as LoginPage
- Success state: show the "Account created. Please wait for approval." text inside the card with a success icon or green colour (`tokens.color.success`)
- Link to `/login` below the form: "Already have an account? Log in"

### ChildProfileSelectPage

- Page-level heading "Who's Playing?" centred above a card
- Profile list rendered as a CSS grid of clickable `<Card>` buttons (auto-fill, min 120px columns)
- Each profile card: avatar placeholder circle (40px, `tokens.color.border` background) + display name
- "Add profile" form sits below the grid inside its own `<Card>` section, with the same styled `<input>` + `Button variant="primary"` as above
- Error/loading states use existing patterns (`LoadingSpinner` / `role="alert"`)

### RequireParent Guard

New file: `frontend/src/infrastructure/auth/RequireParent.tsx`

```ts
export default function RequireParent() {
  const { account, isLoading } = useAuth();
  if (isLoading) return <LoadingSpinner />;
  if (account?.role !== 'parent') return <Navigate to="/" replace />;
  return <Outlet />;
}
```

Wire it in `router.tsx`: wrap the `/parent` route in a `<RequireParent>` element the same way `<RequireAuth>` wraps the authenticated subtree. The `/parent` route then becomes a child of `<RequireParent>` instead of a direct sibling under `<RequireAuth>`.

---

## Section 2: Avatar Gallery Completion

### Favourite Toggle

Each `AvatarCard` gains a star button (top-right corner, absolute-positioned inside the card).

- Filled star (★) when `avatar.is_favourite === true`, hollow star (☆) otherwise
- Button size: `tokens.touchTarget` (44px) tap target, `aria-label="Remove from favourites"` / `"Add to favourites"`
- On click: call `onFavourite(avatar.avatar_id, !avatar.is_favourite)` — provided by `AvatarGalleryPage`
- Optimistic update: `useAvatarGallery` flips `is_favourite` immediately in local state, then calls `patchAvatar(id, { is_favourite })`. On API error, reverts the item to the previous value and sets a non-blocking error string.

### Manage Menu (⋯)

Each card gains a `⋯` button (bottom-right, absolute) with three inline actions:

**Rename:** replaces the avatar's name `<div>` with a controlled `<input>` in-place. Pressing Enter or the "Save" button calls `patchAvatar(id, { name })` and exits edit mode. Pressing Escape cancels with no API call.

**Regenerate:** calls `regeneratePortrait(id)`. On success the response carries a new `job_id` and `status: 'pending'`; the hook updates the avatar locally and the existing polling interval takes over.

**Delete:** opens `<ConfirmDialog>` ("Delete avatar?" / "This cannot be undone."). On confirm, the avatar is removed from local state immediately (optimistic), then `deleteAvatar(id)` is called. On error the item is restored and an error message is shown.

### Hook Extensions (`useAvatarGallery`)

Add three mutation functions alongside the existing state:

```ts
toggleFavourite: (avatarId: string, isFavourite: boolean) => Promise<void>
renameAvatar:    (avatarId: string, name: string)          => Promise<void>
startRegenerate: (avatarId: string)                        => Promise<void>
removeAvatar:    (avatarId: string)                        => Promise<void>
```

Each mutation applies an optimistic update to `avatars` state first, then calls the API, reverting on error. `startRegenerate` patches the local item to `status: 'pending'` and lets the existing 3-second polling interval handle subsequent updates.

### AvatarCard Callback Props

Add to the `AvatarCardProps` interface:

```ts
onFavourite?: (avatarId: string, isFavourite: boolean) => void;
onRename?:    (avatarId: string, name: string)          => void;
onRegenerate?:(avatarId: string) => void;
onDelete?:    (avatarId: string) => void;
```

All four are optional — cards without them (e.g. in the race setup selector) render as before with no manage chrome.

### AvatarGalleryPage wiring

The page destructures the four mutation functions from `useAvatarGallery` and passes them to each `AvatarCard`. It also shows a dismissible inline error banner (role="alert") when any mutation fails — wired to a `mutationError` string returned by the hook.

---

## Constraints and Conventions

- All styling via `tokens` (inline styles); no new CSS files, no Tailwind.
- No new npm dependencies.
- Existing `<Button>`, `<Card>`, `<ConfirmDialog>`, `<LoadingSpinner>` — use them, do not reimplement.
- Manage actions (`⋯` menu) are inline state on the card (`useState`), not a floating dropdown — keeps the DOM simple and accessible.
- Tests: Vitest + Testing Library. Mocks via `vi.hoisted()`. No `eslint-disable-next-line react-hooks/exhaustive-deps`.
- Array helpers use `Array.from({ length: n }, () => v)` (not `Array(n).fill(v)`).
- All new paths are inside `frontend/src/`.

---

## Out of Scope for This Sprint

- Avatar sort / filter controls on the gallery page.
- Favourite ordering (backend already stores the flag; sorting UI is a later sprint).
- `/parent` dashboard content — only the route guard is added here.
- Administrator role routes — not touched.
