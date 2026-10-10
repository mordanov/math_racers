import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { RaceSummary } from '../../engine/race/types';
import * as raceApi from '../../engine/race/raceApi';
import * as authModule from '../auth/AuthContext';
import * as offlineStore from './offlineStore';
import OfflineResultSync from './OfflineResultSync';

vi.mock('../../engine/race/raceApi');
vi.mock('../auth/AuthContext', () => ({ useAuth: vi.fn() }));
vi.mock('./offlineStore', () => ({
  listPendingTrainingResults: vi.fn(),
  removePendingTrainingResult: vi.fn(),
}));

const summary: RaceSummary = {
  race_id: 'race-1',
  idempotency_key: 'race-1',
  mode: 'training',
  human_avatar_id: 'avatar-1',
  started_at: '2026-01-01T00:00:00.000Z',
  completed_at: '2026-01-01T00:01:00.000Z',
  participants: [],
  answers: [],
};

const pending: offlineStore.PendingTrainingResult = {
  idempotency_key: summary.idempotency_key,
  child_profile_id: 'child-1',
  summary,
  player_avatar_id: 'avatar-1',
  avatar_species: 'fox',
  created_at: summary.completed_at,
};

describe('OfflineResultSync', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Object.defineProperty(navigator, 'onLine', { configurable: true, value: true });
    vi.mocked(authModule.useAuth).mockReturnValue({
      activeChildId: 'child-1',
    } as ReturnType<typeof authModule.useAuth>);
    vi.mocked(offlineStore.listPendingTrainingResults).mockResolvedValue([pending]);
    vi.mocked(offlineStore.removePendingTrainingResult).mockResolvedValue(undefined);
    vi.mocked(raceApi.postRaceSummary).mockResolvedValue({
      new_achievements: [],
      progression: { xp_earned_this_race: 20 },
    });
  });

  it('syncs and removes results after the server confirms them', async () => {
    render(<OfflineResultSync />);

    await waitFor(() =>
      expect(offlineStore.removePendingTrainingResult).toHaveBeenCalledWith(
        summary.idempotency_key,
      ),
    );
    expect(raceApi.postRaceSummary).toHaveBeenCalledWith(summary);
    expect(screen.getByText(/results are synced/i)).toBeInTheDocument();
  });

  it('keeps results and offers retry when sync fails', async () => {
    vi.mocked(raceApi.postRaceSummary)
      .mockRejectedValueOnce(new Error('network error'))
      .mockResolvedValueOnce({
        new_achievements: [],
        progression: { xp_earned_this_race: 20 },
      });

    render(<OfflineResultSync />);

    const retry = await screen.findByRole('button', { name: 'Retry' });
    expect(offlineStore.removePendingTrainingResult).not.toHaveBeenCalled();
    fireEvent.click(retry);

    await waitFor(() =>
      expect(offlineStore.removePendingTrainingResult).toHaveBeenCalledWith(
        summary.idempotency_key,
      ),
    );
  });
});
