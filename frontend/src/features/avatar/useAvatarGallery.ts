import { useCallback, useEffect, useRef, useState } from 'react';
import {
  deleteAvatar,
  listAvatars,
  patchAvatar,
  regeneratePortrait,
} from '../../engine/avatar/avatarApi';
import type { AvatarListItem, AvatarStatus } from '../../engine/avatar/types';

export function useAvatarGallery() {
  const [avatars, setAvatars] = useState<AvatarListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mutationError, setMutationError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchAvatars = useCallback(async (fromPoll = false) => {
    try {
      const data = await listAvatars();
      setAvatars(data);
      if (!fromPoll) setLoading(false);

      const hasPending = data.some((a) => a.status === 'pending');
      if (hasPending && !intervalRef.current) {
        intervalRef.current = setInterval(() => {
          void fetchAvatars(true);
        }, 3000);
      } else if (!hasPending && intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
        if (fromPoll) setLoading(false);
      }
    } catch {
      setError('Looks like we lost the signal. Check your connection!');
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchAvatars();
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [fetchAvatars]);

  const clearMutationError = useCallback(() => setMutationError(null), []);

  const toggleFavourite = useCallback(async (avatarId: string, isFavourite: boolean) => {
    setAvatars((list) =>
      list.map((a) => (a.avatar_id === avatarId ? { ...a, is_favourite: isFavourite } : a)),
    );
    try {
      await patchAvatar(avatarId, { is_favourite: isFavourite });
      setMutationError(null);
    } catch {
      setAvatars((list) =>
        list.map((a) => (a.avatar_id === avatarId ? { ...a, is_favourite: !isFavourite } : a)),
      );
      setMutationError('Could not update favourite. Try again.');
    }
  }, []);

  const renameAvatar = useCallback(async (avatarId: string, name: string) => {
    let previousName: string | null = null;
    setAvatars((list) => {
      previousName = list.find((a) => a.avatar_id === avatarId)?.name ?? null;
      return list.map((a) => (a.avatar_id === avatarId ? { ...a, name } : a));
    });
    try {
      await patchAvatar(avatarId, { name });
      setMutationError(null);
    } catch {
      setAvatars((list) =>
        list.map((a) => (a.avatar_id === avatarId ? { ...a, name: previousName } : a)),
      );
      setMutationError('Could not rename avatar. Try again.');
    }
  }, []);

  const startRegenerate = useCallback(
    async (avatarId: string) => {
      let previousStatus: AvatarStatus = 'published';
      setAvatars((list) => {
        previousStatus = list.find((a) => a.avatar_id === avatarId)?.status ?? 'published';
        return list.map((a) =>
          a.avatar_id === avatarId ? { ...a, status: 'pending' as AvatarStatus } : a,
        );
      });
      try {
        await regeneratePortrait(avatarId);
        setMutationError(null);
        void fetchAvatars(true);
      } catch {
        setAvatars((list) =>
          list.map((a) => (a.avatar_id === avatarId ? { ...a, status: previousStatus } : a)),
        );
        setMutationError('Could not regenerate portrait. Try again.');
      }
    },
    [fetchAvatars],
  );

  const removeAvatar = useCallback(async (avatarId: string) => {
    let removedItem: AvatarListItem | undefined;
    let removedIndex = -1;
    setAvatars((list) => {
      removedIndex = list.findIndex((a) => a.avatar_id === avatarId);
      removedItem = list[removedIndex];
      return list.filter((a) => a.avatar_id !== avatarId);
    });
    try {
      await deleteAvatar(avatarId);
      setMutationError(null);
    } catch {
      setAvatars((list) => {
        if (removedItem === undefined || removedIndex === -1) return list;
        const next = [...list];
        next.splice(removedIndex, 0, removedItem);
        return next;
      });
      setMutationError('Could not delete avatar. Try again.');
    }
  }, []);

  return {
    avatars,
    loading,
    error,
    mutationError,
    clearMutationError,
    toggleFavourite,
    renameAvatar,
    startRegenerate,
    removeAvatar,
  };
}
