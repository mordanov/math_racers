import { useEffect, useRef, useState } from 'react';
import { useBlocker, useLocation, useNavigate, useParams } from 'react-router-dom';
import { useRaceEngine } from '../engine/race/hooks/useRaceEngine';
import { MAX_TRACK_DISTANCE, OBSTACLE_COUNT } from '../engine/race/constants';
import { PERSONALITIES } from '../engine/race/personalities';
import type { ParticipantConfig, RaceConfig, RaceMode } from '../engine/race/types';
import type { Tier } from '../engine/math/types';
import { ConfirmDialog } from '../shared/components/ConfirmDialog';
import { useAudioManager } from '../shared/hooks/useAudioManager';
import { useAmbienceManager } from '../shared/hooks/useAmbienceManager';
import { useSfxPlayer } from '../shared/hooks/useSfxPlayer';
import { useVoicePlayer } from '../shared/hooks/useVoicePlayer';
import type { Species } from '../shared/hooks/useVoicePlayer';
import { useReducedMotion } from '../shared/hooks/useReducedMotion';
import tokens from '../shared/tokens';

interface RaceScreenRouteState {
  mode: RaceMode;
  tier: Tier;
  seed: number;
  avatarId: string;
  avatarSpecies: string;
  opponentCount: number;
  championshipId?: string;
  raceIndex: number;
}

function buildParticipants(playerAvatarId: string, opponentCount: number): ParticipantConfig[] {
  const player: ParticipantConfig = { runnerId: 'player', isHuman: true, avatarId: playerAvatarId };
  const ai: ParticipantConfig[] = Array.from({ length: opponentCount }, (_, i) => ({
    runnerId: `ai-${i + 1}`,
    isHuman: false,
    avatarId: `ai-${i + 1}`,
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
    mode: routeState.mode,
    participants: buildParticipants(routeState.avatarId, routeState.opponentCount),
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
    getSummary,
  } = useRaceEngine(config);

  const [countdownNum, setCountdownNum] = useState(3);
  const [answerInput, setAnswerInput] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);
  const { playMusic, stopMusic } = useAudioManager();
  const { playSfx } = useSfxPlayer();
  const { triggerAmbience } = useAmbienceManager();
  const { playVoice } = useVoicePlayer((routeState.avatarSpecies as Species) || null);
  const reduced = useReducedMotion();

  const blocker = useBlocker(state === 'RACING');

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
        championshipId: routeState.championshipId,
        raceIndex: routeState.raceIndex,
      },
      replace: true,
    });
  }, [state]); // intentionally omits stable refs: navigate, getSummary, routeState

  function handleSubmit() {
    if (state !== 'RACING') return;
    const problem = problemSet?.problems[currentObstacle];
    if (!problem) return;
    const parsed = parseInt(answerInput, 10);
    const isCorrect = !isNaN(parsed) && parsed === problem.answer;
    submitAnswer({ isCorrect });
    if (isCorrect) {
      playSfx('correct');
      triggerAmbience('cheer');
      playVoice('happy');
    } else {
      playSfx('incorrect');
      playVoice('surprised');
    }
    setAnswerInput('');
  }

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
          {state === 'COUNTDOWN' ? (countdownNum > 0 ? String(countdownNum) : 'GO!') : '…'}
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
        backgroundImage: 'url(/stadium.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center bottom',
        backgroundRepeat: 'no-repeat',
        minHeight: '100vh',
      }}
    >
      <ConfirmDialog
        open={blocker.state === 'blocked'}
        title="Leave Race?"
        message="Your progress will be lost if you leave now."
        confirmLabel="Leave"
        onConfirm={() => blocker.proceed?.()}
        onClose={() => blocker.reset?.()}
      />

      {/* Runner track */}
      <div role="list" style={{ marginBottom: tokens.spacing.lg }} aria-label="Race track">
        {runners.map((runner) => {
          const pct = Math.min(100, (runner.totalDistanceMetres / MAX_TRACK_DISTANCE) * 100);
          return (
            <div
              key={runner.runnerId}
              role="listitem"
              aria-label={`${runner.isHuman ? 'You' : `CPU ${runner.runnerId.replace('ai-', '')}`}: ${runner.totalDistanceMetres}m`}
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
                  height: 24,
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
                    width: 20,
                    height: 20,
                    borderRadius: '50%',
                    background: runner.isHuman ? tokens.color.primary : tokens.color.textSecondary,
                    transition: reduced ? undefined : `left ${tokens.animation.micro} ease-out`,
                  }}
                />
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

      {/* Timer bar */}
      {state === 'RACING' && (
        <div style={{ marginBottom: tokens.spacing.md }}>
          <div
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
                width: `${Math.min(100, (obstacleClockMs / 8000) * 100)}%`,
                background:
                  obstacleClockMs < 2000
                    ? tokens.color.success
                    : obstacleClockMs < 4000
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
              fontSize: 48,
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
            aria-label={`What is ${problem.operand_a} ${OP_SYMBOL[problem.operation] ?? '?'} ${problem.operand_b}?`}
            value={answerInput}
            onChange={(e) => setAnswerInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleSubmit();
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
              onClick={handleSubmit}
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
              Submit
            </button>
          </div>
          <p
            style={{
              color: tokens.color.textSecondary,
              marginTop: tokens.spacing.sm,
              fontSize: 14,
            }}
          >
            Obstacle {currentObstacle + 1} of {OBSTACLE_COUNT}
          </p>
        </div>
      )}

      {state === 'RACING' && (
        <button
          type="button"
          onClick={() => void navigate('/race/setup')}
          style={{
            background: 'none',
            border: 'none',
            color: tokens.color.textSecondary,
            cursor: 'pointer',
            fontSize: 14,
          }}
        >
          Leave Race
        </button>
      )}
    </div>
  );
}
