// @vitest-environment node
import { describe, expect, it } from 'vitest';
import { calculateMovement } from '../../../src/engine/race/movement';

describe('calculateMovement — incorrect answer', () => {
  it('returns 0 m for incorrect answer regardless of time', () => {
    expect(calculateMovement(false, 0)).toEqual({ tier: 'incorrect', distanceMetres: 0 });
    expect(calculateMovement(false, 1000)).toEqual({ tier: 'incorrect', distanceMetres: 0 });
    expect(calculateMovement(false, 10000)).toEqual({ tier: 'incorrect', distanceMetres: 0 });
  });
});

describe('calculateMovement — Perfect tier (< 2000 ms)', () => {
  it('returns 18 m for 0 ms', () => {
    expect(calculateMovement(true, 0)).toEqual({ tier: 'perfect', distanceMetres: 18 });
  });

  it('returns 18 m for 1999 ms', () => {
    expect(calculateMovement(true, 1999)).toEqual({ tier: 'perfect', distanceMetres: 18 });
  });
});

describe('calculateMovement — Excellent tier (2000–3999 ms)', () => {
  it('returns 15 m at boundary 2000 ms', () => {
    expect(calculateMovement(true, 2000)).toEqual({ tier: 'excellent', distanceMetres: 15 });
  });

  it('returns 15 m at 3999 ms', () => {
    expect(calculateMovement(true, 3999)).toEqual({ tier: 'excellent', distanceMetres: 15 });
  });
});

describe('calculateMovement — Good tier (4000–5999 ms)', () => {
  it('returns 12 m at boundary 4000 ms', () => {
    expect(calculateMovement(true, 4000)).toEqual({ tier: 'good', distanceMetres: 12 });
  });

  it('returns 12 m at 5999 ms', () => {
    expect(calculateMovement(true, 5999)).toEqual({ tier: 'good', distanceMetres: 12 });
  });
});

describe('calculateMovement — Slow tier (>= 6000 ms)', () => {
  it('returns 9 m at boundary 6000 ms', () => {
    expect(calculateMovement(true, 6000)).toEqual({ tier: 'slow', distanceMetres: 9 });
  });

  it('returns 9 m for very slow response', () => {
    expect(calculateMovement(true, 30000)).toEqual({ tier: 'slow', distanceMetres: 9 });
  });
});
