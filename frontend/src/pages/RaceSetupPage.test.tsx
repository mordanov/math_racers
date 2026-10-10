import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as avatarApiModule from '../engine/avatar/avatarApi';
import * as raceSessionApiModule from '../features/race/raceSessionApi';
import * as tier6SettingsApiModule from '../features/race/tier6SettingsApi';
import * as championshipApiModule from '../engine/race/championshipApi';
import * as sfxModule from '../shared/hooks/useSfxPlayer';
import * as authModule from '../infrastructure/auth/AuthContext';
import * as statisticsApiModule from '../features/statistics/statisticsApi';
import * as offlineStoreModule from '../infrastructure/offline/offlineStore';
import RaceSetupPage from './RaceSetupPage';

vi.mock('../engine/avatar/avatarApi');
vi.mock('../features/race/raceSessionApi');
vi.mock('../features/race/tier6SettingsApi');
vi.mock('../engine/race/championshipApi');
vi.mock('../shared/hooks/useSfxPlayer');
vi.mock('../infrastructure/auth/AuthContext', () => ({ useAuth: vi.fn() }));
vi.mock('../features/statistics/statisticsApi');
vi.mock('../infrastructure/offline/offlineStore', () => ({
  cacheChildData: vi.fn().mockResolvedValue(undefined),
  getCachedChildData: vi.fn().mockResolvedValue(null),
}));

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
    vi.mocked(raceSessionApiModule.createRaceSession).mockResolvedValue({
      race_id: 'r1',
      seed: 42,
    });
    vi.mocked(tier6SettingsApiModule.fetchTier6Settings).mockResolvedValue(null);
    vi.mocked(tier6SettingsApiModule.saveTier6Settings).mockImplementation((_accountId, settings) =>
      Promise.resolve(settings),
    );
    vi.mocked(statisticsApiModule.fetchPlayerStats).mockResolvedValue({
      player_id: 'player-1',
      total_races: 0,
      total_problems_solved: 0,
      correct_answers: 0,
      accuracy_all_time: null,
      avg_response_ms: null,
      favourite_operation: null,
      best_streak: 0,
      updated_at: '',
    });
    vi.mocked(offlineStoreModule.getCachedChildData).mockResolvedValue(null);
    vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx: vi.fn() });
    vi.mocked(authModule.useAuth).mockReturnValue({
      account: { id: 'parent-1', email: 'parent@example.com', role: 'parent' },
      activeChildId: 'child-1',
    } as ReturnType<typeof authModule.useAuth>);
  });

  afterEach(() => {
    Object.defineProperty(navigator, 'onLine', { configurable: true, value: true });
  });

  function renderPage(initialPath = '/race/setup', state?: unknown) {
    return render(
      <MemoryRouter initialEntries={[{ pathname: initialPath, state }]}>
        <Routes>
          <Route path="/race/setup" element={<RaceSetupPage />} />
          <Route path="/avatars/new" element={<div>Avatar Creator</div>} />
          <Route path="/child-profiles" element={<div>Choose Child</div>} />
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
    await waitFor(() =>
      expect(screen.getByRole('button', { name: /quick race/i })).toBeInTheDocument(),
    );
    expect(screen.getByRole('button', { name: /training/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /duel/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /championship/i })).toBeInTheDocument();
  });

  it('redirects to child selection when no active child is set', async () => {
    vi.mocked(authModule.useAuth).mockReturnValue({
      activeChildId: null,
    } as ReturnType<typeof authModule.useAuth>);
    renderPage();
    await waitFor(() => expect(screen.getByText('Choose Child')).toBeInTheDocument());
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

  it('saves parent-selected Tier 6 settings before creating a session', async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => screen.getByLabelText(/difficulty/i));
    await user.selectOptions(screen.getByLabelText(/difficulty/i), '6');
    await user.click(screen.getByLabelText('division'));
    const maxOperand = screen.getByLabelText(/maximum operand/i);
    await user.clear(maxOperand);
    await user.type(maxOperand, '50');
    expect(screen.getByRole('button', { name: /start race/i })).toBeDisabled();
    await user.click(screen.getByRole('button', { name: /save tier 6 settings/i }));
    await waitFor(() =>
      expect(tier6SettingsApiModule.saveTier6Settings).toHaveBeenCalledWith('parent-1', {
        tier: 6,
        operations: ['addition', 'division'],
        minOperand: 1,
        maxOperand: 50,
      }),
    );
    await user.click(screen.getByRole('button', { name: /start race/i }));

    await waitFor(() => expect(screen.getByText('Race Screen')).toBeInTheDocument());
    expect(raceSessionApiModule.createRaceSession).toHaveBeenCalledWith(
      expect.objectContaining({
        tier: 6,
      }),
    );
  });

  it('uses the saved Training session when offline', async () => {
    Object.defineProperty(navigator, 'onLine', { configurable: true, value: false });
    vi.mocked(offlineStoreModule.getCachedChildData).mockResolvedValue({
      child_profile_id: 'child-1',
      avatars: [published],
      statistics: null,
      training_session: {
        race_id: 'offline-race',
        seed: 99,
        tier: 1,
        avatar_id: 'av1',
        avatar_species: 'fox',
      },
    });

    const user = userEvent.setup();
    renderPage();
    await waitFor(() => expect(screen.getByRole('button', { name: /start race/i })).toBeEnabled());
    expect(screen.getByLabelText(/difficulty/i)).toBeDisabled();
    await user.click(screen.getByRole('button', { name: /start race/i }));

    await waitFor(() => expect(screen.getByText('Race Screen')).toBeInTheDocument());
    expect(raceSessionApiModule.createRaceSession).not.toHaveBeenCalled();
  });

  it('plays ui_card_select sfx when hovering over a mode card', async () => {
    const user = userEvent.setup();
    const playSfx = vi.fn();
    vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
    renderPage();
    await waitFor(() => screen.getByRole('button', { name: /quick race/i }));
    await user.hover(screen.getByRole('button', { name: /quick race/i }));
    expect(playSfx).toHaveBeenCalledWith('ui_card_select');
  });

  it('plays ui_avatar_select sfx when Start Race is clicked', async () => {
    const user = userEvent.setup();
    const playSfx = vi.fn();
    vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
    renderPage();
    await waitFor(() => screen.getByRole('button', { name: /start race/i }));
    await user.click(screen.getByRole('button', { name: /start race/i }));
    expect(playSfx).toHaveBeenCalledWith('ui_avatar_select');
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
