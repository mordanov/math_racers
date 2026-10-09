import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { useSfxPlayer } from './useSfxPlayer';

let audioInstances: Array<{ src: string; volume: number; play: ReturnType<typeof vi.fn> }>;

beforeEach(() => {
  audioInstances = [];
  vi.stubGlobal(
    'Audio',
    vi.fn().mockImplementation((src: string) => {
      const inst = { src, volume: 0, play: vi.fn().mockResolvedValue(undefined) };
      audioInstances.push(inst);
      return inst;
    }),
  );
});

afterEach(() => vi.unstubAllGlobals());

describe('useSfxPlayer', () => {
  it('creates Audio with the correct path for a gameplay sound', () => {
    const { result } = renderHook(() => useSfxPlayer());
    act(() => {
      result.current.playSfx('correct');
    });
    expect(audioInstances[0].src).toBe('/gameplay_sounds/sfx_correct.mp3');
    expect(audioInstances[0].play).toHaveBeenCalledTimes(1);
  });

  it('creates Audio with the correct path for a UI sound', () => {
    const { result } = renderHook(() => useSfxPlayer());
    act(() => {
      result.current.playSfx('ui_click');
    });
    expect(audioInstances[0].src).toBe('/ui_sounds/ui_click.mp3');
  });

  it('creates a separate Audio instance per call (true one-shot overlap)', () => {
    const { result } = renderHook(() => useSfxPlayer());
    act(() => {
      result.current.playSfx('correct');
      result.current.playSfx('correct');
    });
    expect(audioInstances.length).toBe(2);
    expect(audioInstances[0]).not.toBe(audioInstances[1]);
  });

  it('applies volume from localStorage at call time', () => {
    localStorage.setItem('settings.masterVolume', '80');
    localStorage.setItem('settings.sfxVolume', '50');
    const { result } = renderHook(() => useSfxPlayer());
    act(() => {
      result.current.playSfx('incorrect');
    });
    expect(audioInstances[0].volume).toBeCloseTo(0.4, 2);
    localStorage.removeItem('settings.masterVolume');
    localStorage.removeItem('settings.sfxVolume');
  });

  it('reads volume at call time, not at hook mount', () => {
    const { result } = renderHook(() => useSfxPlayer());
    localStorage.setItem('settings.masterVolume', '50');
    localStorage.setItem('settings.sfxVolume', '100');
    act(() => {
      result.current.playSfx('correct');
    });
    expect(audioInstances[0].volume).toBeCloseTo(0.5, 2);
    localStorage.removeItem('settings.masterVolume');
    localStorage.removeItem('settings.sfxVolume');
  });
});
