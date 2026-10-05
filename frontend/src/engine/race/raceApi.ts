import type { Achievement } from '../achievements/types';
import type { RaceSummary } from './types';
import { apiClient, APIError } from '../../infrastructure/api-client';

export interface RaceSummaryResult {
  new_achievements: Achievement[];
}

export async function postRaceSummary(summary: RaceSummary): Promise<RaceSummaryResult> {
  try {
    return await apiClient.post<RaceSummaryResult>('/races', summary);
  } catch (e) {
    if (e instanceof APIError && e.status === 409) {
      return { new_achievements: [] };
    }
    throw e;
  }
}
