// @vitest-environment node
import { describe, it, expect } from 'vitest';
import { validateAnswer } from '../../../src/engine/math/validator';
import type { Problem } from '../../../src/engine/math/types';

function makeProblem(answer: number): Problem {
  return {
    id: 'test-id',
    operation: 'addition',
    operand_a: 7,
    operand_b: 3,
    answer,
    tier: 1,
    seed: 0,
  };
}

describe('validateAnswer', () => {
  it('returns correct:true for exact integer answer', () => {
    const result = validateAnswer(makeProblem(10), '10', Date.now());
    expect(result.correct).toBe(true);
    expect(result.reason).toBeUndefined();
  });

  it('returns correct:false for wrong integer', () => {
    const result = validateAnswer(makeProblem(10), '9', Date.now());
    expect(result.correct).toBe(false);
    expect(result.reason).toBeUndefined();
  });

  it('returns correct:false and reason:not_a_number for alphabetic input', () => {
    const result = validateAnswer(makeProblem(10), 'abc', Date.now());
    expect(result.correct).toBe(false);
    expect(result.reason).toBe('not_a_number');
  });

  it('returns correct:false and reason:not_a_number for empty string', () => {
    const result = validateAnswer(makeProblem(10), '', Date.now());
    expect(result.correct).toBe(false);
    expect(result.reason).toBe('not_a_number');
  });

  it('trims whitespace before parsing', () => {
    const result = validateAnswer(makeProblem(10), '  10  ', Date.now());
    expect(result.correct).toBe(true);
  });

  it('returns a non-negative elapsedMs', () => {
    const renderTime = Date.now() - 50;
    const result = validateAnswer(makeProblem(10), '10', renderTime);
    expect(result.elapsedMs).toBeGreaterThanOrEqual(0);
  });

  it('never throws for any input', () => {
    const inputs = ['', ' ', 'NaN', '3.14', '99999999', '☃'];
    inputs.forEach(input => {
      expect(() => validateAnswer(makeProblem(5), input, Date.now())).not.toThrow();
    });
  });
});
