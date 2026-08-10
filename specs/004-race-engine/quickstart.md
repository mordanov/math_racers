# Quickstart — Race Engine

**Branch**: `004-race-engine` | **Date**: 2026-08-10

This guide shows a developer how to wire up the race engine from scratch.

---

## 1. Initialise a race

```typescript
import { createRaceEngine } from '@/engine/race';
import { generateProblemSet } from '@/engine/math';

const config: RaceConfig = {
  raceId: crypto.randomUUID(),
  seed: 42,
  tier: 3,
  mode: 'quick',
  participants: [
    { runnerId: 'player-uuid', isHuman: true, avatarId: 'avatar-uuid' },
    { runnerId: 'ai-0', isHuman: false, avatarId: 'ai', personality: AI_PERSONALITY_MEDIUM },
  ],
};

const engine = createRaceEngine(config);
```

---

## 2. Advance through states

```typescript
engine.transition('LOBBY');      // IDLE → LOBBY
engine.transition('COUNTDOWN');  // LOBBY → COUNTDOWN
engine.transition('RACING');     // COUNTDOWN → RACING (starts clock)
```

Illegal transitions throw a `RaceStateError`.

---

## 3. Submit a player answer

```typescript
// Called when the player submits; engine reads obstacleClockMs internally
const result = engine.submitAnswer({ isCorrect: true });
// result: { tier: 'perfect', distanceMetres: 18 }
```

---

## 4. Drive the clock via requestAnimationFrame

```typescript
function gameLoop(timestamp: number) {
  engine.tick(timestamp);         // advances clockMs and obstacleClockMs
  renderFrame(engine.getState()); // read derived state for rendering
  requestAnimationFrame(gameLoop);
}
requestAnimationFrame(gameLoop);
```

---

## 5. React hook usage

```typescript
const { state, runners, currentObstacle, submitAnswer } = useRaceEngine(config);
```

The hook calls `engine.tick()` internally via `useAnimationFrame`.

---

## 6. Persist summary on completion

When `state === 'RESULTS'`, call:

```typescript
const summary = engine.getSummary(); // RaceSummary
await postRaceSummary(summary);      // POST /api/v1/races/
```

---

## 7. Running tests

```bash
cd frontend
pnpm test --reporter=verbose src/engine/race
```

All engine logic is pure TypeScript — no React renderer required for unit tests.

---

## Key Constants

| Constant | Value | Location |
|----------|-------|----------|
| `OBSTACLE_COUNT` | 8 | `engine/race/constants.ts` |
| `MAX_TRACK_DISTANCE` | 144 | `engine/race/constants.ts` |
| `PERFECT_THRESHOLD_MS` | 2000 | `engine/race/movement.ts` |
| `EXCELLENT_THRESHOLD_MS` | 4000 | `engine/race/movement.ts` |
| `GOOD_THRESHOLD_MS` | 6000 | `engine/race/movement.ts` |
| `FRAME_DELTA_CAP_MS` | 100 | `engine/race/clock.ts` |
