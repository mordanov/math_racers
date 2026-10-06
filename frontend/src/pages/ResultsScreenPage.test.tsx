import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as raceApiModule from '../engine/race/raceApi';
import * as progressionApiModule from '../features/race/progressionApi';
import * as championshipApiModule from '../engine/race/championshipApi';
import ResultsScreenPage from './ResultsScreenPage';
import type { RaceSummary } from '../engine/race/types';

vi.mock('../engine/race/raceApi');
vi.mock('../features/race/progressionApi');
vi.mock('../engine/race/championshipApi');

const makeSummary = (xpEarned = 80): RaceSummary => ({
  race_id: 'r1',
  seed: '1',
  difficulty_tier: 1,
  mode: 'quick',
  started_at: '',
  completed_at: '',
  participants: [
    { avatar_id: 'av1', position: 1, problems_correct: 7, longest_streak: 5, average_response_ms: 1500, total_distance: 126, xp_earned: xpEarned },
    { avatar_id: 'ai-1', position: 2, problems_correct: 5, longest_streak: 3, average_response_ms: 3000, total_distance: 90, xp_earned: 60 },
  ],
});

function renderPage(state: unknown) {
  return render(
    <MemoryRouter initialEntries={[{ pathname: '/race/r1/results', state }]}>
      <Routes>
        <Route path="/race/:id/results" element={<ResultsScreenPage />} />
        <Route path="/" element={<div>Home</div>} />
        <Route path="/race/setup" element={<div>Setup</div>} />
        <Route path="/championship/:id" element={<div>Championship</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('ResultsScreenPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(raceApiModule.postRaceSummary).mockResolvedValue({ new_achievements: [] });
    vi.mocked(progressionApiModule.fetchProgression).mockResolvedValue({
      player_id: 'p1', total_xp: 200, current_level: 1, xp_to_next_level: 200,
    });
  });

  it('renders empty page when no route state', () => {
    render(
      <MemoryRouter initialEntries={['/race/r1/results']}>
        <Routes>
          <Route path="/race/:id/results" element={<ResultsScreenPage />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByTestId('page-results-screen')).toBeInTheDocument();
  });

  it('renders results table with col headers and participant rows', async () => {
    renderPage({ summary: makeSummary(), playerAvatarId: 'av1' });
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument());
    expect(screen.getByRole('columnheader', { name: /place/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /correct/i })).toBeInTheDocument();
    expect(screen.getByText('You')).toBeInTheDocument();
    expect(screen.getByText('126m')).toBeInTheDocument();
  });

  it('shows level-up overlay when level increased after race', async () => {
    // Player earned 80 XP. total_xp now = 400 (level 2). Before = 320 (still level 1).
    // level(400) = floor(sqrt(4)) = 2; level(320) = floor(sqrt(3.2)) = 1
    vi.mocked(progressionApiModule.fetchProgression).mockResolvedValue({
      player_id: 'p1', total_xp: 400, current_level: 2, xp_to_next_level: 500,
    });
    renderPage({ summary: makeSummary(80), playerAvatarId: 'av1' });
    await waitFor(() => expect(screen.getByText(/level up/i)).toBeInTheDocument());
  });

  it('shows achievement toast for each new achievement', async () => {
    vi.mocked(raceApiModule.postRaceSummary).mockResolvedValue({
      new_achievements: [{
        key: 'first_race', title: 'First Steps', category: 'racing',
        description: 'Complete your first race', hidden: false, icon_path: '', unlocked_at: '',
      }],
    });
    renderPage({ summary: makeSummary(), playerAvatarId: 'av1' });
    await waitFor(() => expect(screen.getByText(/achievement: first steps/i)).toBeInTheDocument());
  });

  it('shows retry button with role=alert when sync fails', async () => {
    vi.mocked(raceApiModule.postRaceSummary).mockRejectedValue(new Error('Network error'));
    renderPage({ summary: makeSummary(), playerAvatarId: 'av1' });
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument());
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  it('shows View Championship button and calls recordChampionshipRace when mode is championship', async () => {
    vi.mocked(championshipApiModule.recordChampionshipRace).mockResolvedValue({
      championship_id: 'ch1', total_races: 3, races_completed: 1, status: 'active', standings: [],
    });
    const summary: RaceSummary = { ...makeSummary(), mode: 'championship' };
    renderPage({ summary, playerAvatarId: 'av1', championshipId: 'ch1', raceIndex: 0 });
    await waitFor(() => expect(championshipApiModule.recordChampionshipRace).toHaveBeenCalledWith(
      'ch1', 'r1', 0, expect.any(Array),
    ));
    expect(screen.getByRole('button', { name: /view championship/i })).toBeInTheDocument();
  });
});
