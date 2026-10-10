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
  submitAnswer(input: {
    answer: string;
    isCorrect?: boolean;
    responseTimeMs?: number;
  }): ObstacleResult;
  forceComplete(): void;
  getState(): RaceEngineState;
  getSummary(): RaceSummary;
}

export function createRaceEngine(config: RaceConfig): RaceEngine {
  let state: RaceState = 'IDLE';
  const clock = new GameClock();
  let startedAt: Date | null = null;
  let completedAt: Date | null = null;

  let problemSet = generateProblemSet(
    config.tier,
    config.seed,
    config.mode === 'training' ? 1 : OBSTACLE_COUNT,
    config.customTierConfig,
  );
  const runners: RunnerState[] = config.participants.map((p) => makeRunner(p.runnerId, p.isHuman));

  const humanIdx = runners.findIndex((r) => r.isHuman);
  // Per-opponent RNG — offset by participant index + 1 to avoid colliding with problem seed
  const aiRngs = config.participants.map((p, i) =>
    p.isHuman ? null : createRng(config.seed + i + 1),
  );

  function ensureTrainingProblem(index: number): void {
    if (config.mode !== 'training' || index < problemSet.problems.length) return;

    const last = problemSet.problems[problemSet.problems.length - 1];
    let next = generateProblemSet(config.tier, config.seed + index, 1, config.customTierConfig)
      .problems[0];
    let attempt = 0;
    while (
      last !== undefined &&
      next.operation === last.operation &&
      next.operand_a === last.operand_a &&
      next.operand_b === last.operand_b &&
      attempt < 100
    ) {
      attempt += 1;
      next = generateProblemSet(
        config.tier,
        config.seed + index + attempt * 104729,
        1,
        config.customTierConfig,
      ).problems[0];
    }
    if (
      last !== undefined &&
      next.operation === last.operation &&
      next.operand_a === last.operand_a &&
      next.operand_b === last.operand_b
    ) {
      throw new Error('Unable to generate a distinct Training problem.');
    }
    problemSet = {
      ...problemSet,
      count: problemSet.problems.length + 1,
      problems: [...problemSet.problems, next],
    };
  }

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

  function submitAnswer(input: {
    answer: string;
    isCorrect?: boolean;
    responseTimeMs?: number;
  }): ObstacleResult {
    if (state !== 'RACING') {
      throw new RaceStateError(state, 'RACING');
    }
    const runner = runners[humanIdx];
    const obstacleIndex = runner.obstaclesCompleted;
    ensureTrainingProblem(obstacleIndex);
    const problem = problemSet.problems[obstacleIndex];
    const numericAnswer = Number(input.answer.trim());
    const isCorrect =
      input.isCorrect ??
      (input.answer.trim() !== '' &&
        Number.isSafeInteger(numericAnswer) &&
        numericAnswer === problem.answer);
    const responseTimeMs = input.responseTimeMs ?? clock.getObstacleMs();
    const { tier, distanceMetres } = calculateMovement(isCorrect, responseTimeMs);

    const result: ObstacleResult = {
      obstacleIndex,
      isCorrect,
      answer: input.answer,
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
      const pIdx = config.participants.findIndex((p) => p.runnerId === aiRunner.runnerId);
      const cfg = config.participants[pIdx];
      if (!cfg.personality) continue;
      const rng = aiRngs[pIdx]!;
      const { isCorrect: aiCorrect, responseTimeMs: aiTime } = simulateAiObstacle(
        cfg.personality,
        obstacleIndex,
        rng,
      );
      const { tier: aiTier, distanceMetres: aiDist } = calculateMovement(aiCorrect, aiTime);
      const aiResult: ObstacleResult = {
        obstacleIndex,
        isCorrect: aiCorrect,
        answer: '',
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

    if (runner.obstaclesCompleted === OBSTACLE_COUNT && config.mode !== 'training') {
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
    if (state === 'RACING') {
      ensureTrainingProblem(runners[humanIdx]?.obstaclesCompleted ?? 0);
    }
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

  function forceComplete(): void {
    if (state === 'RACING') {
      completedAt = new Date();
      state = 'RESULTS';
    }
  }

  function getSummary(): RaceSummary {
    if (state !== 'RESULTS') {
      throw new RaceSummaryError();
    }

    const isTraining = config.mode === 'training';

    const sorted = isTraining
      ? [...runners]
      : [...runners].sort((a, b) => {
          if (b.totalDistanceMetres !== a.totalDistanceMetres) {
            return b.totalDistanceMetres - a.totalDistanceMetres;
          }
          return a.runnerId < b.runnerId ? -1 : 1;
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
      let longestStreak = 0;
      let currentStreak = 0;
      for (const r of runner.obstacleResults) {
        if (r.isCorrect) {
          currentStreak++;
          if (currentStreak > longestStreak) longestStreak = currentStreak;
        } else {
          currentStreak = 0;
        }
      }

      return {
        avatar_id: cfg.avatarId,
        position: isTraining ? null : posIdx + 1,
        problems_correct: correct,
        longest_streak: longestStreak,
        average_response_ms: avgMs,
        total_distance: runner.totalDistanceMetres,
      };
    });

    const humanRunner = runners[humanIdx];
    return {
      race_id: config.raceId,
      idempotency_key: config.raceId,
      mode: config.mode,
      human_avatar_id: config.participants[humanIdx].avatarId,
      started_at: startedAt!.toISOString(),
      completed_at: completedAt!.toISOString(),
      participants,
      answers: humanRunner.obstacleResults.map((result) => ({
        operation: problemSet.problems[result.obstacleIndex].operation,
        answer: result.answer,
        response_time_ms: result.responseTimeMs,
      })),
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
    forceComplete,
    getState,
    getSummary,
  };
}
