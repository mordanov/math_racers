// @vitest-environment node
import { describe, expect, it } from 'vitest';
import { OBSTACLE_COUNT } from '../../../src/engine/race/constants';
import { RaceStateError } from '../../../src/engine/race/stateMachine';
import { createRaceEngine } from '../../../src/engine/race/raceEngine';
import type { AiPersonality, RaceConfig } from '../../../src/engine/race/types';

const BASE_CONFIG: RaceConfig = {
  raceId: 'test-race-1',
  seed: 42,
  tier: 1,
  mode: 'quick',
  participants: [{ runnerId: 'player-1', isHuman: true, avatarId: 'avatar-1' }],
};

const MEDIUM_PERSONALITY: AiPersonality = {
  id: 'medium',
  name: 'Medium',
  baseResponseTimeMs: 3000,
  responseTimeVarianceMs: 500,
  accuracyRate: 0.8,
  speedProfile: 'uniform',
  tierOffset: 0,
};

function advanceToRacing(engine: ReturnType<typeof createRaceEngine>) {
  engine.transition('LOBBY');
  engine.transition('COUNTDOWN');
  engine.transition('RACING');
  // Seed the clock with a couple of ticks so obstacle clock is running
  engine.tick(0);
  engine.tick(16);
}

describe('Race Engine — full race loop (human only)', () => {
  it('follows the legal state sequence IDLE → LOBBY → COUNTDOWN → RACING', () => {
    const engine = createRaceEngine(BASE_CONFIG);
    expect(engine.getState().state).toBe('IDLE');
    engine.transition('LOBBY');
    expect(engine.getState().state).toBe('LOBBY');
    engine.transition('COUNTDOWN');
    expect(engine.getState().state).toBe('COUNTDOWN');
    engine.transition('RACING');
    expect(engine.getState().state).toBe('RACING');
  });

  it('applies Perfect tier (18 m) for a fast correct answer', () => {
    const engine = createRaceEngine(BASE_CONFIG);
    advanceToRacing(engine);
    // Obstacle clock is 16ms after two ticks — well under 2000ms threshold
    const result = engine.submitAnswer({ isCorrect: true });
    expect(result.tier).toBe('perfect');
    expect(result.distanceMetres).toBe(18);
  });

  it('applies Slow tier (9 m) for a slow correct answer', () => {
    const engine = createRaceEngine(BASE_CONFIG);
    engine.transition('LOBBY');
    engine.transition('COUNTDOWN');
    engine.transition('RACING');
    engine.tick(0);
    // Advance clock past 6000ms threshold
    for (let t = 16; t <= 6016; t += 16) engine.tick(t);
    const result = engine.submitAnswer({ isCorrect: true });
    expect(result.tier).toBe('slow');
    expect(result.distanceMetres).toBe(9);
  });

  it('applies 0 m for incorrect answer', () => {
    const engine = createRaceEngine(BASE_CONFIG);
    advanceToRacing(engine);
    const result = engine.submitAnswer({ isCorrect: false });
    expect(result.distanceMetres).toBe(0);
    expect(result.tier).toBe('incorrect');
  });

  it('total distance never decreases', () => {
    const engine = createRaceEngine(BASE_CONFIG);
    advanceToRacing(engine);
    let prev = 0;
    for (let i = 0; i < OBSTACLE_COUNT; i++) {
      engine.tick(i * 16);
      engine.submitAnswer({ isCorrect: i % 2 === 0 }); // alternate correct / incorrect
      const dist = engine.getState().runners[0].totalDistanceMetres;
      expect(dist).toBeGreaterThanOrEqual(prev);
      prev = dist;
    }
  });

  it('completes exactly 8 obstacles and transitions to RESULTS', () => {
    const engine = createRaceEngine(BASE_CONFIG);
    advanceToRacing(engine);
    for (let i = 0; i < OBSTACLE_COUNT; i++) {
      engine.tick(i * 16);
      engine.submitAnswer({ isCorrect: true });
    }
    expect(engine.getState().state).toBe('RESULTS');
    expect(engine.getState().runners[0].obstaclesCompleted).toBe(OBSTACLE_COUNT);
  });

  it('getSummary() returns correct summary after RESULTS', () => {
    const engine = createRaceEngine(BASE_CONFIG);
    advanceToRacing(engine);
    for (let i = 0; i < OBSTACLE_COUNT; i++) {
      engine.tick(i * 16);
      engine.submitAnswer({ isCorrect: true });
    }
    const summary = engine.getSummary();
    expect(summary.race_id).toBe('test-race-1');
    expect(summary.difficulty_tier).toBe(1);
    expect(summary.mode).toBe('quick');
    expect(summary.participants).toHaveLength(1);
    expect(summary.participants[0].problems_correct).toBe(OBSTACLE_COUNT);
    expect(summary.participants[0].total_distance).toBe(OBSTACLE_COUNT * 18); // all Perfect
    expect(summary.participants[0].position).toBe(1);
  });

  it('getSummary() throws if not in RESULTS state', () => {
    const engine = createRaceEngine(BASE_CONFIG);
    expect(() => engine.getSummary()).toThrow();
  });
});

