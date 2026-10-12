import { useCallback, useEffect, useRef, useState } from 'react';
import { useBlocker, useLocation, useNavigate, useParams } from 'react-router-dom';
import { useRaceEngine } from '../engine/race/hooks/useRaceEngine';
import { submitRaceAnswer } from '../engine/race/raceApi';
import { MAX_TRACK_DISTANCE, OBSTACLE_COUNT } from '../engine/race/constants';
import { PERSONALITIES } from '../engine/race/personalities';
import type { ParticipantConfig, RaceConfig, RaceMode } from '../engine/race/types';
import {
  DEFAULT_PROBLEM_TIME_LIMIT_SECONDS,
  isValidProblemTimeLimitSeconds,
} from '../engine/race/problemTimeLimit';
import type { Tier, TierConfig } from '../engine/math/types';
import { ConfirmDialog } from '../shared/components/ConfirmDialog';
import { useAudioManager } from '../shared/hooks/useAudioManager';
import { useAmbienceManager } from '../shared/hooks/useAmbienceManager';
import { useSfxPlayer } from '../shared/hooks/useSfxPlayer';
import { useVoicePlayer } from '../shared/hooks/useVoicePlayer';
import type { Species } from '../shared/hooks/useVoicePlayer';
import { useReducedMotion } from '../shared/hooks/useReducedMotion';
import { useOffline } from '../shared/hooks/useOffline';
import { useLocale } from '../infrastructure/localization/LocaleContext';
import type { TranslationKey } from '../infrastructure/localization/catalogs';
import tokens from '../shared/tokens';

interface RaceScreenRouteState {
  mode: RaceMode;
  tier: Tier;
  customTierConfig?: TierConfig;
  seed: number;
  avatarId: string;
  avatarSpecies: string;
  opponentCount: number;
  childProfileId?: string;
  championshipId?: string;
  raceIndex: number;
  avatarPortraitUrl?: string;
  opponentPortraitUrls?: string[];
  problemTimeLimitSeconds?: number;
}

const FALLBACK_AVATARS = ['🏎️', '🦊', '🐻', '🐰', '🐼'];

function buildParticipants(
  playerAvatarId: string,
  opponentCount: number,
  playerPortraitUrl?: string,
  opponentPortraitUrls: string[] = [],
): ParticipantConfig[] {
  const player: ParticipantConfig = {
    runnerId: 'player',
    isHuman: true,
    avatarId: playerAvatarId,
    portraitUrl: playerPortraitUrl,
  };
  const ai: ParticipantConfig[] = Array.from({ length: opponentCount }, (_, i) => ({
    runnerId: `ai-${i + 1}`,
    isHuman: false,
    avatarId: `ai-${i + 1}`,
    portraitUrl: opponentPortraitUrls[i],
    personality: PERSONALITIES[i % PERSONALITIES.length],
  }));
  return [player, ...ai];
}

export default function RaceScreenPage() {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();
  const routeState = location.state as RaceScreenRouteState | null;

  if (!routeState || !id) return <div data-testid="page-race-screen" />;

  const config: RaceConfig = {
    raceId: id,
    seed: routeState.seed,
    tier: routeState.tier,
    customTierConfig: routeState.customTierConfig,
    mode: routeState.mode,
    participants: buildParticipants(
      routeState.avatarId,
      routeState.mode === 'training' ? 0 : routeState.opponentCount,
      routeState.avatarPortraitUrl,
      routeState.opponentPortraitUrls,
    ),
  };

  return <RaceScreen raceId={id} config={config} routeState={routeState} />;
}

const OP_SYMBOL: Record<string, string> = {
  addition: '+',
  subtraction: '−',
  multiplication: '×',
  division: '÷',
};

