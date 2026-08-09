# Quickstart: Mathematics Engine

**Feature**: 003-math-engine  
**Date**: 2026-08-09

This document describes end-to-end integration scenarios for verifying the mathematics engine works correctly across the frontend and backend.

---

## Scenario 1: Determinism Verification (Frontend)

**Goal**: Confirm identical `(tier, seed, count)` always produces identical output.

```typescript
import { generateProblemSet } from '@/engine/math';

const setA = generateProblemSet(2, 1234567890, 8);
const setB = generateProblemSet(2, 1234567890, 8);

// All problems must be identical
setA.problems.forEach((p, i) => {
  console.assert(p.operation === setB.problems[i].operation);
  console.assert(p.operand_a === setB.problems[i].operand_a);
  console.assert(p.operand_b === setB.problems[i].operand_b);
  console.assert(p.answer === setB.problems[i].answer);
});
```

---

## Scenario 2: Tier Constraint Verification (Frontend)

**Goal**: Confirm Tier 1 produces only addition with operands in [1, 10].

```typescript
const set = generateProblemSet(1, 42, 50);

set.problems.forEach(p => {
  console.assert(p.operation === 'addition');
  console.assert(p.operand_a >= 1 && p.operand_a <= 10);
  console.assert(p.operand_b >= 1 && p.operand_b <= 10);
});
```

---

## Scenario 3: Division Safety (Frontend)

**Goal**: Confirm every division problem has an integer answer and no zero divisor.

```typescript
const set = generateProblemSet(4, 99, 100);
const divisions = set.problems.filter(p => p.operation === 'division');

divisions.forEach(p => {
  console.assert(p.operand_b !== 0, 'Division by zero');
  console.assert(Number.isInteger(p.answer), 'Non-integer answer');
  console.assert(p.operand_a % p.operand_b === 0, 'Not exactly divisible');
});
```

---

## Scenario 4: Answer Validation (Frontend)

**Goal**: Confirm validation returns correct results and never throws.

```typescript
import { validateAnswer } from '@/engine/math';

const problem = { operation: 'addition', operand_a: 7, operand_b: 3, answer: 10, /* ... */ };

const correct = validateAnswer(problem, '10');
console.assert(correct.correct === true);
console.assert(correct.elapsedMs >= 0);

const wrong = validateAnswer(problem, '9');
console.assert(wrong.correct === false);
console.assert(wrong.reason === undefined);

const nonNumeric = validateAnswer(problem, 'abc');
console.assert(nonNumeric.correct === false);
console.assert(nonNumeric.reason === 'not_a_number');
```

---

## Scenario 5: Frontend ↔ Backend Parity Check

**Goal**: Confirm the backend reference generator produces the same sequence as the frontend for the same seed.

1. Start the backend locally:
   ```bash
   docker compose up backend
   ```

2. Call the reference endpoint:
   ```bash
   curl "http://localhost:8000/api/v1/problems?tier=3&seed=777&count=5" | python3 -m json.tool
   ```

3. Run the frontend engine in a browser console or Vitest test with the same inputs and compare `operation`, `operand_a`, `operand_b`, `answer` for each problem at each index.

4. All five problems must match exactly.

---

## Scenario 6: Parent Override via API

**Goal**: Set a parent difficulty override and confirm the effective tier changes.

```bash
# Authenticate as a parent (token obtained via POST /api/v1/auth/login)
TOKEN="<jwt_token>"
PLAYER_ID="<player_uuid>"

# Set override to Tier 4
curl -X PATCH "http://localhost:8000/api/v1/players/$PLAYER_ID/difficulty" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"parent_override": 4}'

# Confirm effective_tier is 4 regardless of skill score
curl "http://localhost:8000/api/v1/players/$PLAYER_ID/difficulty" \
  -H "Authorization: Bearer $TOKEN"
# Expected: {"current_tier": <X>, "parent_override": 4, "effective_tier": 4}

# Clear override
curl -X PATCH "http://localhost:8000/api/v1/players/$PLAYER_ID/difficulty" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"parent_override": null}'
```

---

## Scenario 7: Out-of-Range Tier Rejection (API)

**Goal**: Confirm the backend rejects tier values outside [1, 6] with HTTP 422.

```bash
curl -w "\nHTTP %{http_code}\n" \
  "http://localhost:8000/api/v1/problems?tier=7&seed=1&count=5"
# Expected: HTTP 422

curl -w "\nHTTP %{http_code}\n" \
  "http://localhost:8000/api/v1/problems?tier=0&seed=1&count=5"
# Expected: HTTP 422
```

---

## Running Frontend Tests

```bash
cd frontend
pnpm test src/engine/math
```

All tests must pass with zero failures before the feature is considered done.

---

## Running Backend Tests

```bash
cd backend
pytest tests/unit/mathematics/ -v
pytest tests/integration/api/test_problems.py -v
```
