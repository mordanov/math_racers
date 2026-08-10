import type { AiPersonality } from './types';

export interface AiObstacleResult {
  isCorrect: boolean;
  responseTimeMs: number;
}

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

function sampleResponseTime(
  profile: AiPersonality['speedProfile'],
  checkpointIndex: number,
  rng: () => number,
): number {
  const t = checkpointIndex / 7;
  let base: number;
  if (profile === 'front_loaded') {
    base = lerp(1500, 5000, t);
  } else if (profile === 'back_loaded') {
    base = lerp(5000, 1500, t);
  } else if (profile === 'random') {
    base = rng() * 6000 + 1000;
  } else {
    base = 3500;
  }
  return base + (rng() - 0.5) * 1000;
}

function speedMultiplier(
  profile: AiPersonality['speedProfile'],
  checkpointIndex: number,
  rng: () => number,
): number {
  if (profile === 'front_loaded') {
    if (checkpointIndex < 3) return 1.2;
    if (checkpointIndex < 6) return 1.0;
    return 0.9;
  }
  if (profile === 'back_loaded') {
    if (checkpointIndex < 3) return 0.85;
    if (checkpointIndex < 6) return 1.0;
    return 1.25;
  }
  if (profile === 'random') {
    return 0.7 + rng() * 0.6;
  }
  return 1.0;
}

export function simulateAiObstacle(
  personality: AiPersonality,
  checkpointIndex: number,
  rng: () => number,
): AiObstacleResult {
  const accuracyRoll = rng();
  const isCorrect = accuracyRoll < personality.accuracyRate;

  const base = sampleResponseTime(personality.speedProfile, checkpointIndex, rng);
  const mult = speedMultiplier(personality.speedProfile, checkpointIndex, rng);
  const responseTimeMs = Math.max(0, base * mult);

  return { isCorrect, responseTimeMs };
}
