import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { listAvatars } from '../engine/avatar/avatarApi';
import type { AvatarListItem } from '../engine/avatar/types';
import { createChampionship } from '../engine/race/championshipApi';
import type { RaceMode } from '../engine/race/types';
import type { Operation, Tier, TierConfig } from '../engine/math/types';
import { createRaceSession } from '../features/race/raceSessionApi';
import { fetchTier6Settings, saveTier6Settings } from '../features/race/tier6SettingsApi';
import { fetchPlayerStats } from '../features/statistics/statisticsApi';
import {
  cacheChildData,
  getCachedChildData,
  type CachedChildData,
  type CachedTrainingSession,
} from '../infrastructure/offline/offlineStore';
import { useAuth } from '../infrastructure/auth/AuthContext';
import { useLocale } from '../infrastructure/localization/LocaleContext';
import type { TranslationKey } from '../infrastructure/localization/catalogs';
import { translateAvatarSpecies } from '../infrastructure/localization/formatters';
import { Button } from '../shared/components/Button';
import { LoadingSpinner } from '../shared/components/LoadingSpinner';
import { useOffline } from '../shared/hooks/useOffline';
import { useSfxPlayer } from '../shared/hooks/useSfxPlayer';
import tokens from '../shared/tokens';

interface SetupRouteState {
  continueChampionshipId?: string;
  continueRaceIndex?: number;
}

const MODES: Array<{ mode: RaceMode; label: TranslationKey; defaultOpponents: number }> = [
  { mode: 'quick', label: 'Quick Race', defaultOpponents: 3 },
  { mode: 'championship', label: 'Championship', defaultOpponents: 3 },
  { mode: 'training', label: 'Training', defaultOpponents: 0 },
  { mode: 'duel', label: 'Duel', defaultOpponents: 1 },
];
const OPERATIONS: Operation[] = ['addition', 'subtraction', 'multiplication', 'division'];