describe('Race Engine — AI determinism', () => {
  const AI_CONFIG: RaceConfig = {
    raceId: 'test-race-ai',
    seed: 77,
    tier: 2,
    mode: 'quick',
    participants: [
      { runnerId: 'player-1', isHuman: true, avatarId: 'avatar-1' },
      {
        runnerId: 'ai-0',
        isHuman: false,
        avatarId: 'ai',
        personality: MEDIUM_PERSONALITY,
      },
    ],
  };

  function runFullRace(cfg: RaceConfig) {
    const engine = createRaceEngine(cfg);
    engine.transition('LOBBY');
    engine.transition('COUNTDOWN');
    engine.transition('RACING');
    engine.tick(0);
    for (let i = 0; i < OBSTACLE_COUNT; i++) {
      engine.tick(i * 16 + 16);
      engine.submitAnswer({ isCorrect: true });
    }
    return engine.getState().runners;
  }

  it('same seed produces identical AI runner distances across two replays', () => {
    const runA = runFullRace(AI_CONFIG);
    const runB = runFullRace(AI_CONFIG);
    runA.forEach((runner, idx) => {
      expect(runner.totalDistanceMetres).toBe(runB[idx].totalDistanceMetres);
      runner.obstacleResults.forEach((r, oIdx) => {
        expect(r.isCorrect).toBe(runB[idx].obstacleResults[oIdx].isCorrect);
      });
    });
  });
});

describe('Race Engine — per-opponent RNG independence', () => {
  it('3 AI opponents of the same personality produce at least one diverging checkpoint', () => {
    const cfg: RaceConfig = {
      raceId: 'test-multi-ai',
      seed: 99,
      tier: 3,
      mode: 'quick',
      participants: [
        { runnerId: 'player', isHuman: true, avatarId: 'avatar-0' },
        { runnerId: 'ai-1', isHuman: false, avatarId: 'ai-1', personality: MEDIUM_PERSONALITY },
        { runnerId: 'ai-2', isHuman: false, avatarId: 'ai-2', personality: MEDIUM_PERSONALITY },
        { runnerId: 'ai-3', isHuman: false, avatarId: 'ai-3', personality: MEDIUM_PERSONALITY },
      ],
    };
    const engine = createRaceEngine(cfg);
    engine.transition('LOBBY');
    engine.transition('COUNTDOWN');
    engine.transition('RACING');
    engine.tick(0);
    for (let i = 0; i < OBSTACLE_COUNT; i++) {
      engine.tick(i * 16 + 16);
      engine.submitAnswer({ isCorrect: true });
    }
    const runners = engine.getState().runners.filter((r) => !r.isHuman);
    // At least one obstacle where not all 3 AI runners produced identical distance
    let foundDivergence = false;
    for (let obs = 0; obs < OBSTACLE_COUNT; obs++) {
      const dists = runners.map((r) => r.obstacleResults[obs].distanceMetres);
      if (new Set(dists).size > 1) {
        foundDivergence = true;
        break;
      }
    }
    expect(foundDivergence).toBe(true);
  });
});

