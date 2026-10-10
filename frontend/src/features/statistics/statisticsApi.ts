import { apiClient } from '../../infrastructure/api-client';

export interface PlayerStats {
  player_id: string;
  total_races: number;
  total_problems_solved: number;
  correct_answers: number;
  accuracy_all_time: number | null;
  avg_response_ms: number | null;
  favourite_operation: string | null;
  best_streak: number;
  updated_at: string;
}

export interface AvatarStats {
  avatar_id: string;
  player_id: string;
  total_races: number;
  wins: number;
  podiums: number;
  best_streak: number;
  last_race_at: string;
}

export interface RaceSessionRecord {
  id: string;
  avatar_id: string;
  mode: string;
  finishing_position: number | null;
  problems_solved: number;
  correct_answers: number;
  mistakes: number;
  difficulty_tier: number;
  xp_earned: number;
  avg_response_ms: number;
  longest_streak: number;
  started_at: string;
  finished_at: string;
}

export interface HistoryResponse {
  results: RaceSessionRecord[];
  page: number;
  total_pages: number;
  total_records: number;
}

export interface WeeklySummary {
  period_start: string;
  period_end: string;
  problems_solved: number;
  correct_answers: number;
  accuracy: number | null;
  avg_response_ms: number | null;
  strongest_operation: string | null;
  weakest_operation: string | null;
  races_completed: number;
  xp_earned: number;
}

export function fetchPlayerStats(): Promise<PlayerStats> {
  return apiClient.get<PlayerStats>('/players/me/statistics');
}

export function fetchHistory(page = 1): Promise<HistoryResponse> {
  return apiClient.get<HistoryResponse>(`/players/me/history?page=${page}`);
}

export function fetchWeeklySummary(): Promise<WeeklySummary> {
  return apiClient.get<WeeklySummary>('/players/me/weekly-summary');
}
