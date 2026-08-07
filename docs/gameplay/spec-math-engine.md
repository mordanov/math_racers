# Mathematics Engine — Implementation Specification

**Level:** Specification
**Status:** Authoritative
**Source:** FR-030–034; feature-math-engine.md; ADR-002; ADR-004; Game Economy §Difficulty
**Parent:** [Epic E1 — Gameplay](epic.md)
**See also:** [feature-math-engine.md](feature-math-engine.md), [feature-adaptive-difficulty.md](../economy/feature-adaptive-difficulty.md)

---

## Data Models

### Problem

```json
{
  "id": "uuid",
  "operation": "addition | subtraction | multiplication | division",
  "operand_a": 7,
  "operand_b": 3,
  "answer": 10,
  "tier": 2,
  "seed": 1234567890
}
```

`answer` is always an integer. Division problems are generated only when `operand_a` is exactly divisible by `operand_b`.

### ProblemSet

```json
{
  "seed": 1234567890,
  "tier": 2,
  "count": 8,
  "problems": ["...Problem[]"]
}
```

---

## Difficulty Tiers

| Tier | Operations | Operand Range | Notes |
|------|-----------|---------------|-------|
| 1 | Addition only | 1–10 | Intro level |
| 2 | Addition, Subtraction | 1–20 | No negative results |
| 3 | Addition, Subtraction, Multiplication | 1–12 | ×1–×12 tables |
| 4 | All four operations | 1–25 | Division: exact divisors only |
| 5 | All four operations | 1–100 | Mixed sets |
| 6 | All four operations | Custom per parent setting | Teacher/parent-configured |

---

## Generation Algorithm

The mathematics engine executes entirely in the browser (ADR-004). No network call occurs during generation.

```
function generateProblemSet(tier, seed, count):
  rng = seededRandom(seed)
  problems = []
  lastProblem = null

  while len(problems) < count:
    operation = pickOperation(tier, rng)
    (a, b) = pickOperands(operation, tier, rng)
    answer = compute(operation, a, b)
    candidate = Problem(operation, a, b, answer, tier, seed)

    if isDuplicate(candidate, lastProblem):
      continue          # regenerate; never two identical consecutive problems

    problems.append(candidate)
    lastProblem = candidate

  return ProblemSet(seed, tier, count, problems)
```

**Determinism guarantee:** identical `(tier, seed, count)` always produces identical output.

### Division safety

```
function pickOperands(division, tier, rng):
  b = randomInt(rng, 2, maxOperand(tier))
  a = b * randomInt(rng, 1, maxOperand(tier) // b)
  return (a, b)
```

Division by zero is structurally impossible.

### Duplicate prevention

Two consecutive problems are duplicates if `operation`, `operand_a`, and `operand_b` are all identical. A single retry per slot is sufficient because the operand space is always larger than 1.

---

## Tier Selection

Called once before race setup; not called during an active race (FR-043).

```
function selectTier(skillScore, parentOverride):
  if parentOverride is set:
    return clamp(parentOverride, 1, 6)

  if skillScore >= 0.90:
    return min(currentTier + 1, 6)
  elif skillScore < 0.60:
    return max(currentTier - 1, 1)
  else:
    return currentTier
```

---

## Answer Validation

Validation is client-side and synchronous (FR-033).

```
function validateAnswer(problem, playerInput):
  parsed = parseInt(playerInput.trim())
  if isNaN(parsed):
    return { correct: false, reason: "not_a_number" }
  return { correct: parsed === problem.answer }
```

Response time is measured from problem render to `validateAnswer` call. Timing categories map directly to movement tiers (see `feature-race-engine.md`).

---

## API Endpoint

The backend exposes a reference generator for seed verification and parent-configured Tier 6 settings. It is **not** called during active gameplay.

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/v1/problems?tier=N&seed=X&count=N` | Generate a reference problem set |
| `GET` | `/api/v1/players/{id}/difficulty` | Return current adaptive tier + parent override |
| `PATCH` | `/api/v1/players/{id}/difficulty` | Set parent difficulty override |

---

## Edge Cases

1. **Tier 6 with no parent configuration** — fall back to Tier 5 behaviour; do not error.
2. **Seed produces the same problem twice in a row** — retry loop regenerates; maximum 10 retries per slot before accepting the duplicate (prevents infinite loop on extremely constrained tiers).
3. **Operand overflow for large tier ranges** — clamp operands to the tier's documented max; do not panic.
4. **`parseInt` on non-numeric input** — return `correct: false`; never throw.
5. **`count` of 0** — return empty `ProblemSet`; valid for training mode preview.
6. **Tier boundary violation via parent override** — clamp silently to [1, 6]; reject values outside range with HTTP 422.
7. **Concurrent races with same seed** — each race session holds its own `ProblemSet` instance; no shared mutable state.

---

## Manual Verification Steps

1. Open Training Mode. Select Tier 1. Start a session. Confirm all 8 problems are addition-only with operands in [1, 10].
2. In the same session, confirm no two consecutive problems are identical.
3. Start a second Training session with the same seed. Confirm all 8 problems are identical to step 1.
4. Change the seed. Confirm the problem set changes.
5. Select Tier 4. Confirm division problems appear and that every division answer is a whole number.
6. Submit a correct answer. Confirm the UI registers it as correct immediately (< 100 ms perceived delay).
7. Submit an incorrect answer. Confirm the UI registers it as incorrect and that the runner does not advance.
8. Open Parent Settings. Set Tier 6 with a custom operand range. Start a race. Confirm problems respect the custom range.

---

## Acceptance Criteria

- [ ] Identical `(tier, seed, count)` always produces identical problem sequence.
- [ ] No two consecutive problems in a set are identical.
- [ ] Division problems always have integer answers.
- [ ] Division by zero never occurs.
- [ ] Tier 1 contains only addition; Tier 4+ includes all four operations.
- [ ] Answer validation completes in < 1 ms.
- [ ] Tier is never changed during an active race.
- [ ] Parent override is respected and clamped to [1, 6].
