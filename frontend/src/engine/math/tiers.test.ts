import { describe, expect, it } from 'vitest';
import { generateProblemSet } from './generator';
import { TIER_CONFIGS } from './tiers';

describe('difficulty tier operation sets', () => {
  it('uses multiplication in Tier 3 and division in Tier 4', () => {
    expect(TIER_CONFIGS[3].operations).toEqual(['multiplication']);
    expect(TIER_CONFIGS[4].operations).toEqual(['division']);
  });

  it('requires custom settings for Tier 6', () => {
    expect(() => generateProblemSet(6, 42, 1)).toThrow(/parent-configured/);
  });
});
