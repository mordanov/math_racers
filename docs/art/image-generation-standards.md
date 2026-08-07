# Image Generation Standards

**Level:** Specification
**Status:** Authoritative
**Source:** art_bible.md Part IV
**See also:** [../prompts/gpt-image-prompts.md](../prompts/gpt-image-prompts.md), [../ai/asset-pipeline.md](../ai/asset-pipeline.md)

---

## Purpose

Define the technical and artistic standards that every AI-generated image must meet before being published in the game.

---

## Technical Specifications

| Property | Required Value |
|----------|---------------|
| Format | PNG |
| Size | 1024×1024 pixels |
| Aspect ratio | 1:1 |
| Background | Transparent (alpha channel) |
| Colour space | sRGB |
| Maximum file size | 5 MB |

---

## Quality Gates

### Technical Gate

| Check | Pass Condition |
|-------|---------------|
| API response | HTTP 200 |
| Dimensions | Exactly 1024×1024 |
| Format | PNG with alpha |
| File size | < 5 MB |
| Background | Transparent detected |
| No cropping | Full character body visible |

### Artistic Gate

| Check | Pass Condition |
|-------|---------------|
| Single character | Exactly one character visible |
| No text | No letters, numbers, logos, watermarks |
| No borders | No frame or edge artefact |
| Expression | Character appears friendly/positive |
| Proportions | Large head, expressive face, readable silhouette |
| Colours | Bright, vibrant, consistent with metadata |

### Content Safety Gate

| Forbidden Content | Action on Detection |
|-------------------|---------------------|
| Violence, weapons | Reject + regenerate |
| Frightening imagery | Reject + regenerate |
| Offensive symbols | Reject + log + escalate |
| Inappropriate clothing | Reject + regenerate |
| Political/religious messaging | Reject + log + escalate |
| Realistic injury | Reject + regenerate |

---

## Regeneration Policy

| Failure Type | Automatic Action |
|-------------|-----------------|
| Technical gate failure | Retry (same prompt) |
| Artistic gate failure | Retry (simplified prompt) |
| Content safety failure | Retry (stricter negative prompt) |
| 3 consecutive failures | Log, notify user, offer manual retry |

The child never sees a technical error. They see a friendly message: "Something went a bit sideways — let's try again!"

---

## Visual Consistency Requirements

Every character asset must:

- Match the species, colours, and accessories described in the character metadata.
- Use the same proportions (40% head, 25% torso, 35% legs).
- Display a friendly expression aligned with the requested pose.
- Appear consistent with other assets for the same avatar.

**Character identity across versions:** Regenerating a portrait must produce a recognisably similar character. If species, colours, and accessories match, identity is preserved even with creative variation in pose or shading.

---

## Human Review (Roadmap)

- **v1.0:** Automated validation only.
- **v1.5:** Optional parental approval before avatars become visible to others.
- **v2.0:** Moderation queue for flagged content.

---

## Production Pipeline (Art Bible Reference)

```
Character Metadata
      ↓
Prompt Builder (deterministic)
      ↓
GPT Image API
      ↓
Technical Validation
      ↓
Artistic Validation
      ↓
Human Review (future)
      ↓
Asset Library (published)
```

All stages are logged. Every published asset has an auditable creation record.

---

## Thumbnail Standards

| Variant | Size | Format |
|---------|------|--------|
| Full | 1024×1024 | PNG |
| Medium | 512×512 | PNG |
| Small | 256×256 | PNG |
| Thumb | 128×128 | PNG |

Thumbnails are generated automatically after each successful publish. They share the same quality gate as the full-size image.

---

## Prompt Quality Standard

Prompt complexity should remain **moderate**. Long prompts do not necessarily produce better images. Every sentence in a prompt must add meaningful artistic information.

Prompt engineering is treated as software engineering, not ad-hoc experimentation.
