import type { Achievement, PlayerAchievement } from './types';

export async function fetchAchievements(accountId?: string): Promise<Achievement[]> {
  const url = accountId
    ? `/api/v1/achievements?account_id=${encodeURIComponent(accountId)}`
    : '/api/v1/achievements';
  const resp = await fetch(url, { credentials: 'include' });
  if (!resp.ok) throw new Error(`GET /api/v1/achievements failed: ${resp.status}`);
  const data = await resp.json();
  return data.achievements as Achievement[];
}

export async function fetchPlayerAchievements(accountId: string): Promise<PlayerAchievement[]> {
  const resp = await fetch(`/api/v1/players/${encodeURIComponent(accountId)}/achievements`, {
    credentials: 'include',
  });
  if (!resp.ok)
    throw new Error(`GET /api/v1/players/${accountId}/achievements failed: ${resp.status}`);
  const data = await resp.json();
  return data.achievements as PlayerAchievement[];
}
