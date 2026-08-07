# Audio Design

**Level:** Specification
**Status:** Authoritative
**Source:** GDD Chapter 11
**Parent:** [Epic E6 — Engineering](technical-requirements.md)

---

## Audio Philosophy

> **Every sound should make the player smile.**

- Correct answers sound exciting.
- Mistakes sound amusing — never harsh.
- Silence is used intentionally to create anticipation.

---

## Audio Layers

Six independent layers, each independently configurable:

```
Music → Ambience → Character Voices → Gameplay Effects → UI Sounds → Celebration Effects
```

---

## Music

### Adaptive Progression

```
Main Menu (Relaxed Theme)
     ↓ Countdown
     ↓ Race (Energetic Theme)
     ↓ Final Sprint (High Energy)
     ↓ Victory (Celebration Theme)
```

Music transitions must be smooth (no abrupt track changes).

### Style Requirements

Uplifting, playful, orchestral, lightly electronic, melodic, memorable.

Inspired by: animated feature films, modern family games, sports festivals.

Avoid: aggressive rock, heavy electronic, dramatic tension, repetitive loops.

### Temporal key points

| Moment | Music Behaviour |
|--------|----------------|
| Menu | Warm, welcoming, relaxed theme |
| Countdown | Energy gradually increases; strong accent on "GO!" |
| Race | Medium tempo, rhythmic, optimistic; highly repeatable |
| Final sprint (obstacle 7–8) | Brighter, stronger percussion — tempo stable |
| Finish | Short triumphant phrase (< 3 seconds) |

---

## Crowd Ambience

Stadium crowd is continuously present with ambient: cheering, applause, whistles, laughter.

Dynamic crowd reactions:

| Event | Crowd Response |
|-------|----------------|
| Leader changes | Louder cheering |
| Correct answer | Supportive applause |
| Final sprint | Growing excitement |
| Finish | Large applause |

---

## Character Voices

Short expressive sounds, not spoken dialogue. Language-independent.

| Expression | Sound |
|------------|-------|
| Happy | "Yay!" |
| Thinking | "Hmm..." |
| Celebrating | "Woohoo!" |
| Surprised | "Oh!" |

Each species has a distinct pitch profile (e.g. fox = higher; bear = deep and warm).

---

## Gameplay Effects

| Event | Sound |
|-------|-------|
| Correct answer | Pleasant chime + sparkle |
| Incorrect answer | Soft bounce + gentle "oops" |
| Obstacle jump (correct) | Whoosh → landing |
| Obstacle hit (incorrect) | Boing → dust → laughter |

**Never use harsh buzzers for incorrect answers.**

---

## UI Sounds

| Interaction | Sound |
|-------------|-------|
| Button hover | Tiny pop |
| Button click | Soft click |
| Card selection | Paper flip |
| Window opening | Gentle swoosh |
| Window closing | Soft fade |
| Avatar selected | Friendly greeting |

---

## Celebration Effects

Achievement unlock sequence:

```
Sparkle → Ascending notes → Badge appears → Short fanfare
```

Duration: < 2 seconds total.

---

## Audio Priority

When simultaneous sounds conflict:

1. Mathematics feedback (highest)
2. Countdown
3. Character reactions
4. Victory
5. UI
6. Ambient (lowest)

Lower-priority sounds are automatically reduced during important moments.

---

## Performance Requirements

- Audio playback latency: < 50 ms from event to playback.
- All commonly used sounds preloaded before race starts.
- Audio engine handles automatic layer mixing (crowd reduces during key moments).

---

## Accessibility

Audio must **never** be required for gameplay.

Every sound cue has a visual equivalent:
- Correct answer: green flash + animation.
- Incorrect answer: colour change + character stumble animation.
- Achievement: badge animation + sparkle effect.

Children with hearing impairments receive identical gameplay information.

---

## Settings

Configurable per user (or parent):

- Master volume
- Music volume
- Sound effects volume
- Ambience volume
- Character voices volume

Settings persist automatically.

---

## Technical Notes

- Avoid `<audio>` element for gameplay sounds; use Web Audio API.
- Sound sprites recommended for low-latency UI effects.
- All sounds must be provided in WebM/Opus format with MP3 fallback.
- Total audio bundle size target: < 10 MB before lazy-loading additional packs.
