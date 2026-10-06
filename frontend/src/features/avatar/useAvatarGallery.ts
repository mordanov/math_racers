import { useCallback, useEffect, useRef, useState } from 'react';
import { listAvatars } from '../../engine/avatar/avatarApi';
import type { AvatarListItem } from '../../engine/avatar/types';

export function useAvatarGallery() {
  const [avatars, setAvatars] = useState<AvatarListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
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

  return { avatars, loading, error };
}
