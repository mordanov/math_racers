import { apiClient } from '../../infrastructure/api-client';
import type { RaceMode } from '../../engine/race/types';
import type { Tier } from '../../engine/math/types';

export interface CreateRaceSessionParams {
  mode: RaceMode;
  tier: Tier;
  avatar_id: string;
  opponent_count: number;
  championship_id?: string;
}

export interface CreateRaceSessionResult {
  race_id: string;
  seed: number;
}

export async function createRaceSession(
  params: CreateRaceSessionParams,
): Promise<CreateRaceSessionResult> {
  const body: Record<string, unknown> = {
    mode: params.mode,
    difficulty_tier: params.tier,
    avatar_id: params.avatar_id,
    opponent_count: params.opponent_count,
  };
  if (params.championship_id !== undefined) {
    body.championship_id = params.championship_id;
  }
  return apiClient.post<CreateRaceSessionResult>('/races', body);
}
