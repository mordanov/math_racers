import { render, screen } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';
import { vi } from 'vitest';
import { routeConfig } from './router';

vi.mock('./infrastructure/auth/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    isLoading: false,
    account: { id: 'u1', email: 'a@b.com', role: 'parent' },
    activeChildId: null,
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
