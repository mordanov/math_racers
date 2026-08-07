# Epic E2 — Avatar System

**Level:** Epic
**Status:** Authoritative
**Source:** GDD Chapters 4, 13
**Parent:** [PRD](../prd.md)

---

## Summary

Deliver the complete avatar system: child-driven character creation, AI-assisted metadata generation, GPT Image portrait generation, and the full avatar lifecycle including versioning and history.

---

## Features

| Feature | Description | Link |
|---------|-------------|------|
| F2.1 — Avatar Creation | Input form, LLM description, biography, name generation | [feature-avatar-creation.md](feature-avatar-creation.md) |
| F2.2 — Avatar Lifecycle | Favourite, rename, regenerate, history, max limit | [feature-avatar-lifecycle.md](feature-avatar-lifecycle.md) |

---

## Design Constraints

- Children design avatars; they do not buy them.
- Previous portrait versions are never deleted — only superseded.
- AI generation is asynchronous; the child sees a loading state.
- The avatar gallery holds up to 50 avatars per child profile.
- The game's visual language (Art Bible + Prompt Bible) governs all generated imagery.

---

## Acceptance Criteria

- [ ] Child selects species, colours, and accessories; system generates a complete character.
- [ ] LLM produces a name, biography, and structured metadata.
- [ ] Portrait generation completes within 30 seconds under normal conditions.
- [ ] Regenerating a portrait creates a new version without deleting the old one.
- [ ] The favourite avatar is persistent across sessions.
- [ ] All 50 avatar slots are accessible in the gallery.
