import { renderHook, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useRaceEngine } from './useRaceEngine';
import { createRaceEngine } from '../raceEngine';
import type { RaceConfig } from '../types';

const config: RaceConfig = {
  raceId: 'r1',
  seed: 1,
  tier: 1,
  mode: 'quick',
  participants: [{ runnerId: 'player', isHuman: true, avatarId: 'av1' }],
};

describe('useRaceEngine', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it('starts in IDLE state', () => {
    const { result } = renderHook(() => useRaceEngine(config));
    expect(result.current.state).toBe('IDLE');
  });

  it('startCountdown() transitions engine to COUNTDOWN', async () => {
    const { result } = renderHook(() => useRaceEngine(config));
    act(() => {
      result.current.startCountdown();
    });
    await waitFor(() => expect(result.current.state).toBe('COUNTDOWN'));
  });

  it('startRacing() transitions engine from COUNTDOWN to RACING', async () => {
    const { result } = renderHook(() => useRaceEngine(config));
    act(() => {
      result.current.startCountdown();
    });
    await waitFor(() => expect(result.current.state).toBe('COUNTDOWN'));
    act(() => {
      result.current.startRacing();
    });
    await waitFor(() => expect(result.current.state).toBe('RACING'));
  });

  it('getSummary() throws before RESULTS state', () => {
    const { result } = renderHook(() => useRaceEngine(config));
    expect(() => result.current.getSummary()).toThrow();
  });

  it('uses server-authoritative answer correctness and timing', () => {
    const { result } = renderHook(() => useRaceEngine(config));
    act(() => {
      result.current.startCountdown();
      result.current.startRacing();
    });

    let obstacle: ReturnType<typeof result.current.submitAnswer> | undefined;
    act(() => {
      obstacle = result.current.submitAnswer({
        answer: 'not numeric',
        isCorrect: true,
        responseTimeMs: 3750,
      });
    });

    expect(obstacle).toMatchObject({
      isCorrect: true,
      responseTimeMs: 3750,
      distanceMetres: 15,
    });
  });

  it('does not expose summaryStatus', () => {
    const { result } = renderHook(() => useRaceEngine(config));
    expect((result.current as Record<string, unknown>)['summaryStatus']).toBeUndefined();
  });

  it('keeps Training active beyond eight problems and generates more problems', () => {
    const trainingConfig: RaceConfig = {
      ...config,
      mode: 'training',
    };
    const engine = createRaceEngine(trainingConfig);
    engine.transition('LOBBY');
    engine.transition('COUNTDOWN');
    engine.transition('RACING');

    for (let index = 0; index < 10; index += 1) {
      const state = engine.getState();
      const problemSet = state.problemSet;
      if (!problemSet) throw new Error('Training problem set is missing.');
      const problem = problemSet.problems[state.currentObstacle];
      if (!problem) throw new Error('Training problem is missing.');
      engine.submitAnswer({
        answer: String(index % 2 === 0 ? problem.answer : problem.answer + 1),
      });
    }

    const state = engine.getState();
    expect(state.state).toBe('RACING');
    expect(state.currentObstacle).toBe(10);
    expect(state.problemSet?.problems).toHaveLength(11);
  });
});
