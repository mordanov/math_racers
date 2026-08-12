import type { Achievement } from '../achievements/types';
import type { RaceSummary } from './types';

export interface RaceSummaryResult {
  new_achievements: Achievement[];
}

export async function postRaceSummary(summary: RaceSummary): Promise<RaceSummaryResult> {
  const attempt = async (): Promise<RaceSummaryResult> => {
    const resp = await fetch('/api/v1/races', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(summary),
    });
    if (resp.status === 409) {
      // Duplicate — not an error worth surfacing
      return { new_achievements: [] };
    }
    if (!resp.ok) {
      throw new Error(`POST /api/v1/races failed: ${resp.status}`);
    }
    const data = (await resp.json()) as { new_achievements?: Achievement[] };
    return { new_achievements: data.new_achievements ?? [] };
  };

  try {
    return await attempt();
  } catch {
    // Retry once on network error
    return await attempt();
  }
}
