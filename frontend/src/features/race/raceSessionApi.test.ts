import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient } from '../../infrastructure/api-client';
import { createRaceSession } from './raceSessionApi';

vi.mock('../../infrastructure/api-client', () => ({
  apiClient: { post: vi.fn() },
}));

describe('createRaceSession', () => {
  beforeEach(() => vi.clearAllMocks());

  it('posts to /races with correct fields and returns race_id and seed', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ race_id: 'r1', seed: 42 });
    const result = await createRaceSession({ mode: 'quick', tier: 1, avatar_id: 'av1', opponent_count: 2 });
    expect(result).toEqual({ race_id: 'r1', seed: 42 });
    expect(apiClient.post).toHaveBeenCalledWith('/races', {
      mode: 'quick',
      difficulty_tier: 1,
      avatar_id: 'av1',
      opponent_count: 2,
    });
  });

  it('includes championship_id when provided', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({ race_id: 'r2', seed: 99 });
    await createRaceSession({ mode: 'championship', tier: 2, avatar_id: 'av1', opponent_count: 3, championship_id: 'ch1' });
    expect(apiClient.post).toHaveBeenCalledWith('/races', {
      mode: 'championship',
      difficulty_tier: 2,
      avatar_id: 'av1',
      opponent_count: 3,
      championship_id: 'ch1',
    });
  });
});
