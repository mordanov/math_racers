import type { AiPersonality } from './types';

export const STEADY: AiPersonality = {
  id: 'steady',
  name: 'Steady',
  accuracyRate: 0.80,
  baseResponseTimeMs: 3500,
  responseTimeVarianceMs: 175,
  speedProfile: 'uniform',
  tierOffset: 0,
};

export const SPEEDSTER: AiPersonality = {
  id: 'speedster',
  name: 'Speedster',
  accuracyRate: 0.70,
  baseResponseTimeMs: 3500,
  responseTimeVarianceMs: 350,
  speedProfile: 'front_loaded',
  tierOffset: 1,
};

export const SLOW_STARTER: AiPersonality = {
  id: 'slow_starter',
  name: 'Slow Starter',
  accuracyRate: 0.75,
  baseResponseTimeMs: 3500,
  responseTimeVarianceMs: 280,
  speedProfile: 'back_loaded',
  tierOffset: 0,
};

export const UNPREDICTABLE: AiPersonality = {
  id: 'unpredictable',
  name: 'Unpredictable',
  accuracyRate: 0.65,
  baseResponseTimeMs: 3500,
  responseTimeVarianceMs: 875,
  speedProfile: 'random',
  tierOffset: 0,
};

export const BALANCED: AiPersonality = {
  id: 'balanced',
  name: 'Balanced',
  accuracyRate: 0.78,
  baseResponseTimeMs: 3500,
  responseTimeVarianceMs: 245,
  speedProfile: 'uniform',
  tierOffset: 0,
};

export const PERSONALITIES: AiPersonality[] = [STEADY, SPEEDSTER, SLOW_STARTER, UNPREDICTABLE, BALANCED];

export async function fetchPersonalities(): Promise<AiPersonality[]> {
  const resp = await fetch('/api/v1/opponents/personalities');
  if (!resp.ok) {
    throw new Error(`GET /api/v1/opponents/personalities failed: ${resp.status}`);
  }
  return resp.json() as Promise<AiPersonality[]>;
}
