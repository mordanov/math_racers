import { afterEach, describe, expect, it, vi } from 'vitest';
import { postRaceSummary, submitRaceAnswer } from './raceApi';

const mockPost = vi.hoisted(() => vi.fn());

vi.mock('../../infrastructure/api-client', () => ({
  apiClient: { post: mockPost },
}));

afterEach(() => vi.clearAllMocks());

describe('race API', () => {
  it('submits a competitive result without client timing or answer claims', async () => {
    const response = { new_achievements: [] };
    mockPost.mockResolvedValue(response);

    const result = await postRaceSummary({
      race_id: 'race-1',
      idempotency_key: 'result-key',
      mode: 'quick',
      human_avatar_id: 'avatar-1',
      started_at: '2026-08-10T12:00:00Z',
      completed_at: '2026-08-10T12:05:00Z',
      participants: [
        {
          avatar_id: 'avatar-1',
          position: 1,
          problems_correct: 8,
          longest_streak: 8,
          average_response_ms: 1500,
          total_distance: 144,
        },
      ],
      answers: [{ operation: 'addition', answer: '9', response_time_ms: 1500 }],
    } as never);

    expect(result).toEqual(response);
    expect(mockPost).toHaveBeenCalledWith('/races/race-1/results', {
      idempotency_key: 'result-key',
      human_avatar_id: 'avatar-1',
      participants: [{ avatar_id: 'avatar-1', position: 1 }],
    });
  });

  it('keeps locally queued Training answers in the sync request', async () => {
    mockPost.mockResolvedValue({ new_achievements: [] });

    await postRaceSummary({
      race_id: 'race-1',
      idempotency_key: 'result-key',
      mode: 'training',
      human_avatar_id: 'avatar-1',
      started_at: '2026-08-10T12:00:00Z',
      completed_at: '2026-08-10T12:05:00Z',
      participants: [],
      answers: [{ operation: 'addition', answer: '9', response_time_ms: 500 }],
    } as never);

    expect(mockPost).toHaveBeenCalledWith('/races/race-1/results', {
      idempotency_key: 'result-key',
      human_avatar_id: 'avatar-1',
      participants: [],
      answers: [{ operation: 'addition', answer: '9', response_time_ms: 500 }],
    });
  });

  it('submits one answer to the race endpoint', async () => {
    mockPost.mockResolvedValue({
      answer_index: 2,
      is_correct: true,
      response_time_ms: 1200,
    });

    await submitRaceAnswer('race-1', 2, 'multiplication', '18');

    expect(mockPost).toHaveBeenCalledWith('/races/race-1/answers', {
      answer_index: 2,
      operation: 'multiplication',
      answer: '18',
    });
  });
});
