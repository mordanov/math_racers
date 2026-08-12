import type { Achievement, PlayerAchievement } from './types';

interface AchievementListResponse {
  achievements: Achievement[];
}

export async function fetchAchievements(accountId?: string): Promise<Achievement[]> {
  const url = accountId
    ? `/api/v1/achievements?account_id=${encodeURIComponent(accountId)}`
    : '/api/v1/achievements';
  const resp = await fetch(url, { credentials: 'include' });
  if (!resp.ok) throw new Error(`GET /api/v1/achievements failed: ${resp.status}`);
  const data = (await resp.json()) as AchievementListResponse;
  return data.achievements;
}

interface PlayerAchievementListResponse {
  achievements: PlayerAchievement[];
}

export async function fetchPlayerAchievements(accountId: string): Promise<PlayerAchievement[]> {
  const resp = await fetch(`/api/v1/players/${encodeURIComponent(accountId)}/achievements`, {
    credentials: 'include',
  });
  if (!resp.ok)
    throw new Error(`GET /api/v1/players/${accountId}/achievements failed: ${resp.status}`);
  const data = (await resp.json()) as PlayerAchievementListResponse;
  return data.achievements;
}
