// @vitest-environment node
import { describe, expect, it } from 'vitest';
import { createRng } from '../../../src/engine/math/rng';
import { simulateAiObstacle } from '../../../src/engine/race/aiRunner';
import type { AiPersonality } from '../../../src/engine/race/types';

const MEDIUM: AiPersonality = {
  id: 'medium',
  baseResponseTimeMs: 3000,
  responseTimeVarianceMs: 500,
  accuracyRate: 0.8,
};

describe('simulateAiObstacle — determinism', () => {
  it('produces identical results with the same seed across 10 calls', () => {
    const results = Array.from({ length: 10 }, () => {
      const rng = createRng(99);
      return simulateAiObstacle(MEDIUM, rng);
    });
    results.forEach((r) => {
      expect(r.isCorrect).toBe(results[0].isCorrect);
      expect(r.responseTimeMs).toBeCloseTo(results[0].responseTimeMs, 5);
    });
  });
});

describe('simulateAiObstacle — constraints', () => {
  it('response time is always non-negative', () => {
    for (let seed = 0; seed < 100; seed++) {
      const rng = createRng(seed);
      const result = simulateAiObstacle(MEDIUM, rng);
      expect(result.responseTimeMs).toBeGreaterThanOrEqual(0);
    }
  });

  it('accuracyRate=1.0 always returns isCorrect=true', () => {
    const always: AiPersonality = { ...MEDIUM, accuracyRate: 1.0 };
    for (let seed = 0; seed < 50; seed++) {
      const rng = createRng(seed);
      expect(simulateAiObstacle(always, rng).isCorrect).toBe(true);
    }
  });

  it('accuracyRate=0.0 always returns isCorrect=false', () => {
    const never: AiPersonality = { ...MEDIUM, accuracyRate: 0.0 };
    for (let seed = 0; seed < 50; seed++) {
      const rng = createRng(seed);
      expect(simulateAiObstacle(never, rng).isCorrect).toBe(false);
    }
  });
});

describe('simulateAiObstacle — distribution sanity', () => {
  it('produces a mix of correct/incorrect at 0.5 accuracy over many seeds', () => {
    const half: AiPersonality = { ...MEDIUM, accuracyRate: 0.5 };
    let correct = 0;
    for (let seed = 0; seed < 1000; seed++) {
      const rng = createRng(seed);
      if (simulateAiObstacle(half, rng).isCorrect) correct++;
    }
    // Should be roughly 50% — allow 40%–60% band
    expect(correct).toBeGreaterThan(400);
    expect(correct).toBeLessThan(600);
  });
});
