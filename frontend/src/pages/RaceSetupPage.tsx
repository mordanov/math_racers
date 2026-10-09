import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { listAvatars } from '../engine/avatar/avatarApi';
import type { AvatarListItem } from '../engine/avatar/types';
import { createChampionship } from '../engine/race/championshipApi';
import type { RaceMode } from '../engine/race/types';
import type { Tier } from '../engine/math/types';
import { createRaceSession } from '../features/race/raceSessionApi';
import { Button } from '../shared/components/Button';
import { LoadingSpinner } from '../shared/components/LoadingSpinner';
import { useOffline } from '../shared/hooks/useOffline';
import tokens from '../shared/tokens';

interface SetupRouteState {
  continueChampionshipId?: string;
  continueRaceIndex?: number;
}

const MODES: Array<{ mode: RaceMode; label: string; defaultOpponents: number }> = [
  { mode: 'quick', label: 'Quick Race', defaultOpponents: 3 },
  { mode: 'championship', label: 'Championship', defaultOpponents: 3 },
  { mode: 'training', label: 'Training', defaultOpponents: 0 },
  { mode: 'duel', label: 'Duel', defaultOpponents: 1 },
];

export default function RaceSetupPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const routeState = (location.state ?? {}) as SetupRouteState;

  const [avatars, setAvatars] = useState<AvatarListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState<RaceMode>(
    routeState.continueChampionshipId ? 'championship' : 'quick',
  );
  const [tier, setTier] = useState<Tier>(1);
  const [opponentCount, setOpponentCount] = useState(3);
  const [champRaces, setChampRaces] = useState(3);
  const [selectedAvatarId, setSelectedAvatarId] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const continueChampionshipId = routeState.continueChampionshipId;
  const continueRaceIndex = routeState.continueRaceIndex ?? 0;
  const isOffline = useOffline();

  useEffect(() => {
    if (isOffline) setMode('training');
  }, [isOffline]);

  useEffect(() => {
    listAvatars()
      .then((list) => {
        const published = list.filter((a) => a.status === 'published');
        if (published.length === 0) {
          void navigate('/avatars/new', { replace: true });
          return;
        }
        setAvatars(published);
        setSelectedAvatarId(published[0].avatar_id);
      })
      .catch(() => void navigate('/avatars/new', { replace: true }))
      .finally(() => setLoading(false));
  }, [navigate]);

  function handleModeChange(m: RaceMode) {
    setMode(m);
    setOpponentCount(MODES.find((x) => x.mode === m)?.defaultOpponents ?? 0);
  }

  async function handleStart() {
    if (!selectedAvatarId || starting) return;
    setStarting(true);
    try {
      let championship_id = continueChampionshipId;
      let raceIndex = continueRaceIndex;

      if (mode === 'championship' && !championship_id) {
        const champ = await createChampionship(champRaces);
        championship_id = champ.championship_id;
        raceIndex = champ.races_completed;
        localStorage.setItem('activeChampionshipId', championship_id);
      }

      const session = await createRaceSession({
        mode,
        tier,
        avatar_id: selectedAvatarId,
        opponent_count: opponentCount,
        championship_id,
      });

      void navigate(`/race/${session.race_id}`, {
        state: {
          mode,
          tier,
          seed: session.seed,
          avatarId: selectedAvatarId,
          avatarSpecies: avatars.find((a) => a.avatar_id === selectedAvatarId)?.species ?? '',
          opponentCount,
          championshipId: championship_id,
          raceIndex,
        },
      });
    } finally {
      setStarting(false);
    }
  }

  return (
    <div
      data-testid="page-race-setup"
      style={{ maxWidth: 480, margin: '0 auto', padding: tokens.spacing.xl }}
    >
      {loading && <LoadingSpinner message="Loading your avatars…" />}
      {!loading && (
        <>
          <h1 style={{ color: tokens.color.textPrimary, marginBottom: tokens.spacing.lg }}>
            Race Setup
          </h1>

          <section aria-labelledby="mode-heading" style={{ marginBottom: tokens.spacing.lg }}>
            <h2
              id="mode-heading"
              style={{
                fontSize: 18,
                color: tokens.color.textSecondary,
                marginBottom: tokens.spacing.sm,
              }}
            >
              Mode
            </h2>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: tokens.spacing.sm }}>
              {MODES.map((m) => {
                const disabledByOffline = isOffline && m.mode !== 'training';
                return (
                  <button
                    key={m.mode}
                    type="button"
                    aria-pressed={mode === m.mode}
                    disabled={disabledByOffline}
                    onClick={() => handleModeChange(m.mode)}
                    style={{
                      padding: `${tokens.spacing.sm}px ${tokens.spacing.md}px`,
                      borderRadius: tokens.radius.md,
                      border: `2px solid ${mode === m.mode ? tokens.color.primary : tokens.color.border}`,
                      background: mode === m.mode ? tokens.color.primary : tokens.color.surface,
                      color:
                        mode === m.mode ? tokens.color.textOnPrimary : tokens.color.textPrimary,
                      cursor: disabledByOffline ? 'not-allowed' : 'pointer',
                      fontWeight: 600,
                      opacity: disabledByOffline ? 0.5 : 1,
                    }}
                  >
                    {m.label}
                    {disabledByOffline ? ' (offline)' : ''}
                  </button>
                );
              })}
            </div>
          </section>

          {mode === 'championship' && !continueChampionshipId && (
            <section style={{ marginBottom: tokens.spacing.lg }}>
              <label
                htmlFor="champ-races"
                style={{
                  display: 'block',
                  color: tokens.color.textSecondary,
                  marginBottom: tokens.spacing.xs,
                }}
              >
                Number of Races
              </label>
              <select
                id="champ-races"
                value={champRaces}
                onChange={(e) => setChampRaces(Number(e.target.value))}
                style={{
                  padding: tokens.spacing.sm,
                  borderRadius: tokens.radius.sm,
                  border: `1px solid ${tokens.color.border}`,
                  fontSize: 16,
                }}
              >
                {[3, 5, 7].map((n) => (
                  <option key={n} value={n}>
                    {n} races
                  </option>
                ))}
              </select>
            </section>
          )}

          {mode === 'quick' && (
            <section style={{ marginBottom: tokens.spacing.lg }}>
              <label
                htmlFor="opponent-count"
                style={{
                  display: 'block',
                  color: tokens.color.textSecondary,
                  marginBottom: tokens.spacing.xs,
                }}
              >
                Opponents
              </label>
              <select
                id="opponent-count"
                value={opponentCount}
                onChange={(e) => setOpponentCount(Number(e.target.value))}
                style={{
                  padding: tokens.spacing.sm,
                  borderRadius: tokens.radius.sm,
                  border: `1px solid ${tokens.color.border}`,
                  fontSize: 16,
                }}
              >
                {[1, 2, 3, 4].map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </section>
          )}

          <section style={{ marginBottom: tokens.spacing.lg }}>
            <label
              htmlFor="tier-select"
              style={{
                display: 'block',
                color: tokens.color.textSecondary,
                marginBottom: tokens.spacing.xs,
              }}
            >
              Difficulty (Tier 1 = easiest)
            </label>
            <select
              id="tier-select"
              value={tier}
              onChange={(e) => setTier(Number(e.target.value) as Tier)}
              style={{
                padding: tokens.spacing.sm,
                borderRadius: tokens.radius.sm,
                border: `1px solid ${tokens.color.border}`,
                fontSize: 16,
              }}
            >
              {([1, 2, 3, 4, 5] as Tier[]).map((t) => (
                <option key={t} value={t}>
                  Tier {t}
                </option>
              ))}
            </select>
          </section>

          {avatars.length > 1 && (
            <section style={{ marginBottom: tokens.spacing.lg }}>
              <label
                htmlFor="avatar-select"
                style={{
                  display: 'block',
                  color: tokens.color.textSecondary,
                  marginBottom: tokens.spacing.xs,
                }}
              >
                Racing as
              </label>
              <select
                id="avatar-select"
                value={selectedAvatarId ?? ''}
                onChange={(e) => setSelectedAvatarId(e.target.value)}
                style={{
                  padding: tokens.spacing.sm,
                  borderRadius: tokens.radius.sm,
                  border: `1px solid ${tokens.color.border}`,
                  fontSize: 16,
                }}
              >
                {avatars.map((a) => (
                  <option key={a.avatar_id} value={a.avatar_id}>
                    {a.name ?? a.species}
                  </option>
                ))}
              </select>
            </section>
          )}

          <div style={{ width: '100%' }}>
            <Button
              variant="primary"
              disabled={!selectedAvatarId || starting}
              onClick={() => void handleStart()}
            >
              {starting ? 'Setting up…' : 'Start Race'}
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
