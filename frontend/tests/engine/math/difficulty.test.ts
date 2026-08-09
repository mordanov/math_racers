// @vitest-environment node
import { describe, it, expect } from 'vitest';
import { selectTier } from '../../../src/engine/math/difficulty';

describe('selectTier — skill score thresholds', () => {
  it('advances tier when skillScore >= 0.90', () => {
    expect(selectTier({ currentTier: 2, skillScore: 0.90 })).toBe(3);
    expect(selectTier({ currentTier: 2, skillScore: 0.95 })).toBe(3);
    expect(selectTier({ currentTier: 2, skillScore: 1.0 })).toBe(3);
  });

  it('decreases tier when skillScore < 0.60', () => {
    expect(selectTier({ currentTier: 3, skillScore: 0.59 })).toBe(2);
    expect(selectTier({ currentTier: 3, skillScore: 0.0 })).toBe(2);
  });

  it('keeps tier when 0.60 <= skillScore < 0.90', () => {
    expect(selectTier({ currentTier: 3, skillScore: 0.60 })).toBe(3);
    expect(selectTier({ currentTier: 3, skillScore: 0.75 })).toBe(3);
    expect(selectTier({ currentTier: 3, skillScore: 0.89 })).toBe(3);
  });
});

describe('selectTier — boundary clamping', () => {
  it('does not advance beyond tier 6', () => {
    expect(selectTier({ currentTier: 6, skillScore: 1.0 })).toBe(6);
  });

  it('does not decrease below tier 1', () => {
    expect(selectTier({ currentTier: 1, skillScore: 0.0 })).toBe(1);
  });
});

describe('selectTier — parent override', () => {
  it('returns clamped override regardless of skill score', () => {
    expect(selectTier({ currentTier: 2, skillScore: 0.95, parentOverride: 4 })).toBe(4);
    expect(selectTier({ currentTier: 5, skillScore: 0.1, parentOverride: 3 })).toBe(3);
  });

  it('clamps override silently to [1, 6]', () => {
    expect(selectTier({ currentTier: 3, skillScore: 0.5, parentOverride: 7 })).toBe(6);
    expect(selectTier({ currentTier: 3, skillScore: 0.5, parentOverride: 0 })).toBe(1);
    expect(selectTier({ currentTier: 3, skillScore: 0.5, parentOverride: -5 })).toBe(1);
  });
});
