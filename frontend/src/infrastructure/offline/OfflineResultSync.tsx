import { useCallback, useEffect, useRef, useState } from 'react';
import { postRaceSummary } from '../../engine/race/raceApi';
import { useAuth } from '../auth/AuthContext';
import { listPendingTrainingResults, removePendingTrainingResult } from './offlineStore';
import tokens from '../../shared/tokens';
import { useLocale } from '../localization/LocaleContext';

type SyncState = 'idle' | 'syncing' | 'synced' | 'error';

export default function OfflineResultSync() {
  const { activeChildId } = useAuth();
  const { t } = useLocale();
  const [state, setState] = useState<SyncState>('idle');
  const isSyncing = useRef(false);

  const sync = useCallback(async () => {
    if (!activeChildId || !navigator.onLine || isSyncing.current) return;
    isSyncing.current = true;
    setState('syncing');
    try {
      const pending = (await listPendingTrainingResults()).filter(
        (item) => item.child_profile_id === activeChildId,
      );
      for (const item of pending) {
        const result = await postRaceSummary(item.summary);
        await removePendingTrainingResult(item.idempotency_key);
        window.dispatchEvent(
          new CustomEvent('training-result-synced', {
            detail: { idempotency_key: item.idempotency_key, result },
          }),
        );
      }
      setState(pending.length > 0 ? 'synced' : 'idle');
    } catch {
      setState('error');
    } finally {
      isSyncing.current = false;
    }
  }, [activeChildId]);

  useEffect(() => {
    const handleOnline = () => {
      void sync();
    };
    window.addEventListener('online', handleOnline);
    if (navigator.onLine) void sync();
    return () => window.removeEventListener('online', handleOnline);
  }, [sync]);

  if (state === 'idle') return null;

  return (
    <div
      role={state === 'error' ? 'alert' : 'status'}
      aria-live="polite"
      style={{
        padding: tokens.spacing.sm,
        color: state === 'error' ? tokens.color.error : tokens.color.textPrimary,
      }}
    >
      {state === 'syncing' && t('Syncing saved Training results…')}
      {state === 'synced' && t('Saved Training results are synced.')}
      {state === 'error' && (
        <>
          {t('Training results could not sync. They remain saved on this device.')}{' '}
          <button type="button" onClick={() => void sync()}>
            {t('Retry')}
          </button>
        </>
      )}
    </div>
  );
}
