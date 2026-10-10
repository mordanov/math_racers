import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { recordChampionshipRace } from '../engine/race/championshipApi';
import { postRaceSummary } from '../engine/race/raceApi';
import type { RaceSummary } from '../engine/race/types';
import type { Achievement } from '../engine/achievements/types';
import type { RaceSummaryResult } from '../engine/race/raceApi';
import { fetchProgression } from '../features/race/progressionApi';
import { Button } from '../shared/components/Button';
import { NotificationToast } from '../shared/components/NotificationToast';
import { getBadgeUrl } from '../features/achievements/achievementBadges';
import { queueTrainingResult } from '../infrastructure/offline/offlineStore';
import { useAudioManager } from '../shared/hooks/useAudioManager';
import { useSfxPlayer } from '../shared/hooks/useSfxPlayer';
import { useVoicePlayer } from '../shared/hooks/useVoicePlayer';
import type { Species } from '../shared/hooks/useVoicePlayer';
import tokens from '../shared/tokens';

interface ResultsRouteState {
  summary: RaceSummary;
  playerAvatarId: string;
  avatarSpecies: string;
  childProfileId?: string;
  championshipId?: string;
  raceIndex?: number;
}

type SyncStatus = 'pending' | 'saved' | 'queued' | 'error';

function computeLevel(totalXp: number): number {
  return Math.max(1, Math.floor(Math.sqrt(totalXp / 100)));
}

export default function ResultsScreenPage() {
  const location = useLocation();
  const routeState = location.state as ResultsRouteState | null;
  if (!routeState) return <div data-testid="page-results-screen" />;
  return <ResultsScreen routeState={routeState} />;
}

