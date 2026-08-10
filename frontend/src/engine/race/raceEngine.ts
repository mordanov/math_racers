import { generateProblemSet } from '../math/generator';
import { createRng } from '../math/rng';
import { simulateAiObstacle } from './aiRunner';
import { GameClock } from './clock';
import { OBSTACLE_COUNT } from './constants';
import { calculateMovement } from './movement';
import { RaceStateError, transition } from './stateMachine';
import type {
  ObstacleResult,
  ParticipantSummary,
  RaceConfig,
  RaceEngineState,
  RaceSummary,
  RaceState,
  RunnerState,
} from './types';

export class RaceSummaryError extends Error {
  constructor() {
    super('Race summary is only available in RESULTS state');
    this.name = 'RaceSummaryError';
  }
}

function makeRunner(runnerId: string, isHuman: boolean): RunnerState {
  return {
    runnerId,
    isHuman,
    totalDistanceMetres: 0,
    obstaclesCompleted: 0,
    obstacleResults: [],
    finishTime: null,
  };
}

export interface RaceEngine {
  transition(toState: RaceState): void;
  tick(timestamp: number): void;
  pause(): void;
  resume(): void;
  submitAnswer(input: { isCorrect: boolean }): ObstacleResult;
  getState(): RaceEngineState;
  getSummary(): RaceSummary;
}

export function createRaceEngine(config: RaceConfig): RaceEngine {
  let state: RaceState = 'IDLE';
  const clock = new GameClock();
  let startedAt: Date | null = null;
  let completedAt: Date | null = null;

  const problemSet = generateProblemSet(config.tier, config.seed, OBSTACLE_COUNT);
  const runners: RunnerState[] = config.participants.map((p) => makeRunner(p.runnerId, p.isHuman));

  const humanIdx = runners.findIndex((r) => r.isHuman);
  // Separate RNG for AI variance — offset by 1 to avoid colliding with problem seed
  const aiRng = createRng(config.seed + 1);

  function doTransition(toState: RaceState): void {
    transition(state, toState);
    state = toState;
    if (toState === 'RACING') {
      startedAt = new Date();
      clock.reset();
      clock.startObstacleClock();
    }
    if (toState === 'RESULTS') {
      completedAt = new Date();
    }
  }

  function submitAnswer(input: { isCorrect: boolean }): ObstacleResult {
    if (state !== 'RACING') {
      throw new RaceStateError(state, 'RACING');
    }
    const runner = runners[humanIdx];
    const obstacleIndex = runner.obstaclesCompleted;
    const responseTimeMs = clock.getObstacleMs();
    const { tier, distanceMetres } = calculateMovement(input.isCorrect, responseTimeMs);

    const result: ObstacleResult = {
      obstacleIndex,
      isCorrect: input.isCorrect,
      responseTimeMs,
      distanceMetres,
      tier,
    };

    runner.obstacleResults.push(result);
    runner.totalDistanceMetres += distanceMetres;
    runner.obstaclesCompleted += 1;

    // Simulate AI runners sequentially for this obstacle
    for (const aiRunner of runners) {
      if (aiRunner.isHuman) continue;
      const cfg = config.participants.find((p) => p.runnerId === aiRunner.runnerId)!;
      if (!cfg.personality) continue;
      const { isCorrect: aiCorrect, responseTimeMs: aiTime } = simulateAiObstacle(
        cfg.personality,
        aiRng,
      );
      const { tier: aiTier, distanceMetres: aiDist } = calculateMovement(aiCorrect, aiTime);
      const aiResult: ObstacleResult = {
        obstacleIndex,
        isCorrect: aiCorrect,
        responseTimeMs: aiTime,
        distanceMetres: aiDist,
        tier: aiTier,
      };
      aiRunner.obstacleResults.push(aiResult);
      aiRunner.totalDistanceMetres += aiDist;
      aiRunner.obstaclesCompleted += 1;
      if (aiRunner.obstaclesCompleted === OBSTACLE_COUNT) {
        aiRunner.finishTime = clock.getMs();
      }
    }

    if (runner.obstaclesCompleted === OBSTACLE_COUNT) {
      runner.finishTime = clock.getMs();
      const allFinished = runners.every((r) => r.obstaclesCompleted === OBSTACLE_COUNT);
      if (allFinished) {
        doTransition('FINISHING');
        doTransition('RESULTS');
      } else {
        doTransition('FINISHING');
      }
    } else {
      clock.startObstacleClock();
    }

    return result;
  }

  function getState(): RaceEngineState {
    return {
      state,
      config,
      clockMs: clock.getMs(),
      obstacleClockMs: clock.getObstacleMs(),
      currentObstacle: state === 'RACING' ? (runners[humanIdx]?.obstaclesCompleted ?? 0) : -1,
      runners: runners.map((r) => ({ ...r, obstacleResults: [...r.obstacleResults] })),
      problemSet,
    };
  }

  function getSummary(): RaceSummary {
    if (state !== 'RESULTS') {
      throw new RaceSummaryError();
    }

    const sorted = [...runners].sort((a, b) => {
      if (b.totalDistanceMetres !== a.totalDistanceMetres) {
        return b.totalDistanceMetres - a.totalDistanceMetres;
      }
      return runners.indexOf(a) - runners.indexOf(b);
    });

    const participants: ParticipantSummary[] = sorted.map((runner, posIdx) => {
      const cfg = config.participants.find((p) => p.runnerId === runner.runnerId)!;
      const correct = runner.obstacleResults.filter((r) => r.isCorrect).length;
      const avgMs =
        runner.obstacleResults.length > 0
          ? Math.round(
              runner.obstacleResults.reduce((s, r) => s + r.responseTimeMs, 0) /
                runner.obstacleResults.length,
            )
          : 0;
      return {
        avatar_id: cfg.avatarId,
        position: posIdx + 1,
        problems_correct: correct,
        average_response_ms: avgMs,
        total_distance: runner.totalDistanceMetres,
        xp_earned: 0,
      };
    });

    return {
      race_id: config.raceId,
      seed: String(config.seed),
      difficulty_tier: config.tier,
      mode: config.mode,
      started_at: startedAt!.toISOString(),
      completed_at: completedAt!.toISOString(),
      participants,
    };
  }

  return {
    transition: doTransition,
    tick(timestamp: number) {
      clock.tick(timestamp);
    },
    pause() {
      clock.pause();
    },
    resume() {
      clock.resume();
    },
    submitAnswer,
    getState,
    getSummary,
  };
}
