import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import * as statsApi from '../features/statistics/statisticsApi';
import * as parentApi from '../features/statistics/parentApi';
import ParentDashboardPage from './ParentDashboardPage';

vi.mock('../features/statistics/statisticsApi');
vi.mock('../features/statistics/parentApi');

const mockSummary: statsApi.WeeklySummary = {
  period_start: '2026-09-30T00:00:00Z',
  period_end: '2026-10-07T00:00:00Z',
  problems_solved: 64,
  correct_answers: 58,
  accuracy: 0.906,
  avg_response_ms: 1800,
  strongest_operation: null,
  weakest_operation: null,
  races_completed: 8,
  xp_earned: 1920,
};

describe('ParentDashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(statsApi.fetchWeeklySummary).mockResolvedValue(mockSummary);
    vi.mocked(parentApi.fetchPersonalRecords).mockResolvedValue({
      best_streak: 15,
      best_race_accuracy: 1.0,
      fastest_avg_response_ms: 900,
      total_races: 42,
    });
  });

  function renderPage() {
    return render(
      <MemoryRouter>
        <ParentDashboardPage />
      </MemoryRouter>,
    );
  }

  it('renders the page container', () => {
    renderPage();
    expect(screen.getByTestId('page-parent-dashboard')).toBeInTheDocument();
  });

  it('shows weekly summary after loading', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText(/8 races/i)).toBeInTheDocument());
    expect(screen.getByText(/64/)).toBeInTheDocument();
    expect(screen.getByText(/91%/)).toBeInTheDocument();
  });

  it('shows personal records after loading', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByText('42')).toBeInTheDocument());
    expect(screen.getByText('15')).toBeInTheDocument();
  });

  it('shows data export link', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByRole('link', { name: /export/i })).toBeInTheDocument());
  });

  it('shows error message on fetch failure', async () => {
    vi.mocked(statsApi.fetchWeeklySummary).mockRejectedValue(new Error('network error'));
    renderPage();
    await waitFor(() => expect(screen.getByText(/failed to load/i)).toBeInTheDocument());
    expect(screen.queryByText('Loading…')).not.toBeInTheDocument();
  });
});
