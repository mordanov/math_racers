import { EXCELLENT_THRESHOLD_MS, GOOD_THRESHOLD_MS, PERFECT_THRESHOLD_MS } from './constants';
import type { TierResult } from './types';

export function calculateMovement(isCorrect: boolean, responseTimeMs: number): TierResult {
  if (!isCorrect) {
    return { tier: 'incorrect', distanceMetres: 0 };
  }
  if (responseTimeMs < PERFECT_THRESHOLD_MS) {
    return { tier: 'perfect', distanceMetres: 18 };
  }
  if (responseTimeMs < EXCELLENT_THRESHOLD_MS) {
    return { tier: 'excellent', distanceMetres: 15 };
  }
  if (responseTimeMs < GOOD_THRESHOLD_MS) {
    return { tier: 'good', distanceMetres: 12 };
  }
  return { tier: 'slow', distanceMetres: 9 };
}
