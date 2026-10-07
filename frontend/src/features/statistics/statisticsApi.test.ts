import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fetchHistory, fetchPlayerStats, fetchWeeklySummary } from './statisticsApi';

const mockGet = vi.hoisted(() => vi.fn());

vi.mock('../../infrastructure/api-client', () => ({
  apiClient: { get: mockGet },
}));

describe('statisticsApi', () => {
  beforeEach(() => vi.clearAllMocks());

  it('fetchPlayerStats calls /players/me/statistics', async () => {
    mockGet.mockResolvedValue({ total_races: 5, accuracy_all_time: 0.9 });
    const result = await fetchPlayerStats();
    expect(mockGet).toHaveBeenCalledWith('/players/me/statistics');
    expect(result).toEqual({ total_races: 5, accuracy_all_time: 0.9 });
  });

  it('fetchHistory calls /players/me/history with default page 1', async () => {
    mockGet.mockResolvedValue({ results: [], page: 1, total_pages: 1, total_records: 0 });
    await fetchHistory();
    expect(mockGet).toHaveBeenCalledWith('/players/me/history?page=1');
  });

  it('fetchHistory passes page number to query string', async () => {
    mockGet.mockResolvedValue({ results: [], page: 3, total_pages: 5, total_records: 100 });
    await fetchHistory(3);
    expect(mockGet).toHaveBeenCalledWith('/players/me/history?page=3');
  });

  it('fetchWeeklySummary calls /players/me/weekly-summary', async () => {
    mockGet.mockResolvedValue({ races_completed: 3, accuracy: 0.875 });
    const result = await fetchWeeklySummary();
    expect(mockGet).toHaveBeenCalledWith('/players/me/weekly-summary');
    expect(result).toEqual({ races_completed: 3, accuracy: 0.875 });
  });
});
