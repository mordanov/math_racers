import type { Achievement, PlayerAchievement } from './types';
import { apiClient } from '../../infrastructure/api-client';

interface AchievementListResponse {
  achievements: Achievement[];
}

interface PlayerAchievementListResponse {
  achievements: PlayerAchievement[];
}

export async function fetchAchievements(accountId?: string): Promise<Achievement[]> {
  const path = accountId
    ? `/achievements?account_id=${encodeURIComponent(accountId)}`
    : '/achievements';
  const data = await apiClient.get<AchievementListResponse>(path);
  return data.achievements;
}

export async function fetchPlayerAchievements(accountId: string): Promise<PlayerAchievement[]> {
  const data = await apiClient.get<PlayerAchievementListResponse>(
    `/players/${encodeURIComponent(accountId)}/achievements`,
  );
  return data.achievements;
}
