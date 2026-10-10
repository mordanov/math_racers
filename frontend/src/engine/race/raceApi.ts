import type { Achievement } from '../achievements/types';
import type { RaceSummary } from './types';
import { apiClient } from '../../infrastructure/api-client';

export interface RaceAnswerResult {
  answer_index: number;
  is_correct: boolean;
  response_time_ms: number;
}

export interface RaceSummaryResult {
  new_achievements: Achievement[];
  progression?: { xp_earned_this_race: number } | null;
}

export async function postRaceSummary(summary: RaceSummary): Promise<RaceSummaryResult> {
  return apiClient.post<RaceSummaryResult>(`/races/${summary.race_id}/results`, {
    idempotency_key: summary.idempotency_key,
    human_avatar_id: summary.human_avatar_id,
    participants: summary.participants.map(({ avatar_id, position }) => ({
      avatar_id,
      position,
    })),
    ...(summary.mode === 'training' ? { answers: summary.answers } : {}),
  });
}

export async function submitRaceAnswer(
  raceId: string,
  answerIndex: number,
  operation: RaceSummary['answers'][number]['operation'],
  answer: string,
): Promise<RaceAnswerResult> {
  return apiClient.post<RaceAnswerResult>(`/races/${raceId}/answers`, {
    answer_index: answerIndex,
    operation,
    answer,
  });
}
