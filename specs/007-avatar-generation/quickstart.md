# Quickstart: Avatar Generation

**Feature**: 007-avatar-generation
**Date**: 2026-08-10
**Purpose**: Integration scenarios for manual and automated end-to-end testing.

Prerequisites: authenticated account session cookie; backend + worker running; Redis available; GPT API key configured.

---

## Scenario 1 — Happy Path: Create and Poll

**Goal**: A child creates an avatar with all fields and sees a published portrait.

```
1. POST /api/v1/avatars
   Body: { species: "fox", fur_color: "#FF8C00", eye_color: "#228B22",
           hairstyle: "curly", accessories: ["headband"],
           clothes_top_color: "#4169E1", clothes_bottom_color: "#FFFFFF" }
   Expect: 201 → { avatar_id, job_id, status: "pending" }

2. Poll GET /api/v1/avatars/{avatar_id}/jobs/{job_id} every 2 s
   Expect: status transitions through queued → llm_running → generating → validating → storing → complete
   (within 30 s on a normal connection)

3. GET /api/v1/avatars/{avatar_id}
   Expect: 200 → name non-null, biography non-null, portrait.full_url non-null,
           portrait.prompt_version non-null, portrait.model_version non-null,
           status: "published"
```

**Verification**: Avatar appears in gallery; portrait thumbnail renders; all four URL variants (full/medium/small/thumb) are accessible.

---

## Scenario 2 — Minimal Creation (defaults)

**Goal**: Only `species` provided; all other fields receive defaults.

```
1. POST /api/v1/avatars
   Body: { species: "rabbit" }
   Expect: 201 → { avatar_id, job_id }

2. Poll until complete (same as Scenario 1)

3. GET /api/v1/avatars/{avatar_id}
   Expect: 200 → status: "published"; name, biography non-null;
           fur_color, eye_color, clothes_top_color, clothes_bottom_color all set to defaults
```

---

## Scenario 3 — Regenerate Portrait

**Goal**: A child regenerates their avatar portrait; old portrait remains accessible.

```
1. Complete Scenario 1 (avatar_id = A, portrait_id = P1)

2. POST /api/v1/avatars/{avatar_id}/regenerate
   Expect: 201 → { avatar_id, job_id: J2, status: "queued" }

3. Poll GET /api/v1/avatars/{avatar_id}/jobs/{J2} until complete

4. GET /api/v1/avatars/{avatar_id}
   Expect: active_portrait_id ≠ P1 (new portrait is active)
           portrait_history contains both P1 and the new portrait
           name and biography unchanged
```

**Verification**: Both portrait versions are accessible via their respective URLs.

---

## Scenario 4 — Ownership Guard

**Goal**: Account B cannot access Account A's avatar.

```
1. Account A: POST /api/v1/avatars → avatar_id = X

2. Account B: GET /api/v1/avatars/{X}
   Expect: 403 or 404 (avatar not visible to another account)

3. Account B: DELETE /api/v1/avatars/{X}
   Expect: 403 or 404
```

---

## Scenario 5 — Avatar Limit (50)

**Goal**: The 51st avatar creation is rejected.

```
1. Create 50 avatars (can use test fixture to insert directly to DB)

2. POST /api/v1/avatars with any valid body
   Expect: 422 → { error_code: "AVATAR_LIMIT_REACHED" }
```

---

## Scenario 6 — Concurrency Limit (2 in-progress)

**Goal**: A 3rd simultaneous generation is rejected while 2 are in-progress.

```
1. POST /api/v1/avatars → job J1 (do not wait for completion)
2. POST /api/v1/avatars → job J2 (do not wait)
3. POST /api/v1/avatars
   Expect: 429 → { error_code: "CONCURRENCY_LIMIT_REACHED" }
```

Note: For automated tests, mock the worker or pause it so jobs stay in `queued` state.

---

## Scenario 7 — Rename and Set Favourite

**Goal**: A child renames their avatar and marks it as favourite.

```
1. Complete Scenario 1 (avatar_id = A)

2. PATCH /api/v1/avatars/{A}
   Body: { name: "Zara Fox", is_favourite: true }
   Expect: 200 → name: "Zara Fox", is_favourite: true

3. GET /api/v1/avatars/{A}
   Expect: name: "Zara Fox", is_favourite: true
```

---

## Scenario 8 — Delete Avatar

**Goal**: Deleting an avatar removes it from the gallery.

```
1. Complete Scenario 1 (avatar_id = A)

2. DELETE /api/v1/avatars/{A}
   Expect: 204

3. GET /api/v1/avatars/{A}
   Expect: 404 → { error_code: "AVATAR_NOT_FOUND" }

4. GET /api/v1/avatars
   Expect: avatar A absent from list
```

---

## Scenario 9 — Browser Close During Generation (persistence)

**Goal**: Closing the browser mid-generation does not lose the portrait.

```
1. POST /api/v1/avatars → job J1 (generation starts)
2. Do NOT poll — simulate browser close
3. Wait 35 s (generation should complete in worker)
4. New session: GET /api/v1/avatars/{avatar_id}
   Expect: status: "published"; portrait available
```

---

## Scenario 10 — Invalid Input Rejection

**Goal**: Malformed hex colours are rejected before generation is attempted.

```
1. POST /api/v1/avatars
   Body: { species: "fox", fur_color: "orange" }
   Expect: 422 → validation error for fur_color

2. POST /api/v1/avatars
   Body: { species: "dragon" }
   Expect: 422 → validation error for species (not in allowed list)
```
