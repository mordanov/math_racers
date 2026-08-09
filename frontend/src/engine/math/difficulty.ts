import type { Tier, TierSelectionInput } from './types';

function clampTier(value: number): Tier {
  return Math.max(1, Math.min(6, value)) as Tier;
}

export function selectTier(input: TierSelectionInput): Tier {
  const { currentTier, skillScore, parentOverride } = input;
  if (parentOverride !== undefined && parentOverride !== null) {
    return clampTier(parentOverride);
  }
  if (skillScore >= 0.9) {
    return clampTier(currentTier + 1);
  }
  if (skillScore < 0.6) {
    return clampTier(currentTier - 1);
  }
  return currentTier;
}
