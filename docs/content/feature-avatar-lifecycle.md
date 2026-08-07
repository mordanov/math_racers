# Feature F2.2 — Avatar Lifecycle

**Level:** Feature
**Status:** Authoritative
**Source:** GDD Chapter 4; GDD Chapter 10 §5
**Parent:** [Epic E2 — Avatar System](epic.md)

---

## Purpose

Avatars are long-lived companions with their own history. The lifecycle system ensures every avatar can be personalised, regenerated, and retired without losing its story.

---

## Avatar Gallery

- Maximum **50 avatars** per child profile.
- Gallery shows all avatars with name, portrait thumbnail, and race count.
- One avatar is always designated as the **favourite**.

---

## Favourite Avatar

- The child selects one avatar as their favourite at any time.
- The favourite avatar is used in race lobbies and profile screens by default.
- Every favourite change is recorded in the avatar history timeline.

---

## Rename

- The child may rename any avatar at any time.
- Renaming does not affect biography, personality, or statistics.

---

## Avatar History

Each avatar maintains an independent history:

| Field | Description |
|-------|-------------|
| Created | Creation date |
| Races | Total races with this avatar |
| Victories | Total first-place finishes |
| Favourite Since | Date the avatar was last selected as favourite |
| Best Championship Finish | Best championship placement |

History makes every avatar feel like it has a story.

---

## Portrait Versioning

When the child regenerates a portrait:

```
Version 1 → Version 2 → Version 3
```

- The previous portrait is **never deleted**.
- The child can select any version as the active portrait.
- Each version stores: prompt version, model version, generation date.

---

## Deletion

The child (or parent) may permanently delete an avatar:

- All versions of the portrait are deleted.
- Race history attributable to this avatar is anonymised, not deleted (statistics totals preserved).
- The avatar slot becomes available for a new character.

---

## Read Biographies

Reading an avatar's biography contributes to the "Read every biography" collection achievement.

---

## Acceptance Criteria

- [ ] Gallery loads all 50 avatars without performance degradation.
- [ ] Favouriting an avatar persists across sessions and devices.
- [ ] Rename is saved immediately with no page reload.
- [ ] Regenerating a portrait creates a new version; the previous is accessible.
- [ ] Deletion removes the avatar from the gallery and frees the slot.
- [ ] Avatar history increments race count after every completed race.
- [ ] Favourite timeline records every favourite-change with a timestamp.