export default function RaceSetupPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const routeState = (location.state ?? {}) as SetupRouteState;
  const { account, activeChildId } = useAuth();
  const { t } = useLocale();

  const [avatars, setAvatars] = useState<AvatarListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState<RaceMode>(
    routeState.continueChampionshipId ? 'championship' : 'quick',
  );
  const [tier, setTier] = useState<Tier>(1);
  const [customTierConfig, setCustomTierConfig] = useState<TierConfig>({
    tier: 6,
    operations: ['addition'],
    minOperand: 1,
    maxOperand: 20,
  });
  const [tier6SettingsSaved, setTier6SettingsSaved] = useState(false);
  const [savingTier6Settings, setSavingTier6Settings] = useState(false);
  const [tier6SettingsError, setTier6SettingsError] = useState<TranslationKey | null>(null);
  const [opponentCount, setOpponentCount] = useState(3);
  const [champRaces, setChampRaces] = useState(3);
  const [selectedAvatarId, setSelectedAvatarId] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [cachedChildData, setCachedChildData] = useState<CachedChildData | null>(null);
  const [offlineError, setOfflineError] = useState<TranslationKey | null>(null);
  const continueChampionshipId = routeState.continueChampionshipId;
  const continueRaceIndex = routeState.continueRaceIndex ?? 0;
  const isOffline = useOffline();
  const { playSfx } = useSfxPlayer();

  useEffect(() => {
    if (!account?.id) return;
    let cancelled = false;
    void fetchTier6Settings(account.id)
      .then((saved) => {
        if (cancelled) return;
        if (saved) {
          setCustomTierConfig(saved);
          setTier6SettingsSaved(true);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setTier6SettingsError('Saved Tier 6 settings could not be loaded.');
        }
      });
    return () => {
      cancelled = true;
    };
  }, [account?.id]);

  useEffect(() => {
    if (!activeChildId) void navigate('/child-profiles', { replace: true });
  }, [activeChildId, navigate]);

  useEffect(() => {
    if (isOffline) setMode('training');
  }, [isOffline]);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        if (isOffline) {
          if (!activeChildId) throw new Error('Select a child profile before Training.');
          const cached = await getCachedChildData(activeChildId);
          const published = cached?.avatars.filter((avatar) => avatar.status === 'published') ?? [];
          if (!cached || published.length === 0 || !cached.training_session) {
            throw new Error('No saved avatar or offline Training session is available.');
          }
          if (!cancelled) {
            setCachedChildData(cached);
            setAvatars(published);
            setSelectedAvatarId(cached.training_session.avatar_id);
          }
          return;
        }

        const published = (await listAvatars()).filter((avatar) => avatar.status === 'published');
        if (published.length === 0) {
          void navigate('/avatars/new', { replace: true });
          return;
        }
        const selected = published[0];
        if (!cancelled) {
          setAvatars(published);
          setSelectedAvatarId(selected.avatar_id);
        }

        if (!activeChildId) return;
        const existing = await getCachedChildData(activeChildId).catch(() => null);
        let trainingSession: CachedTrainingSession | null = existing?.training_session ?? null;
        if (!trainingSession) {
          try {
            const session = await createRaceSession({
              mode: 'training',
              tier: 1,
              avatar_id: selected.avatar_id,
              opponent_count: 0,
            });
            trainingSession = {
              ...session,
              tier: 1,
              avatar_id: selected.avatar_id,
              avatar_species: selected.species,
            };
          } catch {
            trainingSession = null;
          }
        }

        let statistics = existing?.statistics ?? null;
        try {
          statistics = await fetchPlayerStats();
        } catch (error) {
          if (!cancelled) setOfflineError('Statistics could not be refreshed for offline use.');
        }
        const data: CachedChildData = {
          child_profile_id: activeChildId,
          avatars: published,
          statistics,
          training_session: trainingSession,
        };
        await cacheChildData(data);
        if (!cancelled) {
          setCachedChildData(data);
          if (!trainingSession) {
            setOfflineError('Offline Training is not ready. You can still play while online.');
          }
        }
      } catch (error) {
        if (!cancelled) {
          const message =
            error instanceof Error &&
            (error.message === 'Select a child profile before Training.' ||
              error.message === 'No saved avatar or offline Training session is available.')
              ? error.message
              : 'Could not load saved child data.';
          setOfflineError(message);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [activeChildId, isOffline, navigate]);

  function handleModeChange(m: RaceMode) {
    setMode(m);
    setOpponentCount(MODES.find((x) => x.mode === m)?.defaultOpponents ?? 0);
  }

  async function handleSaveTier6Settings(): Promise<void> {
    if (!account?.id || savingTier6Settings) return;
    setSavingTier6Settings(true);
    setTier6SettingsError(null);
    try {
      const saved = await saveTier6Settings(account.id, customTierConfig);
      setCustomTierConfig(saved);
      setTier6SettingsSaved(true);
    } catch {
      setTier6SettingsError('Settings could not be saved.');
    } finally {
      setSavingTier6Settings(false);
    }
  }

  async function handleStart() {
    if (!selectedAvatarId || starting) return;
    playSfx('ui_avatar_select');
    setStarting(true);
    try {
      const cachedTraining =
        mode === 'training' ? (cachedChildData?.training_session ?? null) : null;
      const sessionTier = isOffline && mode === 'training' ? (cachedTraining?.tier ?? 1) : tier;
      let championship_id = continueChampionshipId;
      let raceIndex = continueRaceIndex;

      if (mode === 'championship' && !championship_id) {
        const champ = await createChampionship(champRaces);
        championship_id = champ.championship_id;
        raceIndex = champ.races_completed;
        localStorage.setItem('activeChampionshipId', championship_id);
      }

      const raceAvatarId = cachedTraining?.avatar_id ?? selectedAvatarId;
      const session =
        isOffline && mode === 'training' && cachedTraining
          ? cachedTraining
          : await createRaceSession({
              mode,
              tier: sessionTier,
              avatar_id: raceAvatarId,
              opponent_count: opponentCount,
              championship_id,
            });
      if (isOffline && mode === 'training' && activeChildId && cachedChildData) {
        const updated = { ...cachedChildData, training_session: null };
        await cacheChildData(updated);
        setCachedChildData(updated);
      }

      void navigate(`/race/${session.race_id}`, {
        state: {
          mode,
          tier: sessionTier,
          ...(sessionTier === 6 ? { customTierConfig } : {}),
          seed: session.seed,
          avatarId: raceAvatarId,
          avatarSpecies:
            cachedTraining?.avatar_species ??
            avatars.find((a) => a.avatar_id === raceAvatarId)?.species ??
            '',
          opponentCount,
          childProfileId: activeChildId,
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
      {loading && <LoadingSpinner message={t('Loading your avatars…')} />}
      {!loading && (
        <>
          <h1 style={{ color: tokens.color.textPrimary, marginBottom: tokens.spacing.lg }}>
            {t('Race Setup')}
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
              {t('Mode')}
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
                    onMouseEnter={disabledByOffline ? undefined : () => playSfx('ui_card_select')}
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
                    {t(m.label)}
                    {disabledByOffline ? ` (${t('offline')})` : ''}
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
                {t('Number of Races')}
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
                    {t('{{races}} races', { races: n })}
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
                {t('Opponents')}
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
              {t('Difficulty (Tier 1 = easiest)')}
            </label>
            <select
              id="tier-select"
              value={
                isOffline && mode === 'training'
                  ? (cachedChildData?.training_session?.tier ?? 1)
                  : tier
              }
              disabled={isOffline && mode === 'training'}
              onChange={(e) => setTier(Number(e.target.value) as Tier)}
              style={{
                padding: tokens.spacing.sm,
                borderRadius: tokens.radius.sm,
                border: `1px solid ${tokens.color.border}`,
                fontSize: 16,
              }}
            >
              {([1, 2, 3, 4, 5, 6] as Tier[]).map((tierOption) => (
                <option key={tierOption} value={tierOption}>
                  {t('Tier {{tier}}', { tier: tierOption })}
                </option>
              ))}
            </select>
          </section>

          {tier === 6 && (
            <fieldset style={{ marginBottom: tokens.spacing.lg }}>
              <legend>{t('Custom Tier 6 settings')}</legend>
              <p>{t('Select one or more operations and an operand range from 1 to 100.')}</p>
              {OPERATIONS.map((operation) => (
                <label key={operation} style={{ display: 'block' }}>
                  <input
                    type="checkbox"
                    checked={customTierConfig.operations.includes(operation)}
                    onChange={(event) => {
                      setTier6SettingsSaved(false);
                      setCustomTierConfig((current) => ({
                        ...current,
                        operations: event.target.checked
                          ? [...current.operations, operation]
                          : current.operations.filter((item) => item !== operation),
                      }));
                    }}
                  />{' '}
                  {t(operation)}
                </label>
              ))}
              <label>
                {t('Minimum operand')}
                <input
                  type="number"
                  min={1}
                  max={100}
                  value={customTierConfig.minOperand}
                  onChange={(event) => {
                    setTier6SettingsSaved(false);
                    setCustomTierConfig((current) => ({
                      ...current,
                      minOperand: Number(event.target.value),
                    }));
                  }}
                />
              </label>
              <label>
                {t('Maximum operand')}
                <input
                  type="number"
                  min={1}
                  max={100}
                  value={customTierConfig.maxOperand}
                  onChange={(event) => {
                    setTier6SettingsSaved(false);
                    setCustomTierConfig((current) => ({
                      ...current,
                      maxOperand: Number(event.target.value),
                    }));
                  }}
                />
              </label>
              <Button
                variant="secondary"
                disabled={
                  savingTier6Settings ||
                  customTierConfig.operations.length === 0 ||
                  customTierConfig.minOperand < 1 ||
                  customTierConfig.minOperand > customTierConfig.maxOperand ||
                  customTierConfig.maxOperand > 100
                }
                onClick={() => void handleSaveTier6Settings()}
              >
                {savingTier6Settings ? t('Saving…') : t('Save Tier 6 settings')}
              </Button>
              {tier6SettingsSaved && <p>{t('Tier 6 settings saved.')}</p>}
              {tier6SettingsError && <p role="alert">{t(tier6SettingsError)}</p>}
            </fieldset>
          )}

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
                {t('Racing as')}
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
                    {a.name ?? translateAvatarSpecies(a.species, t)}
                  </option>
                ))}
              </select>
            </section>
          )}

          {offlineError && (
            <p role="alert" style={{ color: tokens.color.error, marginBottom: tokens.spacing.md }}>
              {t(offlineError)}
            </p>
          )}
          <div style={{ width: '100%' }}>
            <Button
              variant="primary"
              disabled={
                !selectedAvatarId ||
                starting ||
                (isOffline && !cachedChildData?.training_session) ||
                (tier === 6 && !tier6SettingsSaved) ||
                (tier === 6 &&
                  (customTierConfig.operations.length === 0 ||
                    customTierConfig.minOperand < 1 ||
                    customTierConfig.minOperand > customTierConfig.maxOperand ||
                    customTierConfig.maxOperand > 100))
              }
              onClick={() => void handleStart()}
            >
              {starting ? t('Setting up…') : t('Start Race')}
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
