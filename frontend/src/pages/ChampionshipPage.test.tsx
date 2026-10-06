import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as championshipApiModule from '../engine/race/championshipApi';
import ChampionshipPage from './ChampionshipPage';

vi.mock('../engine/race/championshipApi');

const activeChampionship = {
  championship_id: 'ch1',
  total_races: 3,
  races_completed: 1,
  status: 'active' as const,
  standings: [
    { avatar_id: 'av1', is_player: true, points: 10, podiums: 1, position: 1 },
    { avatar_id: 'ai-1', is_player: false, points: 6, podiums: 0, position: 2 },
  ],
};

function renderPage(champId = 'ch1') {
  return render(
    <MemoryRouter initialEntries={[`/championship/${champId}`]}>
      <Routes>
        <Route path="/championship/:id" element={<ChampionshipPage />} />
        <Route path="/race/setup" element={<div>Setup</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('ChampionshipPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(championshipApiModule.getChampionship).mockResolvedValue(activeChampionship);
  });

  it('shows standings table with position order', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByRole('table')).toBeInTheDocument());
    expect(screen.getByText('You')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
    expect(screen.getAllByRole('row').length).toBeGreaterThan(1);
  });

  it('shows Start Next Race button when championship is active', async () => {
    renderPage();
    await waitFor(() =>
      expect(screen.getByRole('button', { name: /start next race/i })).toBeInTheDocument(),
    );
  });

  it('navigates to /race/setup with championship context when Start Next Race clicked', async () => {
    const user = userEvent.setup();
    renderPage();
    await waitFor(() => screen.getByRole('button', { name: /start next race/i }));
    await user.click(screen.getByRole('button', { name: /start next race/i }));
    await waitFor(() => expect(screen.getByText('Setup')).toBeInTheDocument());
  });

  it('shows completion message when championship is completed', async () => {
    vi.mocked(championshipApiModule.getChampionship).mockResolvedValue({
      ...activeChampionship,
      races_completed: 3,
      status: 'completed',
    });
    renderPage();
    await waitFor(() => expect(screen.getByText(/championship complete/i)).toBeInTheDocument());
    expect(screen.queryByRole('button', { name: /start next race/i })).not.toBeInTheDocument();
  });

  it('has data-testid="page-championship"', async () => {
    renderPage();
    await waitFor(() => expect(screen.getByTestId('page-championship')).toBeInTheDocument());
  });
});
