import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as avatarApiModule from '../engine/avatar/avatarApi';
import * as raceSessionApiModule from '../features/race/raceSessionApi';
import * as championshipApiModule from '../engine/race/championshipApi';
import RaceSetupPage from './RaceSetupPage';

vi.mock('../engine/avatar/avatarApi');
vi.mock('../features/race/raceSessionApi');
vi.mock('../engine/race/championshipApi');

const published = {
  avatar_id: 'av1',
  name: 'Foxy',
  species: 'fox',
  status: 'published' as const,
  is_favourite: false,
  portrait: null,
  created_at: '',
};

describe('RaceSetupPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([published]);
    vi.mocked(raceSessionApiModule.createRaceSession).mockResolvedValue({ race_id: 'r1', seed: 42 });
  });

  function renderPage(initialPath = '/race/setup', state?: unknown) {
    return render(
      <MemoryRouter initialEntries={[{ pathname: initialPath, state }]}>
        <Routes>
          <Route path="/race/setup" element={<RaceSetupPage />} />
          <Route path="/avatars/new" element={<div>Avatar Creator</div>} />
          <Route path="/race/:id" element={<div>Race Screen</div>} />
        </Routes>
      </MemoryRouter>,
    );
  }

  it('redirects to /avatars/new when no published avatars exist', async () => {
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([]);
    renderPage();
    await waitFor(() => expect(screen.getByText('Avatar Creator')).toBeInTheDocument());
  });

  it('renders mode selector buttons', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByRole('button', { name: /quick race/i })).toBeInTheDocument());
    expect(screen.getByRole('button', { name: /training/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /duel/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /championship/i })).toBeInTheDocument();
  });

  it('shows championship races dropdown only when championship mode is active', async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => screen.getByRole('button', { name: /championship/i }));
    expect(screen.queryByLabelText(/number of races/i)).not.toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /championship/i }));
    expect(screen.getByLabelText(/number of races/i)).toBeInTheDocument();
  });

  it('creates race session and navigates to /race/:id on start', async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => screen.getByRole('button', { name: /start race/i }));
    await user.click(screen.getByRole('button', { name: /start race/i }));
    await waitFor(() => expect(screen.getByText('Race Screen')).toBeInTheDocument());
    expect(raceSessionApiModule.createRaceSession).toHaveBeenCalled();
  });

  it('pre-selects championship mode when continueChampionshipId in route state', async () => {
    vi.mocked(championshipApiModule.getChampionship).mockResolvedValue({
      championship_id: 'ch1',
      total_races: 3,
      races_completed: 1,
      status: 'active',
      standings: [],
    });
    renderPage('/race/setup', { continueChampionshipId: 'ch1', continueRaceIndex: 1 });
    await waitFor(() => {
      const btn = screen.getByRole('button', { name: /championship/i });
      expect(btn).toHaveAttribute('aria-pressed', 'true');
    });
  });
});
