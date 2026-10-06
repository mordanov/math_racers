import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createRaceSession } from './raceSessionApi';

const mockPost = vi.hoisted(() => vi.fn());

vi.mock('../../infrastructure/api-client', () => ({
  apiClient: { post: mockPost },
}));

describe('createRaceSession', () => {
  beforeEach(() => vi.clearAllMocks());

  it('posts to /races with correct fields and returns race_id and seed', async () => {
    mockPost.mockResolvedValue({ race_id: 'r1', seed: 42 });
    const result = await createRaceSession({
      mode: 'quick',
      tier: 1,
      avatar_id: 'av1',
      opponent_count: 2,
    });
    expect(result).toEqual({ race_id: 'r1', seed: 42 });
    expect(mockPost).toHaveBeenCalledWith('/races', {
      mode: 'quick',
      difficulty_tier: 1,
      avatar_id: 'av1',
      opponent_count: 2,
    });
  });

  it('includes championship_id when provided', async () => {
    mockPost.mockResolvedValue({ race_id: 'r2', seed: 99 });
    await createRaceSession({
      mode: 'championship',
      tier: 2,
      avatar_id: 'av1',
      opponent_count: 3,
      championship_id: 'ch1',
    });
    expect(mockPost).toHaveBeenCalledWith('/races', {
      mode: 'championship',
      difficulty_tier: 2,
      avatar_id: 'av1',
      opponent_count: 3,
      championship_id: 'ch1',
    });
  });
});
