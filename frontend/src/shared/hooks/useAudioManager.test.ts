import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAudioManager } from './useAudioManager';

const mockAudio = {
  play: vi.fn().mockResolvedValue(undefined),
  pause: vi.fn(),
  loop: false,
  volume: 1,
  currentTime: 0,
  src: '',
};

beforeEach(() => {
  vi.spyOn(window, 'Audio' as keyof Window).mockImplementation(
    () => mockAudio as unknown as HTMLAudioElement,
  );
  mockAudio.play.mockResolvedValue(undefined);
  mockAudio.loop = false;
  mockAudio.volume = 1;
  mockAudio.currentTime = 0;
  mockAudio.src = '';
});

describe('useAudioManager', () => {
  it('plays music and sets loop=true for menu track', async () => {
    const { result } = renderHook(() => useAudioManager());
    await act(async () => {
      result.current.playMusic('menu');
    });
    expect(mockAudio.play).toHaveBeenCalled();
    expect(mockAudio.loop).toBe(true);
  });

  it('does not loop victory music', async () => {
    const { result } = renderHook(() => useAudioManager());
    await act(async () => {
      result.current.playMusic('victory');
    });
    expect(mockAudio.loop).toBe(false);
  });

  it('stops music on stopMusic()', async () => {
    const { result } = renderHook(() => useAudioManager());
    await act(async () => {
      result.current.playMusic('race');
      result.current.stopMusic();
    });
    expect(mockAudio.pause).toHaveBeenCalled();
    expect(mockAudio.currentTime).toBe(0);
  });

  it('applies volume from localStorage', async () => {
    localStorage.setItem('settings.masterVolume', '50');
    localStorage.setItem('settings.musicVolume', '80');
    const { result } = renderHook(() => useAudioManager());
    await act(async () => {
      result.current.playMusic('menu');
    });
    // 0.5 * 0.8 = 0.4
    expect(mockAudio.volume).toBeCloseTo(0.4, 2);
    localStorage.removeItem('settings.masterVolume');
    localStorage.removeItem('settings.musicVolume');
  });
});
