import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import * as statsApi from '../features/statistics/statisticsApi';
import * as parentApi from '../features/statistics/parentApi';
import * as authModule from '../infrastructure/auth/AuthContext';
import * as offlineStoreModule from '../infrastructure/offline/offlineStore';
import * as childProfileApi from '../engine/childProfiles/childProfilesApi';
import ParentDashboardPage from './ParentDashboardPage';

vi.mock('../features/statistics/statisticsApi');
vi.mock('../features/statistics/parentApi');
vi.mock('../infrastructure/auth/AuthContext', () => ({ useAuth: vi.fn() }));
vi.mock('../infrastructure/offline/offlineStore', () => ({
  deleteCachedChildData: vi.fn().mockResolvedValue(undefined),
  getCachedChildData: vi.fn().mockResolvedValue(null),
}));
vi.mock('../engine/childProfiles/childProfilesApi');

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
  afterEach(() => vi.restoreAllMocks());

  beforeEach(() => {
    vi.clearAllMocks();
    Object.defineProperty(navigator, 'onLine', { configurable: true, value: true });
    vi.mocked(statsApi.fetchWeeklySummary).mockResolvedValue(mockSummary);
    vi.mocked(parentApi.fetchPersonalRecords).mockResolvedValue({
      best_streak: 15,
      best_race_accuracy: 1.0,
      fastest_avg_response_ms: 900,
      total_races: 42,
    });
    vi.mocked(authModule.useAuth).mockReturnValue({
      account: null,
      activeChildId: 'child-1',
      isAuthenticated: false,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      selectChild: vi.fn(),
    } as ReturnType<typeof authModule.useAuth>);
    vi.mocked(offlineStoreModule.getCachedChildData).mockResolvedValue(null);
    vi.mocked(offlineStoreModule.deleteCachedChildData).mockResolvedValue(undefined);
    vi.mocked(childProfileApi.listLegacyData).mockResolvedValue([]);
    vi.mocked(childProfileApi.assignLegacyData).mockResolvedValue({ assigned: 1 });
    vi.mocked(childProfileApi.exportChildData).mockResolvedValue({});
    vi.mocked(childProfileApi.deleteChildProfile).mockResolvedValue(undefined);
  });

  function renderPage() {
    return render(
      <MemoryRouter>
        <ParentDashboardPage />
      </MemoryRouter>,
    );
  }

  it('renders the page container', async () => {
    renderPage();
    expect(screen.getByTestId('page-parent-dashboard')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText(/8 races/i)).toBeInTheDocument());
    await waitFor(() => expect(screen.getByText(/no unassigned records/i)).toBeInTheDocument());
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

  it('shows cached progress when offline', async () => {
    Object.defineProperty(navigator, 'onLine', { configurable: true, value: false });
    vi.mocked(offlineStoreModule.getCachedChildData).mockResolvedValue({
      child_profile_id: 'child-1',
      avatars: [],
      training_session: null,
      statistics: {
        player_id: 'child-1',
        total_races: 3,
        total_problems_solved: 24,
        correct_answers: 20,
        accuracy_all_time: 20 / 24,
        avg_response_ms: 1200,
        favourite_operation: 'addition',
        best_streak: 5,
        updated_at: '',
      },
    });

    renderPage();

    await waitFor(() => expect(screen.getByText('3 races completed')).toBeInTheDocument());
    expect(screen.getByText('24 problems answered')).toBeInTheDocument();
    expect(statsApi.fetchWeeklySummary).not.toHaveBeenCalled();
  });

  it('lets the parent assign selected legacy records to the active child', async () => {
    vi.mocked(childProfileApi.listLegacyData).mockResolvedValue([
      { record_type: 'avatar', record_id: 'avatar-1', label: 'Fox' },
    ]);
    renderPage();

    const checkbox = await screen.findByRole('checkbox', { name: /avatar: fox/i });
    fireEvent.click(checkbox);
    fireEvent.click(screen.getByRole('button', { name: /assign selected data/i }));

    await waitFor(() =>
      expect(childProfileApi.assignLegacyData).toHaveBeenCalledWith('child-1', [
        { record_type: 'avatar', record_id: 'avatar-1' },
      ]),
    );
    expect(await screen.findByRole('status')).toHaveTextContent(/1 records assigned/i);
  });

  it('deletes the selected child and clears the active child selection', async () => {
    const selectChild = vi.fn();
    vi.mocked(authModule.useAuth).mockReturnValue({
      account: null,
      activeChildId: 'child-1',
      isAuthenticated: false,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      selectChild,
    } as ReturnType<typeof authModule.useAuth>);
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    renderPage();
    await waitFor(() => screen.getByRole('button', { name: /delete child profile and data/i }));

    fireEvent.click(screen.getByRole('button', { name: /delete child profile and data/i }));

    await waitFor(() => expect(childProfileApi.deleteChildProfile).toHaveBeenCalledWith('child-1'));
    expect(offlineStoreModule.deleteCachedChildData).toHaveBeenCalledWith('child-1');
    expect(selectChild).toHaveBeenCalledWith(null);
  });

  it('reports when deleted child data could not be removed from offline storage', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    vi.mocked(offlineStoreModule.deleteCachedChildData).mockRejectedValue(
      new Error('IndexedDB unavailable'),
    );
    renderPage();

    fireEvent.click(await screen.findByRole('button', { name: /delete child profile and data/i }));

    expect(
      await screen.findByText(/profile was deleted, but saved offline data could not be removed/i),
    ).toBeInTheDocument();
    expect(childProfileApi.deleteChildProfile).toHaveBeenCalledWith('child-1');
    expect(offlineStoreModule.deleteCachedChildData).toHaveBeenCalledWith('child-1');
  });
});
