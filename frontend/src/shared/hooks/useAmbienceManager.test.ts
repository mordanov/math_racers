import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { useAmbienceManager } from './useAmbienceManager';

let audioInstances: Array<{
  src: string;
  volume: number;
  loop: boolean;
  play: ReturnType<typeof vi.fn>;
  pause: ReturnType<typeof vi.fn>;
  currentTime: number;
}>;

beforeEach(() => {
  audioInstances = [];
  vi.stubGlobal(
    'Audio',
    vi.fn().mockImplementation((src: string) => {
      const inst = {
        src,
        volume: 0,
        loop: false,
        currentTime: 0,
        play: vi.fn().mockResolvedValue(undefined),
        pause: vi.fn(),
      };
      audioInstances.push(inst);
      return inst;
    }),
  );
});

afterEach(() => vi.unstubAllGlobals());

describe('useAmbienceManager', () => {
  it('starts crowd baseline looping on mount', () => {
    renderHook(() => useAmbienceManager());
    expect(audioInstances[0].src).toBe('/ambience/ambience_crowd_baseline.ogg');
    expect(audioInstances[0].loop).toBe(true);
    expect(audioInstances[0].play).toHaveBeenCalled();
  });

  it('stops baseline on unmount', () => {
    const { unmount } = renderHook(() => useAmbienceManager());
    unmount();
    expect(audioInstances[0].pause).toHaveBeenCalled();
    expect(audioInstances[0].currentTime).toBe(0);
  });

  it('triggerAmbience("cheer") plays cheer sound as one-shot', () => {
    const { result } = renderHook(() => useAmbienceManager());
    act(() => {
      result.current.triggerAmbience('cheer');
    });
    const cheer = audioInstances.find((a) => a.src.includes('cheer'));
    expect(cheer).toBeDefined();
    expect(cheer!.loop).toBe(false);
    expect(cheer!.play).toHaveBeenCalled();
  });

  it('triggerAmbience("applause") plays applause sound as one-shot', () => {
    const { result } = renderHook(() => useAmbienceManager());
    act(() => {
      result.current.triggerAmbience('applause');
    });
    const applause = audioInstances.find((a) => a.src.includes('applause'));
    expect(applause).toBeDefined();
    expect(applause!.loop).toBe(false);
  });

  it('applies ambienceVolume from localStorage', () => {
    localStorage.setItem('settings.masterVolume', '100');
    localStorage.setItem('settings.ambienceVolume', '60');
    renderHook(() => useAmbienceManager());
    expect(audioInstances[0].volume).toBeCloseTo(0.6, 2);
    localStorage.removeItem('settings.masterVolume');
    localStorage.removeItem('settings.ambienceVolume');
  });
});
