import type { Achievement, PlayerAchievement } from './types';
import { apiClient } from '../../infrastructure/api-client';

interface AchievementListResponse {
  achievements: Achievement[];
}

interface PlayerAchievementListResponse {
  achievements: PlayerAchievement[];
}

export async function fetchAchievements(): Promise<Achievement[]> {
  const data = await apiClient.get<AchievementListResponse>('/achievements');
  return data.achievements;
}

export async function fetchPlayerAchievements(accountId: string): Promise<PlayerAchievement[]> {
  const data = await apiClient.get<PlayerAchievementListResponse>(
    `/players/${encodeURIComponent(accountId)}/achievements`,
  );
  return data.achievements;
}
