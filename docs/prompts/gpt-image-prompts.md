# GPT Image Prompts

**Level:** Specification
**Status:** Authoritative — do not modify prompts without incrementing Prompt Version
**Source:** prompt_bible.md Part I
**See also:** [../ai/asset-pipeline.md](../ai/asset-pipeline.md), [../art/image-generation-standards.md](../art/image-generation-standards.md)

---

## Core Principle

> **Never write prompts manually. Always generate them from structured metadata.**

The Prompt Builder constructs all production prompts. No hard-coded prompts are permitted in application code.

---

## Global Prompt Prefix

Every image prompt starts with this foundation. Never omit or modify without incrementing Prompt Version.

```text
A premium stylized 3D animated illustration for a modern children's educational game. Warm, cheerful, colorful, rounded shapes, expressive character design, feature-film quality, soft global illumination, vibrant harmonious colors, family-friendly, highly readable, polished, timeless visual style, original artwork, not based on any existing franchise.
```

---

## Global Negative Prompt

Appended to every request:

```text
No text, no letters, no numbers, no logos, no watermark, no signature, no frame, no border, no extra characters, no cropped body, no weapons, no violence, no horror, no realistic anatomy, no photorealism, no anime, no comic book style, no low-quality rendering, no blur.
```

---

## Template Variables

| Variable | Description |
|----------|-------------|
| `{{species}}` | Animal species (e.g. fox, rabbit, bear) |
| `{{appearance}}` | One-line appearance summary from LLM |
| `{{hair}}` | Hair description |
| `{{eyes}}` | Eye colour and style |
| `{{skin}}` | Fur or skin colour |
| `{{accessories}}` | Accessories list |
| `{{clothes}}` | Sports outfit description |
| `{{personality}}` | One-word personality trait |
| `{{pose}}` | Pose description (overridden per template) |
| `{{expression}}` | Facial expression (overridden per template) |
| `{{background}}` | Background description (usually "Transparent") |

---

## Character Prompt Template

```text
{{GLOBAL_PREFIX}}

Create exactly one full-body character.

Species:
{{species}}

Appearance:
{{appearance}}

Hair:
{{hair}}

Eyes:
{{eyes}}

Skin/Fur:
{{skin}}

Accessories:
{{accessories}}

Sports Outfit:
{{clothes}}

Personality:
{{personality}}

Pose:
Standing in a friendly running-ready pose.

Facial expression:
Happy, curious and confident.

Camera:
Three-quarter front view.

Background:
Transparent.

{{GLOBAL_NEGATIVE}}
```

---

## Character Portrait Template

For profile screens (head and shoulders only):

```text
{{GLOBAL_PREFIX}}

Create a portrait of the existing avatar.

Head and shoulders only.

Friendly smile.

Eye contact.

Soft warm lighting.

Simple gradient background.

Highly expressive eyes.

{{GLOBAL_NEGATIVE}}
```

---

## Victory Pose Template

```text
{{GLOBAL_PREFIX}}

Create exactly one character celebrating victory after finishing a race.

Jumping happily.

Raised hands.

Big smile.

Confetti lighting reflections.

Transparent background.

{{GLOBAL_NEGATIVE}}
```

---

## Thinking Pose Template

Used while solving mathematics:

```text
{{GLOBAL_PREFIX}}

Character is thinking carefully.

One hand on chin.

Friendly curious expression.

Transparent background.

{{GLOBAL_NEGATIVE}}
```

---

## Stadium Background Template

```text
{{GLOBAL_PREFIX}}

Create a colorful athletics stadium for children.

Running track.

Green grass.

Rounded trees.

Blue sky.

Colorful banners.

Happy atmosphere.

No people.

Wide composition.

Highly detailed but visually calm.

No text.
```

---

## Main Menu Illustration Template

```text
{{GLOBAL_PREFIX}}

A joyful children's athletics festival.

Several unique runners warming up.

Large colorful stadium.

Bright morning light.

Soft clouds.

Friendly atmosphere.

Highly cinematic composition.

No text.
```

---

## Loading Screen Template

```text
{{GLOBAL_PREFIX}}

Children practicing mathematics before a fun race.

Playful environment.

Joyful atmosphere.

Lots of movement.

Warm sunlight.

Landscape composition.

No text.
```

---

## Trophy Template

```text
{{GLOBAL_PREFIX}}

Large playful golden trophy.

Rounded shapes.

Colorful enamel decorations.

Premium polished finish.

Transparent background.

No text.
```

---

## Medal Template

```text
{{GLOBAL_PREFIX}}

Premium enamel sports medal for children.

Gold rim.

Bright colors.

Ribbon.

Transparent background.

No text.
```

---

## Achievement Badge Template

```text
{{GLOBAL_PREFIX}}

Create a collectible achievement badge.

Rounded enamel pin.

Premium quality.

Bright colors.

Transparent background.

No text.
```

---

## Icon Template

```text
{{GLOBAL_PREFIX}}

Create a simple game icon.

Rounded.

Slightly three-dimensional.

Bright colors.

Transparent background.

No text.
```

---

## Button Illustration Template

```text
{{GLOBAL_PREFIX}}

Create a glossy rounded game button.

Bright colors.

Soft shadows.

Transparent background.

No text.
```

---

## Seasonal Asset Rule

Seasonal prompts modify only:
- Colours
- Vegetation
- Decorations
- Weather effects

Everything else (character proportions, style, quality requirements) remains identical.

---

## Prompt Builder Rules

The Prompt Builder MUST:
- ✅ Always use the Global Prefix
- ✅ Always append the Global Negative Prompt
- ✅ Always generate deterministic prompts (same inputs → same output)
- ✅ Never allow free-form prompt editing from the frontend

The Prompt Builder MUST NOT:
- ❌ Hard-code prompts in application code
- ❌ Construct prompts inside controllers or view layers
- ❌ Send raw user input to the generation API

---

## Prompt Versioning

Every generated prompt records:

| Field | Value |
|-------|-------|
| `prompt_version` | Template version string (e.g. `1.0.0`) |
| `prompt_template` | Full prompt text as sent |
| `model_version` | GPT Image model identifier |
| `generation_date` | ISO 8601 timestamp |
| `seed` | If supported by the model |

Changing any template text requires incrementing `prompt_version`.
