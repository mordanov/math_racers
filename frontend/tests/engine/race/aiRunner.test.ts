// @vitest-environment node
import { describe, expect, it } from 'vitest';
import { createRng } from '../../../src/engine/math/rng';
import { simulateAiObstacle } from '../../../src/engine/race/aiRunner';
import type { AiPersonality } from '../../../src/engine/race/types';

const MEDIUM: AiPersonality = {
  id: 'medium',
  name: 'Medium',
  baseResponseTimeMs: 3000,
  responseTimeVarianceMs: 500,
  accuracyRate: 0.8,
  speedProfile: 'uniform',
  tierOffset: 0,
};

const SPEEDSTER_P: AiPersonality = {
  id: 'speedster',
  name: 'Speedster',
  baseResponseTimeMs: 3500,
  responseTimeVarianceMs: 350,
  accuracyRate: 0.70,
  speedProfile: 'front_loaded',
  tierOffset: 1,
};

const SLOW_STARTER_P: AiPersonality = {
  id: 'slow_starter',
  name: 'Slow Starter',
  baseResponseTimeMs: 3500,
  responseTimeVarianceMs: 280,
  accuracyRate: 0.75,
  speedProfile: 'back_loaded',
  tierOffset: 0,
};

describe('simulateAiObstacle — determinism', () => {
  it('produces identical results with the same seed across 10 calls', () => {
    const results = Array.from({ length: 10 }, () => {
      const rng = createRng(99);
      return simulateAiObstacle(MEDIUM, 0, rng);
    });
    results.forEach((r) => {
      expect(r.isCorrect).toBe(results[0].isCorrect);
      expect(r.responseTimeMs).toBeCloseTo(results[0].responseTimeMs, 5);
    });
  });

  it('same seed + same checkpointIndex produces identical result', () => {
    for (let ci = 0; ci < 8; ci++) {
      const rngA = createRng(42);
      const rngB = createRng(42);
      const a = simulateAiObstacle(MEDIUM, ci, rngA);
      const b = simulateAiObstacle(MEDIUM, ci, rngB);
      expect(a.isCorrect).toBe(b.isCorrect);
      expect(a.responseTimeMs).toBeCloseTo(b.responseTimeMs, 5);
    }
  });
});

describe('simulateAiObstacle — constraints', () => {
  it('response time is always non-negative', () => {
    for (let seed = 0; seed < 100; seed++) {
      const rng = createRng(seed);
      const result = simulateAiObstacle(MEDIUM, seed % 8, rng);
      expect(result.responseTimeMs).toBeGreaterThanOrEqual(0);
    }
  });

  it('accuracyRate=1.0 always returns isCorrect=true regardless of checkpointIndex', () => {
    const always: AiPersonality = { ...MEDIUM, accuracyRate: 1.0 };
    for (let ci = 0; ci < 8; ci++) {
      for (let seed = 0; seed < 10; seed++) {
        const rng = createRng(seed);
        expect(simulateAiObstacle(always, ci, rng).isCorrect).toBe(true);
      }
    }
  });

  it('accuracyRate=0.0 always returns isCorrect=false regardless of checkpointIndex', () => {
    const never: AiPersonality = { ...MEDIUM, accuracyRate: 0.0 };
    for (let ci = 0; ci < 8; ci++) {
      for (let seed = 0; seed < 10; seed++) {
        const rng = createRng(seed);
        expect(simulateAiObstacle(never, ci, rng).isCorrect).toBe(false);
      }
    }
  });
});

describe('simulateAiObstacle — distribution sanity', () => {
  it('produces a mix of correct/incorrect at 0.5 accuracy over many seeds', () => {
    const half: AiPersonality = { ...MEDIUM, accuracyRate: 0.5 };
    let correct = 0;
    for (let seed = 0; seed < 1000; seed++) {
      const rng = createRng(seed);
      if (simulateAiObstacle(half, 0, rng).isCorrect) correct++;
    }
    // Should be roughly 50% — allow 40%–60% band
    expect(correct).toBeGreaterThan(400);
    expect(correct).toBeLessThan(600);
  });
});

describe('simulateAiObstacle — speed profile arcs', () => {
  function avgTime(personality: AiPersonality, checkpointIndex: number, seeds = 50): number {
    let total = 0;
    for (let s = 0; s < seeds; s++) {
      total += simulateAiObstacle(personality, checkpointIndex, createRng(s)).responseTimeMs;
    }
    return total / seeds;
  }

  it('Speedster has lower avg responseTimeMs at checkpoint 0 than checkpoint 7 (front_loaded arc)', () => {
    expect(avgTime(SPEEDSTER_P, 0)).toBeLessThan(avgTime(SPEEDSTER_P, 7));
  });

  it('Slow Starter has lower avg responseTimeMs at checkpoint 7 than checkpoint 0 (back_loaded arc)', () => {
    expect(avgTime(SLOW_STARTER_P, 7)).toBeLessThan(avgTime(SLOW_STARTER_P, 0));
  });
});
