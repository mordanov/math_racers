import type { Tier, TierConfig } from './types';

export const TIER_CONFIGS: Record<Exclude<Tier, 6>, TierConfig> = {
  1: { tier: 1, operations: ['addition'], minOperand: 1, maxOperand: 10 },
  2: { tier: 2, operations: ['addition', 'subtraction'], minOperand: 1, maxOperand: 20 },
  3: {
    tier: 3,
    operations: ['addition', 'subtraction', 'multiplication'],
    minOperand: 1,
    maxOperand: 12,
  },
  4: {
    tier: 4,
    operations: ['addition', 'subtraction', 'multiplication', 'division'],
    minOperand: 1,
    maxOperand: 25,
  },
  5: {
    tier: 5,
    operations: ['addition', 'subtraction', 'multiplication', 'division'],
    minOperand: 1,
    maxOperand: 100,
  },
};
