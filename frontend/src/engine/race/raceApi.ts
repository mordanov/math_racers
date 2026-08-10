import type { RaceSummary } from './types';

export async function postRaceSummary(summary: RaceSummary): Promise<void> {
  const attempt = async () => {
    const resp = await fetch('/api/v1/races', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(summary),
    });
    if (resp.status === 409) {
      // Duplicate — not an error worth surfacing
      return;
    }
    if (!resp.ok) {
      throw new Error(`POST /api/v1/races failed: ${resp.status}`);
    }
  };

  try {
    await attempt();
  } catch {
    // Retry once on network error
    await attempt();
  }
}
