import type { ProblemSet, Tier } from '../math/types';

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
  position: number;
  problems_correct: number;
  average_response_ms: number;
  total_distance: number;
  xp_earned: number;
}

export interface RaceSummary {
  race_id: string;
  seed: string;
  difficulty_tier: Tier;
  mode: RaceMode;
  started_at: string;
  completed_at: string;
  participants: ParticipantSummary[];
}
