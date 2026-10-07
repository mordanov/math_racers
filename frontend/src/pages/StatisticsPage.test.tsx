import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import * as statsApi from '../features/statistics/statisticsApi';
import StatisticsPage from './StatisticsPage';

vi.mock('../features/statistics/statisticsApi');

const mockStats: statsApi.PlayerStats = {
  player_id: 'p1',
  total_races: 10,
  total_problems_solved: 80,
  correct_answers: 72,
  accuracy_all_time: 0.9,
  avg_response_ms: 1800,
  favourite_operation: null,
  best_streak: 12,
  updated_at: '2026-10-07T12:00:00Z',
};

const mockHistory: statsApi.HistoryResponse = {
  results: [
    {
      id: 's1',
      avatar_id: 'av1',
      mode: 'quick',
      finishing_position: 1,
      problems_solved: 8,
      correct_answers: 7,
      mistakes: 1,
      difficulty_tier: 3,
      xp_earned: 100,
      avg_response_ms: 1500,
      longest_streak: 5,
      started_at: '2026-10-07T11:00:00Z',
      finished_at: '2026-10-07T11:01:00Z',
    },
  ],
  page: 1,
  total_pages: 1,
  total_records: 1,
};

describe('StatisticsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(statsApi.fetchPlayerStats).mockResolvedValue(mockStats);
    vi.mocked(statsApi.fetchHistory).mockResolvedValue(mockHistory);
  });

  function renderPage() {
    return render(
      <MemoryRouter>
        <StatisticsPage />
      </MemoryRouter>,
    );
  }

  it('renders the page container', () => {
    renderPage();
    expect(screen.getByTestId('page-statistics')).toBeInTheDocument();
  });

  it('shows player stats after loading', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText('10')).toBeInTheDocument());
    expect(screen.getByText('90%')).toBeInTheDocument();
    expect(screen.getByText('1800')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
  });

  it('shows race history entries', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText(/quick/i)).toBeInTheDocument());
    expect(screen.getByText(/7 \/ 8/)).toBeInTheDocument();
  });

  it('shows null accuracy as — when no races yet', async () => {
    vi.mocked(statsApi.fetchPlayerStats).mockResolvedValue({
      ...mockStats,
      total_races: 0,
      accuracy_all_time: null,
      avg_response_ms: null,
    });
    renderPage();
    await waitFor(() => expect(screen.getAllByText('—').length).toBeGreaterThan(0));
  });

  it('shows error message on fetch failure', async () => {
    vi.mocked(statsApi.fetchPlayerStats).mockRejectedValue(new Error('network error'));
    renderPage();
    await waitFor(() => expect(screen.getByText(/failed to load/i)).toBeInTheDocument());
    expect(screen.queryByText('Loading…')).not.toBeInTheDocument();
  });
});
