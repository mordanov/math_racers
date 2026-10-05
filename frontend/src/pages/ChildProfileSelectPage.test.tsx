import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import ChildProfileSelectPage from './ChildProfileSelectPage';
import * as childProfilesApi from '../infrastructure/auth/childProfilesApi';
import * as AuthContextModule from '../infrastructure/auth/AuthContext';

vi.mock('../infrastructure/auth/childProfilesApi');
vi.mock('../infrastructure/auth/AuthContext');

const mockSelectChild = vi.fn();

describe('ChildProfileSelectPage', () => {
  beforeEach(() => {
    vi.mocked(AuthContextModule.useAuth).mockReturnValue({
      selectChild: mockSelectChild,
      login: vi.fn(),
      logout: vi.fn(),
      isAuthenticated: true,
      isLoading: false,
      account: { id: 'acc-1', email: 'p@e.com', role: 'parent' },
      activeChildId: null,
    });
  });

  it('renders list of profiles', async () => {
    vi.mocked(childProfilesApi.fetchChildProfiles).mockResolvedValue([
      { id: 'p1', account_id: 'acc-1', display_name: 'Alice', created_at: '2026-01-01T00:00:00Z' },
      { id: 'p2', account_id: 'acc-1', display_name: 'Bob', created_at: '2026-01-02T00:00:00Z' },
    ]);
    render(
      <MemoryRouter>
        <ChildProfileSelectPage />
      </MemoryRouter>,
    );
    expect(await screen.findByText('Alice')).toBeInTheDocument();
    expect(screen.getByText('Bob')).toBeInTheDocument();
  });

  it('selecting a profile calls selectChild', async () => {
    vi.mocked(childProfilesApi.fetchChildProfiles).mockResolvedValue([
      { id: 'p1', account_id: 'acc-1', display_name: 'Alice', created_at: '2026-01-01T00:00:00Z' },
    ]);
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <ChildProfileSelectPage />
      </MemoryRouter>,
    );
    await user.click(await screen.findByText('Alice'));
    expect(mockSelectChild).toHaveBeenCalledWith('p1');
  });

  it('shows empty state when no profiles exist', async () => {
    vi.mocked(childProfilesApi.fetchChildProfiles).mockResolvedValue([]);
    render(
      <MemoryRouter>
        <ChildProfileSelectPage />
      </MemoryRouter>,
    );
    expect(await screen.findByText(/no profiles yet/i)).toBeInTheDocument();
  });
});