function ResultsScreen({ routeState }: { routeState: ResultsRouteState }) {
  const navigate = useNavigate();
  const { summary, playerAvatarId, avatarSpecies, childProfileId, championshipId, raceIndex } =
    routeState;

  const [syncStatus, setSyncStatus] = useState<SyncStatus>('pending');
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [toastIndex, setToastIndex] = useState(0);
  const [currentLevel, setCurrentLevel] = useState<number | null>(null);
  const [levelBefore, setLevelBefore] = useState<number | null>(null);
  const [xpEarned, setXpEarned] = useState(0);
  const { playMusic, stopMusic } = useAudioManager();
  const { playSfx } = useSfxPlayer();
  const { playVoice } = useVoicePlayer((avatarSpecies as Species) || null);

  const playerEntry = summary.participants.find((p) => p.avatar_id === playerAvatarId);

  useEffect(() => {
    playMusic('victory');
    return () => stopMusic();
  }, []); // stable refs

  useEffect(() => {
    playVoice('celebrating');
  }, []); // stable ref

  async function doSync() {
    const queueLocally = async (): Promise<boolean> => {
      if (summary.mode !== 'training' || !childProfileId) return false;
      await queueTrainingResult({
        idempotency_key: summary.idempotency_key,
        child_profile_id: childProfileId,
        summary,
        player_avatar_id: playerAvatarId,
        avatar_species: avatarSpecies,
        created_at: new Date().toISOString(),
      });
      setSyncStatus('queued');
      return true;
    };

    if (!navigator.onLine && (await queueLocally())) return;

    try {
      const result = await postRaceSummary(summary);
      setAchievements(result.new_achievements);
      let xpEarnedThisFlow = result.progression?.xp_earned_this_race ?? 0;

      if (championshipId !== undefined && raceIndex !== undefined) {
        const championship = await recordChampionshipRace(
          championshipId,
          summary.race_id,
          raceIndex,
          summary.participants.map((p) => ({
            avatar_id: p.avatar_id,
            is_player: p.avatar_id === playerAvatarId,
            finishing_position: p.position ?? 1,
          })),
        );
        xpEarnedThisFlow += championship.completion_xp_awarded ?? 0;
      }
      setXpEarned(xpEarnedThisFlow);

      const progression = await fetchProgression();
      setCurrentLevel(progression.current_level);
      if (playerEntry) {
        setLevelBefore(computeLevel(progression.total_xp - xpEarnedThisFlow));
      }
      setSyncStatus('saved');
    } catch (error) {
      if ((!navigator.onLine || error instanceof TypeError) && (await queueLocally())) return;
      throw error;
    }
  }

  useEffect(() => {
    let cancelled = false;
    doSync().catch(() => {
      if (!cancelled) setSyncStatus('error');
    });
    return () => {
      cancelled = true;
    };
  }, []); // doSync closes over stable props/state from mount

  useEffect(() => {
    const handleSynced = (event: Event) => {
      const detail = (
        event as CustomEvent<{
          idempotency_key: string;
          result: RaceSummaryResult;
        }>
      ).detail;
      if (detail.idempotency_key !== summary.idempotency_key) return;
      setAchievements(detail.result.new_achievements);
      setXpEarned(detail.result.progression?.xp_earned_this_race ?? 0);
      setSyncStatus('saved');
    };
    window.addEventListener('training-result-synced', handleSynced);
    return () => window.removeEventListener('training-result-synced', handleSynced);
  }, [summary.idempotency_key]);

  function retry() {
    setSyncStatus('pending');
    if (syncStatus === 'queued' && navigator.onLine) {
      window.dispatchEvent(new Event('online'));
      return;
    }
    void (async () => {
      try {
        await doSync();
      } catch {
        setSyncStatus('error');
      }
    })();
  }

  const didLevelUp = currentLevel !== null && levelBefore !== null && currentLevel > levelBefore;

  useEffect(() => {
    if (didLevelUp) playSfx('levelup');
  }, [didLevelUp]); // intentional: playSfx is stable ref

  return (
    <div
      data-testid="page-results-screen"
      style={{ maxWidth: 640, margin: '0 auto', padding: tokens.spacing.xl }}
    >
      {didLevelUp && (
        <div
          role="status"
          aria-live="polite"
          style={{
            background: tokens.color.primary,
            color: tokens.color.textOnPrimary,
            borderRadius: tokens.radius.lg,
            padding: tokens.spacing.lg,
            marginBottom: tokens.spacing.lg,
            textAlign: 'center',
          }}
        >
          <p style={{ fontSize: 28, fontWeight: 900, margin: 0 }}>Level Up!</p>
          <p style={{ margin: `${tokens.spacing.xs}px 0 0` }}>You reached Level {currentLevel}!</p>
        </div>
      )}

      {achievements[toastIndex] && (
        <NotificationToast
          message={`Achievement: ${achievements[toastIndex].title}`}
          type="success"
          onClose={() => setToastIndex((i) => i + 1)}
        />
      )}

      <img
        src="/artwork/achievements.png"
        alt=""
        aria-hidden="true"
        style={{
          width: '100%',
          maxWidth: 640,
          borderRadius: tokens.radius.lg,
          display: 'block',
          margin: '0 auto 12px',
        }}
      />

      {achievements.length > 0 && (
        <div
          style={{
            display: 'flex',
            gap: tokens.spacing.md,
            flexWrap: 'wrap',
            marginBottom: tokens.spacing.lg,
          }}
        >
          {achievements.map((a) => (
            <div key={a.key} style={{ textAlign: 'center' }}>
              <img
                src={getBadgeUrl(a.key)}
                alt={a.title}
                style={{ width: 64, height: 64, borderRadius: '50%' }}
              />
              <div
                style={{
                  fontSize: 12,
                  color: tokens.color.textSecondary,
                  marginTop: tokens.spacing.xs,
                }}
              >
                {a.title}
              </div>
            </div>
          ))}
        </div>
      )}

      <h1 style={{ color: tokens.color.textPrimary, marginBottom: tokens.spacing.lg }}>
        {summary.mode === 'training' ? 'Training Complete' : 'Race Finished!'}
      </h1>

      <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: tokens.spacing.lg }}>
        <thead>
          <tr>
            {['Place', 'Runner', 'Distance', 'Correct', 'XP'].map((h) => (
              <th
                key={h}
                scope="col"
                style={{
                  textAlign: h === 'Place' || h === 'Runner' ? 'left' : 'right',
                  padding: tokens.spacing.sm,
                  borderBottom: `2px solid ${tokens.color.border}`,
                  color: tokens.color.textSecondary,
                  fontSize: 14,
                  fontWeight: 600,
                }}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {summary.participants.map((p, i) => {
            const isPlayer = p.avatar_id === playerAvatarId;
            return (
              <tr
                key={p.avatar_id}
                style={{ background: isPlayer ? `${tokens.color.primary}18` : 'transparent' }}
              >
                <th scope="row" style={{ padding: tokens.spacing.sm, fontWeight: 400 }}>
                  {p.position ?? '—'}
                </th>
                <td style={{ padding: tokens.spacing.sm, fontWeight: isPlayer ? 700 : 400 }}>
                  {isPlayer ? 'You' : `Runner ${i + 1}`}
                </td>
                <td style={{ padding: tokens.spacing.sm, textAlign: 'right' }}>
                  {p.total_distance}m
                </td>
                <td style={{ padding: tokens.spacing.sm, textAlign: 'right' }}>
                  {p.problems_correct}
                  {summary.mode === 'training' ? '' : '/8'}
                </td>
                <td
                  style={{
                    padding: tokens.spacing.sm,
                    textAlign: 'right',
                    color: tokens.color.success,
                    fontWeight: 700,
                  }}
                >
                  +{isPlayer ? xpEarned : 0}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {syncStatus === 'error' && (
        <div
          role="alert"
          style={{ color: tokens.color.error, marginBottom: tokens.spacing.md, fontSize: 14 }}
        >
          Couldn&apos;t save results.{' '}
          <button
            type="button"
            onClick={retry}
            style={{
              color: tokens.color.primary,
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              textDecoration: 'underline',
              fontSize: 14,
            }}
          >
            Retry
          </button>
        </div>
      )}
      {syncStatus === 'queued' && (
        <p role="status" aria-live="polite" style={{ marginBottom: tokens.spacing.md }}>
          Training results are saved on this device and will sync when online.
        </p>
      )}

      <div style={{ display: 'flex', gap: tokens.spacing.md, flexWrap: 'wrap' }}>
        <Button variant="primary" onClick={() => void navigate('/race/setup')}>
          Race Again
        </Button>
        {championshipId && (
          <Button
            variant="secondary"
            onClick={() => void navigate(`/championship/${championshipId}`)}
          >
            View Championship
          </Button>
        )}
        <Button variant="secondary" onClick={() => void navigate('/')}>
          Home
        </Button>
      </div>
    </div>
  );
}
