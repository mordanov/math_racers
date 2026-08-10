# Contract: AI Simulation Engine (Frontend)

**Feature**: 005-ai-opponents
**Status**: Authoritative

---

## simulateAiObstacle

Updated signature (checkpoint-aware):

```typescript
function simulateAiObstacle(
  personality: AiPersonality,
  checkpointIndex: number,   // 0-based, range [0, 7]
  rng: () => number,
): AiObstacleResult
```

**Parameters**:

| Param | Type | Constraints |
|-------|------|-------------|
| `personality` | AiPersonality | must include `speedProfile`, `tierOffset` |
| `checkpointIndex` | number | integer, `[0, 7]` |
| `rng` | () => number | returns uniform `[0, 1)` — must be a seeded RNG, not `Math.random()` |

**Returns**:

```typescript
interface AiObstacleResult {
  isCorrect: boolean;
  responseTimeMs: number;  // ≥ 0
}
```

**Behaviour**:

1. `accuracyRoll = rng()` — `isCorrect = accuracyRoll < personality.accuracyRate` (after applying variability offset clamped to [0, 1]).
2. If `!isCorrect` → `responseTimeMs` is still computed (used for state, but `calculateMovement` will return distance 0).
3. `baseTime` = `sampleResponseTime(personality.speedProfile, checkpointIndex, rng)` — see algorithm below.
4. `speedMult` = `speedMultiplier(personality.speedProfile, checkpointIndex, rng)` — see algorithm below.
5. Final `responseTimeMs = max(0, baseTime)` (no further Gaussian noise step — the response time sampling replaces the old Gaussian model).

**sampleResponseTime algorithm**:

```
function sampleResponseTime(profile, checkpointIndex, rng):
  // checkpointIndex is 0-based; t = checkpointIndex / 7 normalises to [0, 1]
  t = checkpointIndex / 7
  if profile == "front_loaded":  base = lerp(1500, 5000, t)
  if profile == "back_loaded":   base = lerp(5000, 1500, t)
  if profile == "random":        base = rng() * 6000 + 1000   // uniform [1000, 7000]ms
  else (uniform):                base = 3500
  return base + (rng() - 0.5) * 1000   // ±500ms noise
```

**speedMultiplier algorithm**:

```
function speedMultiplier(profile, checkpointIndex, rng):
  if profile == "front_loaded":
    if checkpointIndex < 3: return 1.2
    if checkpointIndex < 6: return 1.0
    return 0.9
  if profile == "back_loaded":
    if checkpointIndex < 3: return 0.85
    if checkpointIndex < 6: return 1.0
    return 1.25
  if profile == "random":
    return 0.7 + rng() * 0.6   // uniform [0.7, 1.3]
  return 1.0   // uniform
```

Note: `speedMultiplier` is applied to `responseTimeMs` — a lower multiplier means a faster response, which maps to a higher `base_distance` tier via the existing `calculateMovement` thresholds.

**Determinism guarantee**: For the same `personality`, `checkpointIndex`, and `rng` initialised with the same seed, `simulateAiObstacle` MUST return identical results across all invocations.

---

## RaceEngine: per-opponent RNG

Updated seeding in `createRaceEngine`:

```typescript
// Before (single shared RNG):
const aiRng = createRng(config.seed + 1);

// After (per-opponent, index-offset):
// rng for AI participant at index i (0-based in participants array):
const aiRngs = config.participants.map((p, i) =>
  p.isHuman ? null : createRng(config.seed + i + 1)
);
```

- `i = 0` (first participant) → `createRng(seed + 1)` (same as before for a single-opponent race)
- Human participant slots produce `null` and are skipped.
- This guarantees per-opponent independence while preserving backward compatibility for single-AI races.

---

## AiPersonality (extended type)

```typescript
export interface AiPersonality {
  id: string;
  name: string;
  accuracyRate: number;             // [0.0, 1.0]
  baseResponseTimeMs: number;       // retained for test fixture compatibility
  responseTimeVarianceMs: number;   // retained for test fixture compatibility
  speedProfile: 'uniform' | 'front_loaded' | 'back_loaded' | 'random';
  tierOffset: number;               // applied by caller; not used inside simulateAiObstacle
}
```

`baseResponseTimeMs` and `responseTimeVarianceMs` are retained for backward compatibility with existing tests that construct `AiPersonality` inline, but the new `simulateAiObstacle` implementation uses `sampleResponseTime` (driven by `speedProfile` and `checkpointIndex`) instead of the old Gaussian noise model.

---

## Tiebreaking (getSummary)

When two or more runners share identical `totalDistanceMetres` at race end:

```
// Before (insertion order):
return runners.indexOf(a) - runners.indexOf(b);

// After (runnerId lexicographic):
return a.runnerId < b.runnerId ? -1 : 1;
```

This ensures identical `(seed, personalities, playerTier)` always produces identical position rankings.
