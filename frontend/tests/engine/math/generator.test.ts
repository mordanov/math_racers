// @vitest-environment node
import { describe, it, expect } from 'vitest';
import { generateProblemSet } from '../../../src/engine/math/generator';

describe('generateProblemSet — determinism', () => {
  it('produces identical output for identical (tier, seed, count)', () => {
    const a = generateProblemSet(2, 1234567890, 8);
    const b = generateProblemSet(2, 1234567890, 8);
    a.problems.forEach((p, i) => {
      expect(p.operation).toBe(b.problems[i].operation);
      expect(p.operand_a).toBe(b.problems[i].operand_a);
      expect(p.operand_b).toBe(b.problems[i].operand_b);
      expect(p.answer).toBe(b.problems[i].answer);
    });
  });

  it('produces different output for a different seed', () => {
    const a = generateProblemSet(2, 1234567890, 20);
    const b = generateProblemSet(2, 9999999999, 20);
    const allSame = a.problems.every(
      (p, i) =>
        p.operation === b.problems[i].operation &&
        p.operand_a === b.problems[i].operand_a &&
        p.operand_b === b.problems[i].operand_b,
    );
    expect(allSame).toBe(false);
  });

  it('returns empty ProblemSet when count is 0', () => {
    const set = generateProblemSet(1, 42, 0);
    expect(set.problems).toHaveLength(0);
    expect(set.count).toBe(0);
  });
});

describe('generateProblemSet — Tier 1 constraints', () => {
  it('produces only addition problems', () => {
    const set = generateProblemSet(1, 7, 100);
    set.problems.forEach(p => {
      expect(p.operation).toBe('addition');
    });
  });

  it('keeps operands in [1, 10]', () => {
    const set = generateProblemSet(1, 7, 100);
    set.problems.forEach(p => {
      expect(p.operand_a).toBeGreaterThanOrEqual(1);
      expect(p.operand_a).toBeLessThanOrEqual(10);
      expect(p.operand_b).toBeGreaterThanOrEqual(1);
      expect(p.operand_b).toBeLessThanOrEqual(10);
    });
  });
});

describe('generateProblemSet — division safety (Tier 4)', () => {
  it('all division answers are integers', () => {
    const set = generateProblemSet(4, 99, 200);
    const divisions = set.problems.filter(p => p.operation === 'division');
    expect(divisions.length).toBeGreaterThan(0);
    divisions.forEach(p => {
      expect(p.operand_b).not.toBe(0);
      expect(p.answer).toBe(Math.floor(p.answer));
      expect(p.operand_a % p.operand_b).toBe(0);
    });
  });
});

describe('generateProblemSet — subtraction result ≥ 0', () => {
  it('all subtraction results are non-negative', () => {
    const set = generateProblemSet(2, 55, 200);
    const subtractions = set.problems.filter(p => p.operation === 'subtraction');
    expect(subtractions.length).toBeGreaterThan(0);
    subtractions.forEach(p => {
      expect(p.operand_a).toBeGreaterThanOrEqual(p.operand_b);
      expect(p.answer).toBeGreaterThanOrEqual(0);
    });
  });
});

describe('generateProblemSet — duplicate prevention', () => {
  it('no two consecutive problems share (operation, operand_a, operand_b) in a large set', () => {
    const set = generateProblemSet(1, 12345, 200);
    for (let i = 1; i < set.problems.length; i++) {
      const prev = set.problems[i - 1];
      const curr = set.problems[i];
      const identical =
        curr.operation === prev.operation &&
        curr.operand_a === prev.operand_a &&
        curr.operand_b === prev.operand_b;
      expect(identical).toBe(false);
    }
  });
});

describe('generateProblemSet — Tier 6 fallback', () => {
  it('uses Tier 5 config when no customTierConfig provided', () => {
    const tier5 = generateProblemSet(5, 1, 50);
    const tier6 = generateProblemSet(6, 1, 50);
    tier6.problems.forEach(p => {
      expect(p.operand_a).toBeGreaterThanOrEqual(1);
      expect(p.operand_a).toBeLessThanOrEqual(100);
    });
    expect(tier6.tier).toBe(6);
  });
});

describe('generateProblemSet — Tier 4 includes all four operations', () => {
  it('all four operations appear in a large set', () => {
    const set = generateProblemSet(4, 333, 200);
    const ops = new Set(set.problems.map(p => p.operation));
    expect(ops.has('addition')).toBe(true);
    expect(ops.has('subtraction')).toBe(true);
    expect(ops.has('multiplication')).toBe(true);
    expect(ops.has('division')).toBe(true);
  });
});
