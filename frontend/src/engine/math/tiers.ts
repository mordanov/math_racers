import type { Tier, TierConfig } from './types';

export const TIER_CONFIGS: Record<Exclude<Tier, 6>, TierConfig> = {
  1: { tier: 1, operations: ['addition'], minOperand: 1, maxOperand: 10 },
  2: { tier: 2, operations: ['addition', 'subtraction'], minOperand: 1, maxOperand: 20 },
  3: { tier: 3, operations: ['multiplication'], minOperand: 1, maxOperand: 99 },
  4: {
    tier: 4,
    operations: ['division'],
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

export function supportsDivisionRange(minOperand: number, maxOperand: number): boolean {
  return maxOperand >= 2 * Math.max(2, minOperand);
}
