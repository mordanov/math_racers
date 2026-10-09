import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { useVoicePlayer } from './useVoicePlayer';

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

describe('useVoicePlayer', () => {
  it('plays the correct voice file for species + emotion', () => {
    const { result } = renderHook(() => useVoicePlayer('bear'));
    act(() => {
      result.current.playVoice('happy');
    });
    expect(audioInstances[0].src).toBe('/characters/voice_bear_happy.wav');
    expect(audioInstances[0].play).toHaveBeenCalledTimes(1);
  });

  it('plays the correct file for a different species and emotion', () => {
    const { result } = renderHook(() => useVoicePlayer('rabbit'));
    act(() => {
      result.current.playVoice('celebrating');
    });
    expect(audioInstances[0].src).toBe('/characters/voice_rabbit_celebrating.wav');
  });

  it('playVoice is a no-op when species is null', () => {
    const { result } = renderHook(() => useVoicePlayer(null));
    act(() => {
      result.current.playVoice('thinking');
    });
    expect(audioInstances.length).toBe(0);
  });

  it('applies voiceVolume from localStorage', () => {
    localStorage.setItem('settings.masterVolume', '100');
    localStorage.setItem('settings.voiceVolume', '80');
    const { result } = renderHook(() => useVoicePlayer('fox'));
    act(() => {
      result.current.playVoice('surprised');
    });
    expect(audioInstances[0].volume).toBeCloseTo(0.8, 2);
    localStorage.removeItem('settings.masterVolume');
    localStorage.removeItem('settings.voiceVolume');
  });

  it('all five species produce different file paths', () => {
    const species = ['bear', 'cat', 'fox', 'mouse', 'rabbit'] as const;
    const paths = species.map((s) => {
      const { result } = renderHook(() => useVoicePlayer(s));
      act(() => {
        result.current.playVoice('thinking');
      });
      return audioInstances[audioInstances.length - 1].src;
    });
    const unique = new Set(paths);
    expect(unique.size).toBe(5);
  });
});
