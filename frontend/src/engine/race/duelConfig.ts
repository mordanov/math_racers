import type { Tier } from '../math/types';
import { BALANCED } from './personalities';
import type { ParticipantConfig } from './types';

export interface DuelConfig {
  tier: Tier;
  aiParticipants: ParticipantConfig[];
}

export function buildDuelConfig(playerTier: number): DuelConfig {
  const tier = Math.max(1, Math.min(6, playerTier)) as Tier;
  return {
    tier,
    aiParticipants: [
      {
        runnerId: 'duel-opponent',
        isHuman: false,
        avatarId: 'duel-ai',
        personality: { ...BALANCED, tierOffset: 0 },
      },
    ],
  };
}
