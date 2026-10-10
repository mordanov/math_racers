import { render, screen } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';
import { vi } from 'vitest';
import { routeConfig } from './router';

vi.mock('./engine/avatar/avatarApi', () => ({
  listAvatars: () =>
    Promise.resolve([
      {
        avatar_id: 'avatar-1',
        name: 'Test Fox',
        species: 'fox',
        status: 'published',
        is_favourite: false,
        portrait: null,
        created_at: '',
      },
    ]),
}));

vi.mock('./features/race/raceSessionApi', () => ({
  createRaceSession: () => Promise.resolve({ race_id: 'race-1', seed: 1 }),
}));

vi.mock('./infrastructure/offline/offlineStore', () => ({
  cacheChildData: vi.fn(),
  getCachedChildData: vi.fn().mockResolvedValue(null),
  listPendingTrainingResults: vi.fn().mockResolvedValue([]),
  removePendingTrainingResult: vi.fn(),
}));

vi.mock('./infrastructure/offline/OfflineResultSync', () => ({ default: () => null }));

vi.mock('./features/statistics/statisticsApi', () => ({
  fetchPlayerStats: () =>
    Promise.resolve({
      total_races: 0,
      correct_answers: 0,
      total_problems_solved: 0,
      accuracy_all_time: null,
      avg_response_ms: null,
      favourite_operation: null,
      best_streak: 0,
      updated_at: '',
    }),
  fetchHistory: () => Promise.resolve({ results: [], page: 1, total_pages: 1, total_records: 0 }),
  fetchWeeklySummary: () =>
    Promise.resolve({
      period_start: '',
      period_end: '',
      problems_solved: 0,
      correct_answers: 0,
      accuracy: null,
      avg_response_ms: null,
      strongest_operation: null,
      weakest_operation: null,
      races_completed: 0,
      xp_earned: 0,
    }),
}));

vi.mock('./features/statistics/parentApi', () => ({
  fetchPersonalRecords: () =>
    Promise.resolve({
      best_streak: 0,
      best_race_accuracy: null,
      fastest_avg_response_ms: null,
      total_races: 0,
    }),
}));

vi.mock('./shared/hooks/useAudioManager', () => ({
  useAudioManager: () => ({ playMusic: vi.fn(), stopMusic: vi.fn() }),
}));

vi.mock('./infrastructure/auth/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    isLoading: false,
    account: { id: 'u1', email: 'a@b.com', role: 'parent' },
    activeChildId: 'child-1',
    login: vi.fn(),
    logout: vi.fn(),
    selectChild: vi.fn(),
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}));

function go(path: string) {
  const r = createMemoryRouter(routeConfig, { initialEntries: [path] });
  render(<RouterProvider router={r} />);
}

it('/ renders home page', () => {
  go('/');
  expect(screen.getByTestId('page-home')).toBeInTheDocument();
});

it('/avatars renders avatar gallery', () => {
  go('/avatars');
  expect(screen.getByTestId('page-avatar-gallery')).toBeInTheDocument();
});

it('/avatars/new renders avatar creator', () => {
  go('/avatars/new');
  expect(screen.getByTestId('page-avatar-creator')).toBeInTheDocument();
});

it('/race/setup renders race setup', () => {
  go('/race/setup');
  expect(screen.getByTestId('page-race-setup')).toBeInTheDocument();
});

it('/race/:id renders race screen', () => {
  go('/race/abc123');
  expect(screen.getByTestId('page-race-screen')).toBeInTheDocument();
});

it('/race/:id/results renders results screen', () => {
  go('/race/abc123/results');
  expect(screen.getByTestId('page-results-screen')).toBeInTheDocument();
});

it('/statistics renders statistics page', () => {
  go('/statistics');
  expect(screen.getByTestId('page-statistics')).toBeInTheDocument();
});

it('/settings renders settings page', () => {
  go('/settings');
  expect(screen.getByTestId('page-settings')).toBeInTheDocument();
});

it('/parent renders parent dashboard', () => {
  go('/parent');
  expect(screen.getByTestId('page-parent-dashboard')).toBeInTheDocument();
});

it('/championship/:id renders championship page', () => {
  go('/championship/ch1');
  expect(screen.getByTestId('page-championship')).toBeInTheDocument();
});