function RaceScreen({
  raceId,
  config,
  routeState,
}: {
  raceId: string;
  config: RaceConfig;
  routeState: RaceScreenRouteState;
}) {
  const navigate = useNavigate();
  const {
    state,
    obstacleClockMs,
    currentObstacle,
    runners,
    problemSet,
    startCountdown,
    startRacing,
    submitAnswer,
    forceComplete,
    getSummary,
  } = useRaceEngine(config);

  const [countdownNum, setCountdownNum] = useState(3);
  const [answerInput, setAnswerInput] = useState('');
  const [submittingAnswer, setSubmittingAnswer] = useState(false);
  const [answerError, setAnswerError] = useState<TranslationKey | null>(null);
  const [failedPortraits, setFailedPortraits] = useState<Set<string>>(() => new Set());
  const inputRef = useRef<HTMLInputElement>(null);
  const submissionInFlightRef = useRef(false);
  const timedOutObstacleRef = useRef<number | null>(null);
  const answeredObstacleRef = useRef<number | null>(null);
  const pendingAnswerRef = useRef<{ obstacleIndex: number; answer: string } | null>(null);
  const latestObstacleClockRef = useRef(obstacleClockMs);
  latestObstacleClockRef.current = obstacleClockMs;
  const { playMusic, stopMusic } = useAudioManager();
  const { playSfx } = useSfxPlayer();
  const { triggerAmbience } = useAmbienceManager();
  const { playVoice } = useVoicePlayer((routeState.avatarSpecies as Species) || null);
  const reduced = useReducedMotion();
  const isOffline = useOffline();
  const { t } = useLocale();
  const configuredTimeLimit = routeState.problemTimeLimitSeconds;
  const problemTimeLimitSeconds = isValidProblemTimeLimitSeconds(configuredTimeLimit ?? 0)
    ? configuredTimeLimit!
    : DEFAULT_PROBLEM_TIME_LIMIT_SECONDS;
  const problemTimeLimitMs = problemTimeLimitSeconds * 1000;

  const blocker = useBlocker(state === 'RACING' && config.mode !== 'training');

  useEffect(() => {
    startCountdown();
    return () => stopMusic();
  }, []); // startCountdown/stopMusic are stable refs

  useEffect(() => {
    if (state === 'RACING') playMusic('race');
  }, [state]); // intentional: only start music when state transitions to RACING

  useEffect(() => {
    if (state !== 'COUNTDOWN') return;
    if (countdownNum > 0) {
      const t = setTimeout(() => {
        setCountdownNum((n) => n - 1);
        playSfx('countdown');
      }, 1000);
      return () => clearTimeout(t);
    }
    const t = setTimeout(startRacing, 800);
    return () => clearTimeout(t);
  }, [state, countdownNum, startRacing, playSfx]);

  useEffect(() => {
    if (state === 'RACING') inputRef.current?.focus();
  }, [state, currentObstacle]);

  useEffect(() => {
    if (state === 'RACING') playVoice('thinking');
  }, [state, currentObstacle]); // intentional: playVoice is stable ref

  useEffect(() => {
    if (state === 'RESULTS') triggerAmbience('applause');
  }, [state]); // intentional: triggerAmbience is a stable ref

  useEffect(() => {
    if (state !== 'RESULTS') return;
    void navigate(`/race/${raceId}/results`, {
      state: {
        summary: getSummary(),
        playerAvatarId: routeState.avatarId,
        avatarSpecies: routeState.avatarSpecies,
        childProfileId: routeState.childProfileId,
        championshipId: routeState.championshipId,
        raceIndex: routeState.raceIndex,
      },
      replace: true,
    });
  }, [state]); // intentionally omits stable refs: navigate, getSummary, routeState

  const handleSubmit = useCallback(async (): Promise<void> => {
    if (state !== 'RACING' || submittingAnswer || submissionInFlightRef.current) return;
    const problem = problemSet?.problems[currentObstacle];
    if (!problem) return;
    const pendingAnswer =
      pendingAnswerRef.current?.obstacleIndex === currentObstacle ? pendingAnswerRef.current : null;
    const timedOut =
      !pendingAnswer && config.mode !== 'training' && obstacleClockMs >= problemTimeLimitMs;
    const submittedAnswer = timedOut ? '' : (pendingAnswer?.answer ?? answerInput);
    if (timedOut) {
      timedOutObstacleRef.current = currentObstacle;
      setAnswerInput('');
    } else if (!pendingAnswer) {
      pendingAnswerRef.current = { obstacleIndex: currentObstacle, answer: submittedAnswer };
    }
    submissionInFlightRef.current = true;
    setSubmittingAnswer(true);
    setAnswerError(null);
    try {
      const serverAnswer = isOffline
        ? null
        : await submitRaceAnswer(raceId, currentObstacle, problem.operation, submittedAnswer);
      const result = submitAnswer({
        answer: submittedAnswer,
        ...(serverAnswer
          ? {
              isCorrect: serverAnswer.is_correct,
              responseTimeMs: serverAnswer.response_time_ms,
            }
          : {}),
      });
      if (result.isCorrect) {
        playSfx('correct');
        triggerAmbience('cheer');
        playVoice('happy');
      } else {
        playSfx('incorrect');
        playVoice('surprised');
      }
      answeredObstacleRef.current = currentObstacle;
      pendingAnswerRef.current = null;
      setAnswerInput('');
    } catch (error) {
      if (
        !timedOut &&
        pendingAnswerRef.current?.obstacleIndex === currentObstacle &&
        latestObstacleClockRef.current < problemTimeLimitMs
      ) {
        pendingAnswerRef.current = null;
      }
      setAnswerError('The answer could not be saved.');
    } finally {
      submissionInFlightRef.current = false;
      setSubmittingAnswer(false);
    }
  }, [
    answerInput,
    config.mode,
    currentObstacle,
    isOffline,
    obstacleClockMs,
    problemSet,
    problemTimeLimitMs,
    raceId,
    state,
    submitAnswer,
    submittingAnswer,
    playSfx,
    playVoice,
    triggerAmbience,
  ]);

  useEffect(() => {
    if (
      state !== 'RACING' ||
      config.mode === 'training' ||
      obstacleClockMs < problemTimeLimitMs ||
      timedOutObstacleRef.current === currentObstacle ||
      answeredObstacleRef.current === currentObstacle ||
      pendingAnswerRef.current?.obstacleIndex === currentObstacle ||
      submissionInFlightRef.current
    ) {
      return;
    }
    timedOutObstacleRef.current = currentObstacle;
    void handleSubmit();
  }, [config.mode, currentObstacle, handleSubmit, obstacleClockMs, problemTimeLimitMs, state]);

  const problem = problemSet?.problems[currentObstacle];
  const isCountdownPhase = state === 'IDLE' || state === 'LOBBY' || state === 'COUNTDOWN';

  if (isCountdownPhase) {
    return (
      <div
        data-testid="page-race-screen"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
        }}
      >
        <div
          role="status"
          aria-live="polite"
          style={{
            fontSize: 96,
            fontWeight: 900,
            color: tokens.color.primary,
            lineHeight: 1,
          }}
        >
          {state === 'COUNTDOWN' ? (countdownNum > 0 ? String(countdownNum) : t('GO!')) : '…'}
        </div>
      </div>
    );
  }

  return (
    <div
      data-testid="page-race-screen"
      style={{
        maxWidth: 640,
        margin: '0 auto',
        padding: tokens.spacing.xl,
        backgroundImage: 'url(/artwork/stadium.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center bottom',
        backgroundRepeat: 'no-repeat',
        minHeight: '100vh',
      }}
    >
      <ConfirmDialog
        open={blocker.state === 'blocked'}
        title={t('Leave Race?')}
        message={t('Your progress will be lost if you leave now.')}
        confirmLabel={t('Leave')}
        onConfirm={() => blocker.proceed?.()}
        onClose={() => blocker.reset?.()}
      />

      {/* Runner track */}
      {config.mode !== 'training' && (
        <div role="list" style={{ marginBottom: tokens.spacing.lg }} aria-label={t('Race track')}>
          {runners.map((runner) => {
            const pct = Math.min(100, (runner.totalDistanceMetres / MAX_TRACK_DISTANCE) * 100);
            const participant = config.participants.find(
              (candidate) => candidate.runnerId === runner.runnerId,
            );
            const runnerName = runner.isHuman
              ? t('You')
              : t('CPU {{number}}', { number: runner.runnerId.replace('ai-', '') });
            const avatarLabel = t('{{runner}} avatar', { runner: runnerName });
            const portraitUrl = participant?.portraitUrl;
            const portraitFailed = failedPortraits.has(runner.runnerId);
            const fallback =
              FALLBACK_AVATARS[
                runner.isHuman
                  ? 0
                  : Number(runner.runnerId.replace('ai-', '')) % FALLBACK_AVATARS.length
              ];
            return (
              <div
                key={runner.runnerId}
                role="listitem"
                aria-label={t('{{runner}}: {{distance}}m', {
                  runner: runnerName,
                  distance: runner.totalDistanceMetres,
                })}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: tokens.spacing.sm,
                  marginBottom: tokens.spacing.xs,
                }}
              >
                <span
                  aria-hidden="true"
                  style={{
                    width: 24,
                    fontSize: 12,
                    color: tokens.color.textSecondary,
                    textAlign: 'center',
                  }}
                >
                  {runner.isHuman ? '★' : runner.runnerId.replace('ai-', '')}
                </span>
                <div
                  style={{
                    flex: 1,
                    height: 32,
                    background: tokens.color.background,
                    borderRadius: 999,
                    border: `1px solid ${tokens.color.border}`,
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      position: 'absolute',
                      left: `${pct}%`,
                      top: '50%',
                      transform: 'translate(-50%, -50%)',
                      width: 30,
                      height: 30,
                      borderRadius: '50%',
                      background: tokens.color.surface,
                      transition: reduced ? undefined : `left ${tokens.animation.micro} ease-out`,
                      display: 'grid',
                      placeItems: 'center',
                      overflow: 'hidden',
                    }}
                  >
                    {portraitUrl && !portraitFailed ? (
                      <img
                        src={portraitUrl}
                        alt={avatarLabel}
                        onError={() =>
                          setFailedPortraits((current) => new Set(current).add(runner.runnerId))
                        }
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      />
                    ) : (
                      <span role="img" aria-label={avatarLabel} style={{ fontSize: 22 }}>
                        {fallback}
                      </span>
                    )}
                  </div>
                </div>
                <span
                  aria-hidden="true"
                  style={{
                    width: 40,
                    fontSize: 12,
                    color: tokens.color.textSecondary,
                    textAlign: 'right',
                  }}
                >
                  {runner.totalDistanceMetres}m
                </span>
              </div>
            );
          })}
        </div>
      )}

      {/* Timer bar */}
      {state === 'RACING' && config.mode !== 'training' && (
        <div style={{ marginBottom: tokens.spacing.md }}>
          <div style={{ marginBottom: tokens.spacing.xs, textAlign: 'right' }}>
            {Math.max(0, Math.ceil((problemTimeLimitMs - obstacleClockMs) / 1000))} {t('seconds')}
          </div>
          <div
            role="progressbar"
            aria-label={t('Time remaining')}
            aria-valuemin={0}
            aria-valuemax={problemTimeLimitSeconds}
            aria-valuenow={Math.min(problemTimeLimitSeconds, Math.floor(obstacleClockMs / 1000))}
            aria-valuetext={t('{{seconds}} seconds remaining', {
              seconds: Math.max(0, Math.ceil((problemTimeLimitMs - obstacleClockMs) / 1000)),
            })}
            style={{
              height: 8,
              borderRadius: 999,
              background: tokens.color.background,
              border: `1px solid ${tokens.color.border}`,
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                height: '100%',
                width: `${Math.min(100, (obstacleClockMs / problemTimeLimitMs) * 100)}%`,
                background:
                  obstacleClockMs < problemTimeLimitMs / 3
                    ? tokens.color.success
                    : obstacleClockMs < (problemTimeLimitMs * 2) / 3
                      ? tokens.color.warning
                      : tokens.color.error,
                transition: reduced ? undefined : 'width 0.1s linear',
              }}
            />
          </div>
        </div>
      )}

      {/* Problem card */}
      {state === 'RACING' && problem && (
        <div
          style={{
            background: tokens.color.surface,
            borderRadius: tokens.radius.lg,
            padding: tokens.spacing.lg,
            boxShadow: tokens.shadow.card,
            marginBottom: tokens.spacing.lg,
            textAlign: 'center',
          }}
        >
          <p
            style={{
              fontSize: tokens.fontSize.hero,
              fontWeight: 900,
              color: tokens.color.textPrimary,
              margin: `0 0 ${tokens.spacing.md}px`,
            }}
          >
            {problem.operand_a} {OP_SYMBOL[problem.operation] ?? '?'} {problem.operand_b} = ?
          </p>
          <input
            ref={inputRef}
            type="number"
            aria-label={t('What is {{first}} {{operator}} {{second}}?', {
              first: problem.operand_a,
              operator: OP_SYMBOL[problem.operation] ?? '?',
              second: problem.operand_b,
            })}
            value={answerInput}
            onChange={(e) => setAnswerInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') void handleSubmit();
            }}
            style={{
              fontSize: 32,
              width: 120,
              textAlign: 'center',
              border: `2px solid ${tokens.color.border}`,
              borderRadius: tokens.radius.md,
              padding: tokens.spacing.sm,
            }}
          />
          <div style={{ marginTop: tokens.spacing.md }}>
            <button
              type="button"
              onClick={() => void handleSubmit()}
              disabled={submittingAnswer}
              style={{
                padding: `${tokens.spacing.sm}px ${tokens.spacing.lg}px`,
                background: tokens.color.primary,
                color: tokens.color.textOnPrimary,
                borderRadius: tokens.radius.md,
                border: 'none',
                cursor: 'pointer',
                fontSize: 18,
                fontWeight: 700,
                minHeight: tokens.touchTarget,
              }}
            >
              {t('Submit')}
            </button>
          </div>
          {answerError && <p role="alert">{t(answerError)}</p>}
          <p
            style={{
              color: tokens.color.textSecondary,
              marginTop: tokens.spacing.sm,
              fontSize: 14,
            }}
          >
            {config.mode === 'training'
              ? t('Problems answered: {{count}}', { count: currentObstacle })
              : t('Obstacle {{current}} of {{total}}', {
                  current: currentObstacle + 1,
                  total: OBSTACLE_COUNT,
                })}
          </p>
        </div>
      )}

      {state === 'RACING' && (
        <button
          type="button"
          onClick={() => {
            if (config.mode === 'training') {
              forceComplete();
            } else {
              void navigate('/race/setup');
            }
          }}
          style={{
            background: 'none',
            border: 'none',
            color: tokens.color.textSecondary,
            cursor: 'pointer',
            fontSize: 14,
          }}
        >
          {config.mode === 'training' ? t('Finish Training') : t('Leave Race')}
        </button>
      )}
    </div>
  );
}
