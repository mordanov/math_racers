import { apiClient } from '../../infrastructure/api-client';

export interface PlayerProgression {
  total_xp: number;
  current_level: number;
  xp_to_next_level: number;
}

export async function fetchProgression(): Promise<PlayerProgression> {
  return apiClient.get<PlayerProgression>('/progression');
}
