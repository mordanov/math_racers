# UI Style Guide

**Level:** Specification
**Status:** Authoritative
**Source:** art_bible.md Part III
**See also:** [visual-language.md](visual-language.md), [../ui/screens.md](../ui/screens.md)

---

## Design System Principle

The UI extends the game's visual language into every interactive surface. Buttons, cards, and overlays should feel like premium game interfaces — not generic web forms.

---

## Spacing System

Base unit: **8px**

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon padding, micro gaps |
| sm | 8px | Component internal padding |
| md | 16px | Section padding |
| lg | 24px | Card padding |
| xl | 32px | Screen padding |
| 2xl | 48px | Section separation |

---

## Corner Radii

| Element Type | Radius |
|-------------|--------|
| Small icons / chips | 8px |
| Buttons / inputs | 16px |
| Cards / panels | 24px |
| Overlays / modals | 32px |

All interactive elements use rounded corners. Sharp corners are forbidden.

---

## Animation Timing

| Type | Duration | Use |
|------|----------|-----|
| Micro | 100ms | Button hover, icon pulse |
| Quick | 150ms | State transitions, focus rings |
| Standard | 250ms | Component transitions, tooltips |
| Expressive | 350–500ms | Page transitions, reveals, celebrations |

Easing: `ease-out` for entrances, `ease-in` for exits, `ease-in-out` for transforms.

Respect `prefers-reduced-motion` — replace motion with instant transitions.

---

## Button States

| State | Visual Treatment |
|-------|-----------------|
| Default | Full colour, slight shadow |
| Hover | Lighter shade, slight scale-up (102%), faster shadow |
| Active/Pressed | Darker shade, scale-down (98%), shadow removed |
| Disabled | 40% opacity, cursor not-allowed |
| Focus | Visible focus ring (3px, offset 2px) |
| Loading | Spinner overlay, pointer-events disabled |

---

## Typography

- All text is legible at 100% zoom on a 1024px-wide screen.
- Minimum body text: 16px.
- Heading hierarchy: H1 ≥ 32px, H2 ≥ 24px, H3 ≥ 20px.
- Line height: 1.5 for body, 1.2 for headings.
- Font must feel rounded, friendly, and readable for children.

---

## Colour Semantics in UI

| Semantic | Colour | Usage |
|----------|--------|-------|
| Primary action | Sky Blue | Main CTA buttons |
| Success | Bright Green | Correct answer, completion |
| Warning / Incorrect | Warm Orange | Wrong answer feedback |
| Destructive | Warm Red | Delete, danger |
| Neutral | Light Cream / Warm Grey | Background, dividers |
| Interactive | Blue Glow | Selected, focused |

---

## Cards

- White or light-cream background.
- 24px corner radius.
- Subtle shadow: `0 4px 16px rgba(0,0,0,0.08)`.
- Content padding: 24px.
- Hover: slight elevation increase.

---

## Overlays / Modals

- Semi-transparent backdrop: `rgba(0,0,0,0.4)`.
- Modal: white background, 32px radius, 32px padding.
- Dismiss button visible in top-right corner.
- Trap focus within modal while open.

---

## Icons

- 24px base size (scalable to 16px and 32px).
- Rounded style, consistent stroke weight.
- Follow primary palette.
- Paired with text labels except in well-established conventions (✕ close, ✓ confirm).

---

## Progress Bars

- Height: 12px.
- Fully rounded ends.
- Fill colour: Golden Yellow or Sky Blue.
- Background: Light Cream.
- Animate fill on value change (250ms ease-out).

---

## Accessibility Requirements

- All interactive elements have visible focus states.
- Minimum colour contrast ratio: 4.5:1 for text, 3:1 for UI components.
- Touch targets minimum 44×44px.
- Never convey information through colour alone.
- All images have meaningful `alt` text or `aria-hidden` if decorative.

---

## Forbidden UI Patterns

- Cold grey (#808080-style) backgrounds
- Hard-edged buttons or cards
- Flashing or strobing animations
- Sounds that cannot be disabled
- Modal dialogs that cannot be dismissed
- Forms with no visible labels
- Error messages in technical language
