import type { AiPersonality } from './types';

function gaussianNoise(rng: () => number): number {
  // Box-Muller transform
  const u1 = Math.max(rng(), 1e-10); // avoid log(0)
  const u2 = rng();
  return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
}

export interface AiObstacleResult {
  isCorrect: boolean;
  responseTimeMs: number;
}

export function simulateAiObstacle(
  personality: AiPersonality,
  rng: () => number,
): AiObstacleResult {
  const accuracyRoll = rng();
  const isCorrect = accuracyRoll < personality.accuracyRate;

  const noise = gaussianNoise(rng) * personality.responseTimeVarianceMs;
  const responseTimeMs = Math.max(0, personality.baseResponseTimeMs + noise);

  return { isCorrect, responseTimeMs };
}
