import { apiClient } from '../../infrastructure/api-client';

export interface PersonalRecords {
  best_streak: number;
  best_race_accuracy: number | null;
  fastest_avg_response_ms: number | null;
  total_races: number;
}

export function fetchPersonalRecords(): Promise<PersonalRecords> {
  return apiClient.get<PersonalRecords>('/players/me/personal-records');
}
