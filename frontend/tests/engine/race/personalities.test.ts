// @vitest-environment node
import { describe, expect, it } from 'vitest';
import { createRng } from '../../../src/engine/math/rng';
import { simulateAiObstacle } from '../../../src/engine/race/aiRunner';
import { PERSONALITIES, SPEEDSTER, SLOW_STARTER, STEADY, UNPREDICTABLE } from '../../../src/engine/race/personalities';

describe('PERSONALITIES constants', () => {
  it('contains exactly 5 entries', () => {
    expect(PERSONALITIES).toHaveLength(5);
  });

  it('all ids are unique', () => {
    const ids = PERSONALITIES.map((p) => p.id);
    expect(new Set(ids).size).toBe(5);
  });

  it('all names are non-empty', () => {
    for (const p of PERSONALITIES) {
      expect(p.name.length).toBeGreaterThan(0);
    }
  });

  it('speedProfile values are correct per personality', () => {
    expect(SPEEDSTER.speedProfile).toBe('front_loaded');
    expect(SLOW_STARTER.speedProfile).toBe('back_loaded');
    expect(UNPREDICTABLE.speedProfile).toBe('random');
    expect(STEADY.speedProfile).toBe('uniform');
  });
});

describe('Personality behaviour arcs', () => {
  function avgResponseTime(personality: typeof SPEEDSTER, checkpoints: number[]): number {
    let total = 0;
    for (let seed = 0; seed < 20; seed++) {
      for (const ci of checkpoints) {
        const rng = createRng(seed * 100 + ci);
        const result = simulateAiObstacle(personality, ci, rng);
        total += result.responseTimeMs;
      }
    }
    return total / (20 * checkpoints.length);
  }

  it('Speedster has lower avg responseTimeMs early (0-2) than late (5-7)', () => {
    const early = avgResponseTime(SPEEDSTER, [0, 1, 2]);
    const late = avgResponseTime(SPEEDSTER, [5, 6, 7]);
    expect(early).toBeLessThan(late);
  });

  it('Slow Starter has lower avg responseTimeMs late (5-7) than early (0-2)', () => {
    const early = avgResponseTime(SLOW_STARTER, [0, 1, 2]);
    const late = avgResponseTime(SLOW_STARTER, [5, 6, 7]);
    expect(late).toBeLessThan(early);
  });
});
