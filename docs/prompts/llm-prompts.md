# LLM Prompts

**Level:** Specification
**Status:** Authoritative — do not modify prompts without incrementing Prompt Version
**Source:** prompt_bible.md Part II
**See also:** [gpt-image-prompts.md](gpt-image-prompts.md)

---

## Purpose

LLM prompts generate **structured educational content** — character metadata, biographies, names, achievements, tips, and messages. The LLM never generates gameplay mechanics or business logic.

---

## Core Principles

- Produce structured output (JSON where possible).
- Deterministic when given the same inputs.
- Minimise hallucinations.
- Never return Markdown unless explicitly requested.
- Return JSON only when JSON is requested.

---

## System Prompt (applied to every LLM request)

```text
You are the content generation engine for Math Racers, a premium educational racing game for children aged 7–12.

Your responsibilities are limited to generating safe, child-friendly content.

Always be positive, encouraging and imaginative.

Never generate copyrighted characters, existing franchises, political content, religious content, violence, horror, mature themes or offensive material.

When requested, return valid JSON that strictly follows the provided schema.

If information is missing, make reasonable assumptions rather than asking questions.

Never explain your reasoning.
```

---

## Avatar Generation

### Input

```yaml
species: fox
hair: short curly
skin: light
eyes: green
accessories: blue headband
animal_similarity: fox
```

### User Prompt

```text
Create a unique child-friendly racing avatar.

Return JSON only.

Schema:
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

### Biography Requirements

- 2–3 sentences maximum.
- Optimistic, age-appropriate, humorous.
- Inspires curiosity, avoids clichés.
- Does not mention winning.

---

## Avatar Name Generation

```text
Generate five original first names suitable for a friendly animated racing character.

Requirements:
- easy to pronounce;
- suitable for children;
- international;
- not strongly associated with existing fictional characters.

Return JSON array only.
```

---

## Personality Generation

```text
Describe the character's personality using exactly five adjectives.

Return JSON array.
```

Example output:
```json
["curious", "kind", "creative", "determined", "cheerful"]
```

---

## Image Description Generator

Generates the appearance summary used by the Prompt Builder:

```text
Describe this avatar visually using one concise paragraph.

Only mention appearance.

Do not mention emotions, personality or background.

Return plain text.
```

---

## Achievement Name Generator

```text
Generate ten achievement names for a children's mathematics racing game.

Requirements:
- short;
- positive;
- memorable;
- maximum three words.

Return JSON array.
```

---

## Achievement Description

```text
Write a one-sentence description for the following achievement.

Tone: encouraging

Maximum: 20 words
```

---

## Championship Name Generator

```text
Generate names for friendly racing championships.

Examples: Forest Sprint, Rainbow Cup, Sunny Stadium League

Return JSON array.
```

---

## Encouragement Messages

```text
Generate fifty encouraging messages shown after answering incorrectly.

Requirements:
- supportive;
- optimistic;
- short;
- never shame the player.

Maximum eight words.

Return JSON array.
```

Example output:
```json
[
  "Great effort! Try again!",
  "You're getting closer!",
  "Keep thinking!",
  "Nice attempt!",
  "You've got this!"
]
```

---

## Victory Messages

```text
Generate thirty celebration messages.

Maximum six words.

Positive. Energetic.

Return JSON array.
```

---

## Loading Tips

```text
Generate thirty short educational tips for children.

Maximum 12 words.

Topics: mathematics, learning, sports, friendship, curiosity.

Return JSON array.
```

---

## Safety Rules

Every LLM prompt enforces:
- Child-safe language
- Positive tone
- No stereotypes
- No bullying references
- No politics or religion
- No violence or horror
- No inappropriate humour

When uncertain, prefer a simpler response.

---

## JSON Rules

When JSON is requested:
- Return JSON only
- No Markdown code fences
- No explanations
- No trailing commas
- UTF-8 characters allowed
- Must validate without modification

---

## Temperature Guidelines

| Task | Creativity |
|------|-----------|
| Avatar metadata | Low |
| Biography | Medium |
| Names | Medium |
| Achievements | Medium |
| Loading tips | Low |
| Localisation | Very Low |
| Story mode (future) | Medium–High |
| Educational hints (future) | Low |

Consistency is preferred over novelty.

---

## Prompt Versioning

Every prompt records:
- Prompt Version
- Prompt Template
- Model
- Request ID
- Timestamp

Version increments on every template change.
