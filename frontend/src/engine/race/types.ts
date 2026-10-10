import type { ProblemSet, Tier, TierConfig } from '../math/types';

export type RaceState = 'IDLE' | 'LOBBY' | 'COUNTDOWN' | 'RACING' | 'FINISHING' | 'RESULTS';

export type RaceMode = 'quick' | 'championship' | 'duel' | 'training';

export type MovementTier = 'perfect' | 'excellent' | 'good' | 'slow' | 'incorrect';

export interface TierResult {
  tier: MovementTier;
  distanceMetres: number;
}

export interface ObstacleResult {
  obstacleIndex: number;
  isCorrect: boolean;
  answer: string;
  responseTimeMs: number;
  distanceMetres: number;
  tier: MovementTier;
}

export interface RunnerState {
  runnerId: string;
  isHuman: boolean;
  totalDistanceMetres: number;
  obstaclesCompleted: number;
  obstacleResults: ObstacleResult[];
  finishTime: number | null;
}

export interface AiPersonality {
  id: string;
  name: string;
  baseResponseTimeMs: number;
  responseTimeVarianceMs: number;
  accuracyRate: number;
  speedProfile: 'uniform' | 'front_loaded' | 'back_loaded' | 'random';
  tierOffset: number;
}

export type ParticipantConfig = {
  runnerId: string;
  isHuman: boolean;
  avatarId: string;
  personality?: AiPersonality;
};

export interface RaceConfig {
  raceId: string;
  seed: number;
  tier: Tier;
  customTierConfig?: TierConfig;
  mode: RaceMode;
  participants: ParticipantConfig[];
}

export interface RaceEngineState {
  state: RaceState;
  config: RaceConfig | null;
  clockMs: number;
  obstacleClockMs: number;
  currentObstacle: number;
  runners: RunnerState[];
  problemSet: ProblemSet | null;
}

export interface ParticipantSummary {
  avatar_id: string;
  position: number | null;
  problems_correct: number;
  longest_streak: number;
  average_response_ms: number;
  total_distance: number;
}

export interface OperationAnswerSummary {
  operation: ProblemSet['problems'][number]['operation'];
  answer: string;
  response_time_ms: number;
}

export interface RaceSummary {
  race_id: string;
  idempotency_key: string;
  mode: RaceMode;
  human_avatar_id: string;
  started_at: string;
  completed_at: string;
  participants: ParticipantSummary[];
  answers: OperationAnswerSummary[];
}
