# UI Screens & Components

**Level:** Specification
**Status:** Authoritative
**Source:** GDD Chapter 9
**Parent:** [Epic E5 — UI/UX](../prd.md)
**See also:** [../art/ui-style.md](../art/ui-style.md)

---

## Epic E5 Summary

Deliver every screen and component that a child, parent, or administrator interacts with. All UI follows the Art Bible visual language and UI Style Guide.

---

## Screen Inventory

### Authentication Screens

| Screen | Purpose |
|--------|---------|
| Login | Parent email/password entry |
| Register | New parent account creation |
| Child Profile Select | Choose which child profile to use |

### Main Navigation Screens

| Screen | Purpose |
|--------|---------|
| Home / Main Menu | Central hub: avatar display, quick actions, navigation |
| Mode Select | Choose Quick Race, Championship, Duel, or Training |

### Avatar Screens

| Screen | Purpose |
|--------|---------|
| Avatar Gallery | Browse, select, and manage all avatars |
| Avatar Creation | Step-by-step character creation wizard |
| Avatar Profile | View avatar details, biography, history, and statistics |
| Avatar Regeneration | Request new portrait while keeping old version |

### Race Screens

| Screen | Purpose |
|--------|---------|
| Race Lobby | Review participants, settings, and avatar before starting |
| Countdown | 3–2–1–GO animation |
| Race View | Active race: track, runners, current math problem |
| Race Results | Positions, XP earned, personal records, achievements triggered |
| Championship Standings | Cumulative standings between championship races |
| Championship Ceremony | Final ceremony at championship end |

### Progression Screens

| Screen | Purpose |
|--------|---------|
| Statistics | Player and avatar statistics, charts, and history |
| Achievements | Full achievement gallery with locked/unlocked states |
| Level Up | Celebratory level-up overlay |

### Settings & Account Screens

| Screen | Purpose |
|--------|---------|
| Settings | Audio, accessibility, language preferences |
| Parent Dashboard | Weekly summary, difficulty settings, data management |
| Account | Profile info, child management, deletion |

---

## Key Components

### Race View Components

- **Race Track** — horizontal scrolling track with 8 obstacle markers.
- **Runner Sprites** — avatar portraits moving along the track.
- **Problem Card** — current arithmetic problem, large and centred.
- **Answer Input** — numeric keyboard or typed input.
- **Timer** — countdown timer per problem (speed tier feedback).
- **Position Indicator** — current race position (1st–5th).
- **Progress Bar** — shows distance to finish for each runner.

### Common UI Components

- **Avatar Card** — portrait thumbnail, name, race count.
- **XP Bar** — current XP progress toward next level.
- **Achievement Badge** — circular, collectible, status-aware.
- **Loading State** — spinner with friendly message; never blank.
- **Error State** — friendly message; never technical language.
- **Confirmation Dialog** — modal with Cancel and Confirm; focus trapped.
- **Notification Toast** — 3-second auto-dismiss; top-right position.

---

## Navigation Flow

```
Login / Register
        ↓
Child Profile Select
        ↓
    Home Menu
   ↙    ↓    ↘
Avatar  Mode   Statistics
Gallery Select
        ↓
  Race Lobby
        ↓
  Countdown
        ↓
   Race View
        ↓
 Race Results
        ↓
  Home Menu
```

---

## Accessibility Requirements

- All interactive elements reachable by keyboard (Tab / Enter / Space).
- No action requires more than one sequential key press.
- Focus order follows visual reading order.
- All images have alt text or are marked decorative.
- Timer countdowns have `aria-live` announcements.
- Problem cards use `role="main"` and `aria-label`.
- Reduced motion: disable all non-essential animations.

---

## Responsive Breakpoints

| Breakpoint | Target |
|------------|--------|
| ≥ 1280px | Desktop (primary) |
| 768–1279px | Tablet / laptop |
| 480–767px | Large mobile (secondary) |
| < 480px | Out of v1.0 scope |

---

## Child-Facing Error Messages

Children must never see technical error text. Examples:

| Situation | Child-Friendly Message |
|-----------|----------------------|
| Avatar generation failed | "Hmm, something went wobbly. Let's try again!" |
| Network error | "Looks like we lost the signal. Check your connection!" |
| Unknown error | "Oops! Our track needs a quick repair. Try again in a moment." |

---

## Acceptance Criteria

- [ ] Every screen in the inventory is implemented and reachable.
- [ ] Race View renders at ≥ 30 FPS on target hardware.
- [ ] All interactive elements have visible focus states.
- [ ] Child-friendly error messages are shown for all error states.
- [ ] Screen transition animations complete within 500ms.
- [ ] Parent Dashboard shows correct weekly summary data.
- [ ] Modal dialogs trap focus and dismiss on Escape.
