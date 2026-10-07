import { act, renderHook, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import * as avatarApiModule from '../../engine/avatar/avatarApi';
import { useAvatarGallery } from './useAvatarGallery';
import type { AvatarListItem } from '../../engine/avatar/types';

vi.mock('../../engine/avatar/avatarApi');

const published: AvatarListItem = {
  avatar_id: 'a1',
  name: 'Foxy',
  species: 'fox',
  status: 'published',
  is_favourite: false,
  portrait: null,
  created_at: '2026-01-01T00:00:00Z',
};

const pending: AvatarListItem = {
  avatar_id: 'a2',
  name: null,
  species: 'rabbit',
  status: 'pending',
  is_favourite: false,
  portrait: null,
  created_at: '2026-01-01T00:00:00Z',
};

describe('useAvatarGallery', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });
  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  it('returns loaded avatars after initial fetch', async () => {
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([published]);
    const { result } = renderHook(() => useAvatarGallery());
    expect(result.current.loading).toBe(true);
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.avatars).toHaveLength(1);
    expect(result.current.avatars[0].avatar_id).toBe('a1');
  });

  it('does NOT start polling when all avatars are published', async () => {
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([published]);
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));
    // Advance past poll interval — listAvatars should still only have been called once
    act(() => {
      vi.advanceTimersByTime(10000);
    });
    expect(avatarApiModule.listAvatars).toHaveBeenCalledTimes(1);
  });

  it('starts polling when an avatar is pending', async () => {
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([pending]);
    const setIntervalSpy = vi.spyOn(global, 'setInterval');
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(setIntervalSpy).toHaveBeenCalledWith(expect.any(Function), 3000);
  });

  it('stops polling when re-fetch returns no pending avatars', async () => {
    vi.mocked(avatarApiModule.listAvatars)
      .mockResolvedValueOnce([pending])
      .mockResolvedValue([published]);
    const clearIntervalSpy = vi.spyOn(global, 'clearInterval');
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));

    act(() => {
      vi.advanceTimersByTime(3000);
    });
    await waitFor(() =>
      expect(result.current.avatars.every((a) => a.status !== 'pending')).toBe(true),
    );
    expect(clearIntervalSpy).toHaveBeenCalled();
  });

  it('sets child-friendly error message on fetch failure', async () => {
    vi.mocked(avatarApiModule.listAvatars).mockRejectedValue(new Error('Network error'));
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.error).toBe('Looks like we lost the signal. Check your connection!');
  });
});

describe('useAvatarGallery mutations', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([published]);
  });
  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  it('toggleFavourite optimistically flips is_favourite then calls patchAvatar', async () => {
    vi.mocked(avatarApiModule.patchAvatar).mockResolvedValue({ ...published, is_favourite: true } as never);
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));

    act(() => {
      void result.current.toggleFavourite('a1', true);
    });

    expect(result.current.avatars[0].is_favourite).toBe(true);
    expect(avatarApiModule.patchAvatar).toHaveBeenCalledWith('a1', { is_favourite: true });
  });

  it('toggleFavourite reverts on API error', async () => {
    vi.mocked(avatarApiModule.patchAvatar).mockRejectedValue(new Error('fail'));
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.toggleFavourite('a1', true);
    });

    expect(result.current.avatars[0].is_favourite).toBe(false);
    expect(result.current.mutationError).toBeTruthy();
  });

  it('renameAvatar optimistically updates name then calls patchAvatar', async () => {
    vi.mocked(avatarApiModule.patchAvatar).mockResolvedValue({ ...published, name: 'Renamed' } as never);
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));

    act(() => {
      void result.current.renameAvatar('a1', 'Renamed');
    });

    expect(result.current.avatars[0].name).toBe('Renamed');
    expect(avatarApiModule.patchAvatar).toHaveBeenCalledWith('a1', { name: 'Renamed' });
  });

  it('renameAvatar reverts on API error', async () => {
    vi.mocked(avatarApiModule.patchAvatar).mockRejectedValue(new Error('fail'));
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.renameAvatar('a1', 'Renamed');
    });

    expect(result.current.avatars[0].name).toBe('Foxy');
    expect(result.current.mutationError).toBeTruthy();
  });

  it('removeAvatar optimistically removes avatar then calls deleteAvatar', async () => {
    vi.mocked(avatarApiModule.deleteAvatar).mockResolvedValue(undefined);
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.removeAvatar('a1');
    });

    expect(result.current.avatars).toHaveLength(0);
    expect(avatarApiModule.deleteAvatar).toHaveBeenCalledWith('a1');
  });

  it('removeAvatar restores item at original index on API error (Review Focus #3)', async () => {
    const second: AvatarListItem = { ...published, avatar_id: 'a2', name: 'Bear', species: 'bear' };
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([published, second]);
    vi.mocked(avatarApiModule.deleteAvatar).mockRejectedValue(new Error('fail'));
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.removeAvatar('a1');
    });

    expect(result.current.avatars[0].avatar_id).toBe('a1');
    expect(result.current.mutationError).toBeTruthy();
  });

  it('clearMutationError clears the error string', async () => {
    vi.mocked(avatarApiModule.patchAvatar).mockRejectedValue(new Error('fail'));
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));
    await act(async () => {
      await result.current.toggleFavourite('a1', true);
    });
    expect(result.current.mutationError).toBeTruthy();

    act(() => {
      result.current.clearMutationError();
    });

    expect(result.current.mutationError).toBeNull();
  });

  it('startRegenerate sets avatar to pending and calls regeneratePortrait', async () => {
    vi.mocked(avatarApiModule.regeneratePortrait).mockResolvedValue({
      avatar_id: 'a1',
      job_id: 'j1',
      status: 'queued',
    } as never);
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));

    act(() => {
      void result.current.startRegenerate('a1');
    });

    expect(result.current.avatars[0].status).toBe('pending');
    expect(avatarApiModule.regeneratePortrait).toHaveBeenCalledWith('a1');
  });
});
