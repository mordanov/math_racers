import { apiClient } from '../../infrastructure/api-client';
import type { Operation, TierConfig } from '../../engine/math/types';

interface Tier6SettingsDto {
  custom_tier_config: {
    operations: Operation[];
    min_operand: number;
    max_operand: number;
  } | null;
}

function toTierConfig(settings: Tier6SettingsDto['custom_tier_config']): TierConfig | null {
  if (!settings) return null;
  return {
    tier: 6,
    operations: settings.operations,
    minOperand: settings.min_operand,
    maxOperand: settings.max_operand,
  };
}

export async function fetchTier6Settings(accountId: string): Promise<TierConfig | null> {
  const response = await apiClient.get<Tier6SettingsDto>(`/players/${accountId}/tier-6-settings`);
  return toTierConfig(response.custom_tier_config);
}

export async function saveTier6Settings(
  accountId: string,
  config: TierConfig,
): Promise<TierConfig> {
  const response = await apiClient.patch<Tier6SettingsDto>(
    `/players/${accountId}/tier-6-settings`,
    {
      custom_tier_config: {
        operations: config.operations,
        min_operand: config.minOperand,
        max_operand: config.maxOperand,
      },
    },
  );
  const saved = toTierConfig(response.custom_tier_config);
  if (!saved) throw new Error('The server did not save Tier 6 settings.');
  return saved;
}
