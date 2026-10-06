import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import * as avatarApiModule from '../engine/avatar/avatarApi';
import AvatarCreatorPage from './AvatarCreatorPage';

vi.mock('../engine/avatar/avatarApi');

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...(actual as object),
    useNavigate: () => mockNavigate,
  };
});

describe('AvatarCreatorPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it('shows species selection on step 1', () => {
    render(
      <MemoryRouter>
        <AvatarCreatorPage />
      </MemoryRouter>,
    );
    expect(screen.getByRole('heading', { name: /choose your animal/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /fox/i })).toBeInTheDocument();
  });

  it('advancing to step 2 shows colour picker', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(
      <MemoryRouter>
        <AvatarCreatorPage />
      </MemoryRouter>,
    );
    await user.click(screen.getByRole('button', { name: /fox/i }));
    await user.click(screen.getByRole('button', { name: /next/i }));
    expect(screen.getByRole('heading', { name: /choose colours/i })).toBeInTheDocument();
  });

  it('going back from step 2 preserves species selection', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(
      <MemoryRouter>
        <AvatarCreatorPage />
      </MemoryRouter>,
    );
    await user.click(screen.getByRole('button', { name: /fox/i }));
    await user.click(screen.getByRole('button', { name: /next/i }));
    await user.click(screen.getByRole('button', { name: /back/i }));
    expect(screen.getByRole('button', { name: /fox/i })).toHaveAttribute('aria-pressed', 'true');
  });

  it('step 5 calls createAvatar and polls until complete then navigates', async () => {
    vi.mocked(avatarApiModule.createAvatar).mockResolvedValue({
      avatar_id: 'a1',
      job_id: 'j1',
      status: 'queued',
    });
    vi.mocked(avatarApiModule.pollGenerationJob)
      .mockResolvedValueOnce({
        job_id: 'j1',
        avatar_id: 'a1',
        status: 'generating',
        attempt: 1,
        error: null,
        created_at: '2026-01-01T00:00:00Z',
        completed_at: null,
      })
      .mockResolvedValue({
        job_id: 'j1',
        avatar_id: 'a1',
        status: 'complete',
        attempt: 1,
        error: null,
        created_at: '2026-01-01T00:00:00Z',
        completed_at: '2026-01-01T00:01:00Z',
      });

    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(
      <MemoryRouter>
        <AvatarCreatorPage />
      </MemoryRouter>,
    );

    // Step 1: species
    await user.click(screen.getByRole('button', { name: /fox/i }));
    await user.click(screen.getByRole('button', { name: /next/i }));
    // Step 2: colour — just click Next (defaults are fine)
    await user.click(screen.getByRole('button', { name: /next/i }));
    // Step 3: style — just click Next
    await user.click(screen.getByRole('button', { name: /next/i }));
    // Step 4: clothing — just click Next
    await user.click(screen.getByRole('button', { name: /next/i }));
    // Step 5: reveal — createAvatar is called automatically
    await waitFor(() => expect(avatarApiModule.createAvatar).toHaveBeenCalledTimes(1));

    // First poll at 3000ms returns 'generating'; second poll at 6000ms returns 'complete'
    await vi.advanceTimersByTimeAsync(3000);
    await vi.advanceTimersByTimeAsync(3000);
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith('/avatars'));
  });

  it('shows friendly error message when generation permanently fails', async () => {
    vi.mocked(avatarApiModule.createAvatar).mockResolvedValue({
      avatar_id: 'a1',
      job_id: 'j1',
      status: 'queued',
    });
    vi.mocked(avatarApiModule.pollGenerationJob).mockResolvedValue({
      job_id: 'j1',
      avatar_id: 'a1',
      status: 'permanent_failure',
      attempt: 3,
      error: 'Generation failed',
      created_at: '2026-01-01T00:00:00Z',
      completed_at: '2026-01-01T00:01:00Z',
    });

    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    render(
      <MemoryRouter>
        <AvatarCreatorPage />
      </MemoryRouter>,
    );

    // Navigate through all steps to reveal
    await user.click(screen.getByRole('button', { name: /fox/i }));
    await user.click(screen.getByRole('button', { name: /next/i }));
    await user.click(screen.getByRole('button', { name: /next/i }));
    await user.click(screen.getByRole('button', { name: /next/i }));
    await user.click(screen.getByRole('button', { name: /next/i }));

    await waitFor(() => expect(avatarApiModule.createAvatar).toHaveBeenCalledTimes(1));
    // Advance timer to trigger first poll which returns permanent_failure
    await vi.advanceTimersByTimeAsync(3000);
    await waitFor(() => expect(screen.getByText(/went wobbly/i)).toBeInTheDocument());
  });
});
