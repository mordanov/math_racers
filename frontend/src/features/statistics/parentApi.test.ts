import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchPersonalRecords } from './parentApi';

const mockGet = vi.hoisted(() => vi.fn());

vi.mock('../../infrastructure/api-client', () => ({
  apiClient: { get: mockGet },
}));

describe('parentApi', () => {
  beforeEach(() => vi.clearAllMocks());

  it('fetchPersonalRecords calls /players/me/personal-records', async () => {
    mockGet.mockResolvedValue({ best_streak: 15, total_races: 20 });
    const result = await fetchPersonalRecords();
    expect(mockGet).toHaveBeenCalledWith('/players/me/personal-records');
    expect(result).toEqual({ best_streak: 15, total_races: 20 });
  });
});
