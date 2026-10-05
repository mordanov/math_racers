import { afterEach, expect, it, vi } from 'vitest';
import { postRaceSummary } from './raceApi';

afterEach(() => vi.unstubAllGlobals());

it('returns empty achievements on 409 without throwing', async () => {
  vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
    status: 409,
    ok: false,
    json: vi.fn().mockResolvedValue({}),
  }));
  const result = await postRaceSummary({
    session_id: 'test',
    avatar_id: 'a1',
    race_mode: 'quick',
    race_duration_ms: 60000,
    problems_attempted: 10,
    problems_correct: 8,
    distance_covered: 500,
    finishing_position: 1,
    participants: [],
  } as never);
  expect(result).toEqual({ new_achievements: [] });
});