describe('Race Engine — zero AI opponents', () => {
  it('completes without error and returns 1-participant summary', () => {
    const cfg: RaceConfig = {
      raceId: 'training-race',
      seed: 1,
      tier: 2,
      mode: 'training',
      participants: [{ runnerId: 'player', isHuman: true, avatarId: 'avatar-0' }],
    };
    const engine = createRaceEngine(cfg);
    engine.transition('LOBBY');
    engine.transition('COUNTDOWN');
    engine.transition('RACING');
    engine.tick(0);
    for (let i = 0; i < OBSTACLE_COUNT; i++) {
      engine.tick(i * 16 + 16);
      engine.submitAnswer({ isCorrect: true });
    }
    expect(engine.getState().state).toBe('RESULTS');
    const summary = engine.getSummary();
    expect(summary.participants).toHaveLength(1);
  });
});

describe('Race Engine — tiebreaker determinism', () => {
  it('getSummary tiebreaker is stable across two identical replays', () => {
    // Two AI runners with same seed will have same distance — tiebreaker must be stable
    const cfg: RaceConfig = {
      raceId: 'tie-race',
      seed: 5,
      tier: 1,
      mode: 'quick',
      participants: [
        { runnerId: 'player', isHuman: true, avatarId: 'a0' },
        {
          runnerId: 'ai-beta',
          isHuman: false,
          avatarId: 'a1',
          personality: { ...MEDIUM_PERSONALITY, accuracyRate: 0.0 }, // always zero distance
        },
        {
          runnerId: 'ai-alpha',
          isHuman: false,
          avatarId: 'a2',
          personality: { ...MEDIUM_PERSONALITY, accuracyRate: 0.0 }, // always zero distance
        },
      ],
    };
    function runAndGetPositions() {
      const engine = createRaceEngine(cfg);
      engine.transition('LOBBY');
      engine.transition('COUNTDOWN');
      engine.transition('RACING');
      engine.tick(0);
      for (let i = 0; i < OBSTACLE_COUNT; i++) {
        engine.tick(i * 16 + 16);
        engine.submitAnswer({ isCorrect: true });
      }
      return engine.getSummary().participants.map((p) => p.avatar_id);
    }
    const run1 = runAndGetPositions();
    const run2 = runAndGetPositions();
    expect(run1).toEqual(run2);
  });
});

describe('Race Engine — state guard', () => {
  it('rejects submitAnswer when not in RACING state', () => {
    const engine = createRaceEngine(BASE_CONFIG);
    expect(() => engine.submitAnswer({ isCorrect: true })).toThrow(RaceStateError);
    engine.transition('LOBBY');
    expect(() => engine.submitAnswer({ isCorrect: true })).toThrow(RaceStateError);
  });

  it('rejects illegal transition IDLE → RACING from engine', () => {
    const engine = createRaceEngine(BASE_CONFIG);
    expect(() => engine.transition('RACING')).toThrow(RaceStateError);
    expect(engine.getState().state).toBe('IDLE');
  });

  it('rejects illegal transition RESULTS → RACING from engine', () => {
    const engine = createRaceEngine(BASE_CONFIG);
    advanceToRacing(engine);
    for (let i = 0; i < OBSTACLE_COUNT; i++) {
      engine.tick(i * 16);
      engine.submitAnswer({ isCorrect: true });
    }
    expect(engine.getState().state).toBe('RESULTS');
    expect(() => engine.transition('RACING')).toThrow(RaceStateError);
    expect(engine.getState().state).toBe('RESULTS');
  });
});
