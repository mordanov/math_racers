# Feature F2.1 — Avatar Creation

**Level:** Feature
**Status:** Authoritative
**Source:** GDD Chapters 4, 13 §7–11; prompt_bible.md Part II
**Parent:** [Epic E2 — Avatar System](epic.md)

---

## Purpose

The avatar creation experience transforms a child's imagination into a unique AI-generated racing character. Children are creators, not consumers.

---

## Creation Flow

```
Child Input → LLM Character Description → LLM Biography & Names
     → Prompt Builder → GPT Image Generation → Quality Validation
     → Reveal Animation → Avatar Ready
```

---

## Child Input Form

The child provides creative choices through a simple, visual form:

| Field | Options |
|-------|---------|
| Animal species | Fox, Rabbit, Bear, Cat, Mouse, Panda, and more |
| Fur / skin colour | Colour picker (themed palette) |
| Eye colour | Colour picker |
| Hairstyle | Visual selector (short, long, curly, braided, etc.) |
| Accessories | Multi-select (headband, glasses, hat, scarf, etc.) |
| Clothing colours | Colour pickers for top and shorts |

All fields are optional. The system fills unspecified fields with creative defaults.

---

## LLM Step 1 — Character Metadata

The backend sends the child's choices to the LLM using the Avatar Generation prompt from the Prompt Bible.

Output schema:

```json
{
  "name": "...",
  "personality": "...",
  "biography": "...",
  "appearance_summary": "...",
  "species": "...",
  "favorite_color": "...",
  "favorite_subject": "...",
  "running_style": "..."
}
```

The LLM also generates 5 name suggestions. The child may choose one or type a custom name.

---

## LLM Step 2 — Biography

A short biography (max 50 words) is generated following the Avatar Biography prompt:

- Positive and encouraging
- Age-appropriate and humorous
- Focused on curiosity and learning, not winning
- Avoids clichés

---

## Prompt Builder

The Prompt Builder constructs the GPT Image prompt deterministically from the character metadata. It:

- Always applies the Global Prompt Prefix.
- Always appends the Global Negative Prompt.
- Substitutes template variables from the metadata.
- Produces a versioned prompt record.

The Prompt Builder is the only permitted path to a generation prompt. No free-form prompt editing from the frontend.

---

## GPT Image Generation

Request parameters:

- Model: GPT Image (current production version)
- Size: 1024×1024
- Aspect ratio: 1:1
- Background: transparent
- Quality: high

Generation is asynchronous. The child sees a progress animation while waiting.

---

## Quality Validation

Automated checks after generation:

- [ ] Image successfully generated (no API error)
- [ ] Transparent background present
- [ ] Correct dimensions (1024×1024)
- [ ] Single character visible
- [ ] No cropped body parts
- [ ] No visible text or watermark

Failed validation triggers automatic retry (up to 3 attempts with alternative prompt parameters). If all retries fail, the child is shown a friendly error and offered to try again.

---

## Reveal Animation

On success, the avatar is revealed with a celebration animation:

```
Sparkle Effect → Portrait Fades In → Character Name Appears → Confetti → Biography Card
```

---

## Acceptance Criteria

- [ ] All child input fields are functional and accessible (keyboard + pointer).
- [ ] LLM returns valid JSON matching the schema on every request.
- [ ] Prompt Builder produces a deterministic output given the same metadata.
- [ ] Generation completes within 30 seconds under normal conditions.
- [ ] Validation rejects images with visible text or cropped characters.
- [ ] Retry fires automatically on validation failure.
- [ ] Reveal animation plays before the avatar card is shown.
