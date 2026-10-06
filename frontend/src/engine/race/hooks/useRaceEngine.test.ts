import { renderHook, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useRaceEngine } from './useRaceEngine';
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
    act(() => { result.current.startCountdown(); });
    await waitFor(() => expect(result.current.state).toBe('COUNTDOWN'));
  });

  it('startRacing() transitions engine from COUNTDOWN to RACING', async () => {
    const { result } = renderHook(() => useRaceEngine(config));
    act(() => { result.current.startCountdown(); });
    await waitFor(() => expect(result.current.state).toBe('COUNTDOWN'));
    act(() => { result.current.startRacing(); });
    await waitFor(() => expect(result.current.state).toBe('RACING'));
  });

  it('getSummary() throws before RESULTS state', () => {
    const { result } = renderHook(() => useRaceEngine(config));
    expect(() => result.current.getSummary()).toThrow();
  });

  it('does not expose summaryStatus', () => {
    const { result } = renderHook(() => useRaceEngine(config));
    expect((result.current as Record<string, unknown>)['summaryStatus']).toBeUndefined();
  });
});
