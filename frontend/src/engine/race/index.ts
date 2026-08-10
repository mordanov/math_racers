export { createRaceEngine, RaceSummaryError } from './raceEngine';
export { RaceStateError } from './stateMachine';
export { calculateMovement } from './movement';
export { GameClock } from './clock';
export { useRaceEngine } from './hooks/useRaceEngine';
export { postRaceSummary } from './raceApi';
export { OBSTACLE_COUNT, MAX_TRACK_DISTANCE } from './constants';
export type {
  RaceState,
  RaceMode,
  MovementTier,
  TierResult,
  ObstacleResult,
  RunnerState,
  AiPersonality,
  ParticipantConfig,
  RaceConfig,
  RaceEngineState,
  ParticipantSummary,
  RaceSummary,
} from './types';
