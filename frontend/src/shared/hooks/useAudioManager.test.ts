import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { useAudioManager } from './useAudioManager';

let audioInstances: Array<{
  src: string;
  volume: number;
  currentTime: number;
  play: ReturnType<typeof vi.fn>;
  pause: ReturnType<typeof vi.fn>;
  addEventListener: ReturnType<typeof vi.fn>;
  _triggerEnded: () => void;
}>;

beforeEach(() => {
  audioInstances = [];
  vi.stubGlobal(
    'Audio',
    vi.fn().mockImplementation((src: string) => {
      let endedFn: (() => void) | null = null;
      const inst = {
        src,
        volume: 0,
        currentTime: 0,
        play: vi.fn().mockResolvedValue(undefined),
        pause: vi.fn(),
        addEventListener: vi.fn().mockImplementation((ev: string, fn: () => void) => {
          if (ev === 'ended') endedFn = fn;
        }),
        _triggerEnded: () => endedFn?.(),
      };
      audioInstances.push(inst);
      return inst;
    }),
  );
});

afterEach(() => vi.unstubAllGlobals());

describe('useAudioManager — sequential playback', () => {
  it('plays first file of the track on playMusic()', () => {
    const { result } = renderHook(() => useAudioManager());
    act(() => {
      result.current.playMusic('menu');
    });
    expect(audioInstances[0].src).toBe('/audio/music_menu_1.wav');
    expect(audioInstances[0].play).toHaveBeenCalledTimes(1);
  });

  it('plays second file when first ends', () => {
    const { result } = renderHook(() => useAudioManager());
    act(() => {
      result.current.playMusic('race');
    });
    act(() => {
      audioInstances[0]._triggerEnded();
    });
    expect(audioInstances[1].src).toBe('/audio/music_race_2.wav');
    expect(audioInstances[1].play).toHaveBeenCalledTimes(1);
  });

  it('loops back to first file after second ends for non-victory tracks', () => {
    const { result } = renderHook(() => useAudioManager());
    act(() => {
      result.current.playMusic('menu');
    });
    act(() => {
      audioInstances[0]._triggerEnded();
    });
    act(() => {
      audioInstances[1]._triggerEnded();
    });
    expect(audioInstances[2].src).toBe('/audio/music_menu_1.wav');
  });

  it('does NOT loop after second file ends for victory track', () => {
    const { result } = renderHook(() => useAudioManager());
    act(() => {
      result.current.playMusic('victory');
    });
    act(() => {
      audioInstances[0]._triggerEnded();
    });
    act(() => {
      audioInstances[1]._triggerEnded();
    });
    expect(audioInstances.length).toBe(2);
  });

  it('stopMusic() prevents the ended chain from continuing', () => {
    const { result } = renderHook(() => useAudioManager());
    act(() => {
      result.current.playMusic('race');
    });
    act(() => {
      result.current.stopMusic();
    });
    act(() => {
      audioInstances[0]._triggerEnded();
    });
    expect(audioInstances.length).toBe(1);
  });

  it('stopMusic() pauses and clears currentTime', () => {
    const { result } = renderHook(() => useAudioManager());
    act(() => {
      result.current.playMusic('menu');
    });
    act(() => {
      result.current.stopMusic();
    });
    expect(audioInstances[0].pause).toHaveBeenCalled();
    expect(audioInstances[0].currentTime).toBe(0);
  });

  it('applies volume from localStorage', () => {
    localStorage.setItem('settings.masterVolume', '50');
    localStorage.setItem('settings.musicVolume', '80');
    const { result } = renderHook(() => useAudioManager());
    act(() => {
      result.current.playMusic('menu');
    });
    expect(audioInstances[0].volume).toBeCloseTo(0.4, 2);
    localStorage.removeItem('settings.masterVolume');
    localStorage.removeItem('settings.musicVolume');
  });

  it('updates playing track volume when storage event fires', () => {
    localStorage.setItem('settings.masterVolume', '100');
    localStorage.setItem('settings.musicVolume', '100');
    const { result } = renderHook(() => useAudioManager());
    act(() => {
      result.current.playMusic('menu');
    });
    localStorage.setItem('settings.masterVolume', '50');
    act(() => {
      window.dispatchEvent(new StorageEvent('storage'));
    });
    expect(audioInstances[0].volume).toBeCloseTo(0.5, 2);
    localStorage.removeItem('settings.masterVolume');
    localStorage.removeItem('settings.musicVolume');
  });
});
