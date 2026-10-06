import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { recordChampionshipRace } from '../engine/race/championshipApi';
import { postRaceSummary } from '../engine/race/raceApi';
import type { RaceSummary } from '../engine/race/types';
import type { Achievement } from '../engine/achievements/types';
import { fetchProgression } from '../features/race/progressionApi';
import { Button } from '../shared/components/Button';
import { NotificationToast } from '../shared/components/NotificationToast';
import tokens from '../shared/tokens';

interface ResultsRouteState {
  summary: RaceSummary;
  playerAvatarId: string;
  championshipId?: string;
  raceIndex?: number;
}

type SyncStatus = 'pending' | 'saved' | 'error';

function computeLevel(totalXp: number): number {
  return Math.floor(Math.sqrt(totalXp / 100));
}

export default function ResultsScreenPage() {
  const location = useLocation();
  const routeState = location.state as ResultsRouteState | null;
  if (!routeState) return <div data-testid="page-results-screen" />;
  return <ResultsScreen routeState={routeState} />;
}

function ResultsScreen({ routeState }: { routeState: ResultsRouteState }) {
  const navigate = useNavigate();
  const { summary, playerAvatarId, championshipId, raceIndex } = routeState;

  const [syncStatus, setSyncStatus] = useState<SyncStatus>('pending');
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [toastIndex, setToastIndex] = useState(0);
  const [currentLevel, setCurrentLevel] = useState<number | null>(null);
  const [levelBefore, setLevelBefore] = useState<number | null>(null);

  const playerEntry = summary.participants.find((p) => p.avatar_id === playerAvatarId);

  async function doSync() {
    const result = await postRaceSummary(summary);
    setAchievements(result.new_achievements);

    if (championshipId !== undefined && raceIndex !== undefined) {
      await recordChampionshipRace(
        championshipId,
        summary.race_id,
        raceIndex,
        summary.participants.map((p) => ({
          avatar_id: p.avatar_id,
          is_player: p.avatar_id === playerAvatarId,
          finishing_position: p.position ?? 1,
        })),
      );
    }

    const progression = await fetchProgression();
    setCurrentLevel(progression.current_level);
    if (playerEntry) {
      setLevelBefore(computeLevel(progression.total_xp - playerEntry.xp_earned));
    }
    setSyncStatus('saved');
  }

  useEffect(() => {
    let cancelled = false;
    doSync().catch(() => { if (!cancelled) setSyncStatus('error'); });
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function retry() {
    setSyncStatus('pending');
    doSync().catch(() => setSyncStatus('error'));
  }

  const didLevelUp = currentLevel !== null && levelBefore !== null && currentLevel > levelBefore;

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

      <h1 style={{ color: tokens.color.textPrimary, marginBottom: tokens.spacing.lg }}>
        {summary.mode === 'training' ? 'Training Complete' : 'Race Finished!'}
      </h1>

      <table
        style={{ width: '100%', borderCollapse: 'collapse', marginBottom: tokens.spacing.lg }}
      >
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
                <td style={{ padding: tokens.spacing.sm, textAlign: 'right' }}>{p.total_distance}m</td>
                <td style={{ padding: tokens.spacing.sm, textAlign: 'right' }}>{p.problems_correct}/8</td>
                <td style={{ padding: tokens.spacing.sm, textAlign: 'right', color: tokens.color.success, fontWeight: 700 }}>
                  +{p.xp_earned}
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
            style={{ color: tokens.color.primary, background: 'none', border: 'none', cursor: 'pointer', textDecoration: 'underline', fontSize: 14 }}
          >
            Retry
          </button>
        </div>
      )}

      <div style={{ display: 'flex', gap: tokens.spacing.md, flexWrap: 'wrap' }}>
        <Button variant="primary" onClick={() => void navigate('/race/setup')}>Race Again</Button>
        {championshipId && (
          <Button variant="secondary" onClick={() => void navigate(`/championship/${championshipId}`)}>
            View Championship
          </Button>
        )}
        <Button variant="secondary" onClick={() => void navigate('/')}>Home</Button>
      </div>
    </div>
  );
}
