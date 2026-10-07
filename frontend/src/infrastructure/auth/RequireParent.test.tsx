import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import RequireParent from './RequireParent';
import * as AuthContextModule from './AuthContext';

vi.mock('./AuthContext');
vi.mock('../../shared/components/LoadingSpinner', () => ({
  LoadingSpinner: () => <div data-testid="spinner">Loading</div>,
}));

function setup(role: 'parent' | 'administrator' | null, isLoading = false) {
  vi.mocked(AuthContextModule.useAuth).mockReturnValue({
    account: role ? { id: 'u1', email: 'a@b.com', role } : null,
    isLoading,
    isAuthenticated: role !== null,
    activeChildId: null,
    login: vi.fn(),
    logout: vi.fn(),
    selectChild: vi.fn(),
  });
  return render(
    <MemoryRouter initialEntries={['/parent']}>
      <Routes>
        <Route element={<RequireParent />}>
          <Route path="/parent" element={<div>Parent Dashboard</div>} />
        </Route>
        <Route path="/" element={<div>Home</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('RequireParent', () => {
  it('renders child routes for parent role', () => {
    setup('parent');
    expect(screen.getByText('Parent Dashboard')).toBeInTheDocument();
  });

  it('redirects to / for administrator role (Review Focus #1)', () => {
    setup('administrator');
    expect(screen.getByText('Home')).toBeInTheDocument();
  });

  it('redirects to / when account is null', () => {
    setup(null);
    expect(screen.getByText('Home')).toBeInTheDocument();
  });

  it('shows LoadingSpinner while auth is loading', () => {
    setup(null, true);
    expect(screen.getByTestId('spinner')).toBeInTheDocument();
  });
});
