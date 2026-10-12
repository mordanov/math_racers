import { describe, expect, it } from 'vitest';
import { generateProblemSet } from './generator';
import { TIER_CONFIGS } from './tiers';
import type { TierConfig } from './types';

describe('difficulty tier operation sets', () => {
  it('uses multiplication in Tier 3 and division in Tier 4', () => {
    expect(TIER_CONFIGS[3].operations).toEqual(['multiplication']);
    expect(TIER_CONFIGS[4].operations).toEqual(['division']);
  });

  it('requires custom settings for Tier 6', () => {
    expect(() => generateProblemSet(6, 42, 1)).toThrow(/parent-configured/);
  });

  it('uses mental-arithmetic operand widths in tiers 3 through 5', () => {
    for (const tier of [3, 4, 5] as const) {
      const problems = generateProblemSet(tier, 9102, 1000).problems;
      for (const problem of problems) {
        if (problem.operation === 'addition' && tier === 5) {
          expect(problem.operand_a).toBeGreaterThanOrEqual(10);
          expect(problem.operand_b).toBeGreaterThanOrEqual(10);
          expect(problem.operand_a).toBeLessThan(100);
          expect(problem.operand_b).toBeLessThan(100);
        }
        if (problem.operation === 'multiplication') {
          expect(problem.operand_a).toBeGreaterThanOrEqual(10);
          expect(problem.operand_a).toBeLessThan(100);
          expect(problem.operand_b).toBeGreaterThanOrEqual(1);
          expect(problem.operand_b).toBeLessThan(10);
        }
        if (problem.operation === 'division') {
          expect(problem.operand_b).toBeGreaterThanOrEqual(2);
          expect(problem.operand_b).toBeLessThan(10);
          expect(problem.answer).toBeGreaterThan(1);
          expect(problem.operand_a % problem.operand_b).toBe(0);
        }
      }
    }
  });

  it('never generates self-division in standard and custom division tiers', () => {
    const standard = generateProblemSet(5, 19, 10_000).problems;
    const custom = generateProblemSet(6, 20, 10_000, {
      tier: 6,
      operations: ['division'],
      minOperand: 2,
      maxOperand: 30,
    }).problems;

    for (const problem of [...standard, ...custom]) {
      if (problem.operation === 'division') {
        expect(problem.answer).toBeGreaterThan(1);
        expect(problem.operand_a).not.toBe(problem.operand_b);
      }
    }
  });

  it('rejects custom division settings that cannot produce a quotient above one', () => {
    expect(() =>
      generateProblemSet(6, 42, 1, {
        tier: 6,
        operations: ['division'],
        minOperand: 2,
        maxOperand: 3,
      }),
    ).toThrow(/division/i);
  });

  it('matches the seeded generator vectors shared with the backend', () => {
    const config: TierConfig = {
      tier: 6,
      operations: ['division'],
      minOperand: 2,
      maxOperand: 30,
    };
    const expected = {
      3: [
        ['multiplication', 37, 5],
        ['multiplication', 55, 4],
        ['multiplication', 78, 9],
        ['multiplication', 51, 9],
        ['multiplication', 97, 6],
        ['multiplication', 52, 3],
        ['multiplication', 87, 6],
        ['multiplication', 80, 6],
      ],
      4: [
        ['division', 16, 4],
        ['division', 18, 6],
        ['division', 24, 8],
        ['division', 25, 5],
        ['division', 18, 9],
        ['division', 15, 5],
        ['division', 24, 8],
        ['division', 10, 2],
      ],
      5: [
        ['division', 52, 4],
        ['division', 42, 6],
        ['addition', 78, 99],
        ['division', 95, 5],
        ['division', 72, 9],
        ['addition', 52, 37],
        ['division', 72, 8],
        ['subtraction', 8, 3],
      ],
      6: [
        ['division', 18, 6],
        ['division', 18, 9],
        ['division', 24, 12],
        ['division', 24, 8],
        ['division', 30, 15],
        ['division', 16, 8],
        ['division', 28, 14],
        ['division', 26, 13],
      ],
    };

    for (const tier of [3, 4, 5, 6] as const) {
      const problems = generateProblemSet(tier, 12345, 8, tier === 6 ? config : undefined).problems;
      expect(
        problems.map(({ operation, operand_a, operand_b }) => [operation, operand_a, operand_b]),
      ).toEqual(expected[tier]);
    }
  });
});
