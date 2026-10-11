import { afterEach, describe, expect, it, vi } from 'vitest';
import { fetchProgression } from './progressionApi';

describe('fetchProgression', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('requests the backend progression route', async () => {
    const progression = {
      total_xp: 250,
      current_level: 1,
      xp_to_next_level: 150,
    };
    const fetchMock = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      json: vi.fn().mockResolvedValue(progression),
    });
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchProgression()).resolves.toEqual(progression);
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/progression', {
      method: 'GET',
      headers: {},
      body: undefined,
      credentials: 'same-origin',
    });
  });
});
