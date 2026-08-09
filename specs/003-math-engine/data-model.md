# Data Model: Mathematics Engine

**Phase**: 1 — Design  
**Branch**: `003-math-engine`  
**Date**: 2026-08-09

---

## Overview

The mathematics engine is a **stateless, pure computation module**. It has no persistent entities and writes nothing to the database. All data lives in memory for the duration of a race session.

The backend reference endpoint (`GET /api/v1/problems`) also produces in-memory output only; it persists nothing.

---

## Frontend TypeScript Types

### `Operation`

```typescript
type Operation = 'addition' | 'subtraction' | 'multiplication' | 'division';
```

### `Problem`

```typescript
interface Problem {
  id: string;           // UUID v4, generated at creation time
  operation: Operation;
  operand_a: number;    // integer; for subtraction: always >= operand_b
  operand_b: number;    // integer; for division: always a divisor of operand_a; never 0
  answer: number;       // integer; always exact
  tier: Tier;
  seed: number;         // 32-bit unsigned integer seed used to generate this problem
}
```

### `ProblemSet`

```typescript
interface ProblemSet {
  seed: number;         // 32-bit unsigned integer
  tier: Tier;
  count: number;        // 0 <= count <= 100
  problems: Problem[];  // length === count; immutable once generated
}
```

### `Tier`

```typescript
type Tier = 1 | 2 | 3 | 4 | 5 | 6;
```

### `TierConfig`

Describes the allowed operations and operand range for each tier. Tier 6 config is fetched from the backend before race setup; tiers 1–5 are static constants.

```typescript
interface TierConfig {
  tier: Tier;
  operations: Operation[];
  minOperand: number;   // inclusive lower bound for operands
  maxOperand: number;   // inclusive upper bound for operands (multiplication: capped at 12 for Tier 3)
}
```

Static configs (tiers 1–5):

| Tier | Operations | minOperand | maxOperand | Notes |
|------|-----------|-----------|-----------|-------|
| 1 | addition | 1 | 10 | |
| 2 | addition, subtraction | 1 | 20 | subtraction: operand_a ≥ operand_b |
| 3 | addition, subtraction, multiplication | 1 | 12 | ×1–×12 tables |
| 4 | all four | 1 | 25 | division: exact divisors only |
| 5 | all four | 1 | 100 | |
| 6 | parent-configured | custom | custom | falls back to Tier 5 if unconfigured |

### `ValidationResult`

```typescript
interface ValidationResult {
  correct: boolean;
  reason?: 'not_a_number';   // present only when input is non-numeric
  elapsedMs: number;          // time from problem render to validateAnswer call, in milliseconds
}
```

### `TierSelectionInput`

```typescript
interface TierSelectionInput {
  currentTier: Tier;
  skillScore: number;       // float in [0, 1]
  parentOverride?: number;  // raw value before clamping; optional
}
```

---

## Backend Python Types

The backend reference generator mirrors the frontend types. Python dataclasses are used (no ORM, no DB).

```python
from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID

class Operation(StrEnum):
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"

@dataclass(frozen=True)
class Problem:
    id: UUID
    operation: Operation
    operand_a: int
    operand_b: int
    answer: int
    tier: int        # 1–6
    seed: int        # 32-bit unsigned int

@dataclass(frozen=True)
class ProblemSet:
    seed: int
    tier: int
    count: int
    problems: tuple[Problem, ...]  # immutable
```

---

## State Transitions

The engine is stateless; there are no state machines. The only lifecycle note:

1. `ProblemSet` is created once before a race begins.
2. It is consumed sequentially during the race (one `Problem` per question prompt).
3. It is discarded when the race ends.
4. Tier selection is called once before `ProblemSet` creation; it is never called during a race.

---

## Invariants

These invariants must hold for every `Problem` instance, enforced at generation time:

1. `operand_b != 0` (all operations).
2. `operation == 'division'` → `operand_a % operand_b == 0`.
3. `operation == 'subtraction'` → `operand_a >= operand_b` (result ≥ 0).
4. `operand_a >= tierConfig.minOperand` and `operand_a <= tierConfig.maxOperand`.
5. `operand_b >= tierConfig.minOperand` and `operand_b <= tierConfig.maxOperand`.
6. `answer == compute(operation, operand_a, operand_b)` (integer arithmetic).
7. No two consecutive `Problem` instances in a `ProblemSet` share `(operation, operand_a, operand_b)` (after retry; duplicate accepted after 10 retries).
