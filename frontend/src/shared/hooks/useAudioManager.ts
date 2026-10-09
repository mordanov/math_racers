import { useCallback, useEffect, useRef } from 'react';

export type MusicTrack = 'menu' | 'race' | 'victory';

const TRACK_FILES: Record<MusicTrack, string[]> = {
  menu: ['/audio/music_menu_1.wav', '/audio/music_menu_2.wav'],
  race: ['/audio/music_race_1.wav', '/audio/music_race_2.wav'],
  victory: ['/audio/music_victory_1.wav', '/audio/music_victory_2.wav'],
};

function readVolume(): number {
  try {
    const master = parseInt(localStorage.getItem('settings.masterVolume') ?? '100', 10);
    const music = parseInt(localStorage.getItem('settings.musicVolume') ?? '100', 10);
    return (master / 100) * (music / 100);
  } catch {
    return 1;
  }
}

export function useAudioManager() {
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const stopMusic = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
  }, []);

  const playMusic = useCallback(
    (track: MusicTrack) => {
      stopMusic();

      function playAt(index: number) {
        const files = TRACK_FILES[track];
        const audio = new Audio(files[index]);
        audio.volume = readVolume();
        audioRef.current = audio;
        audio.addEventListener(
          'ended',
          () => {
            if (audioRef.current !== audio) return;
            const next = index + 1 < files.length ? index + 1 : track !== 'victory' ? 0 : -1;
            if (next >= 0) playAt(next);
          },
          { once: true },
        );
        audio.play().catch(() => {});
      }

      playAt(0);
    },
    [stopMusic],
  );

  useEffect(() => {
    const handler = () => {
      if (audioRef.current) audioRef.current.volume = readVolume();
    };
    window.addEventListener('storage', handler);
    return () => window.removeEventListener('storage', handler);
  }, []);

  return { playMusic, stopMusic };
}
