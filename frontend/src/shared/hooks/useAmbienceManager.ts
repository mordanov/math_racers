import { useCallback, useEffect, useRef } from 'react';

const AMBIENCE_FILES = {
  baseline: '/ambience/ambience_crowd_baseline.ogg',
  cheer: '/ambience/ambience_crowd_cheer_short.ogg',
  applause: '/ambience/ambience_crowd_applause.ogg',
} as const;

function readAmbienceVolume(): number {
  try {
    const master = parseInt(localStorage.getItem('settings.masterVolume') ?? '100', 10);
    const ambience = parseInt(localStorage.getItem('settings.ambienceVolume') ?? '60', 10);
    return (master / 100) * (ambience / 100);
  } catch {
    return 0.6;
  }
}

export function useAmbienceManager() {
  const baselineRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    const audio = new Audio(AMBIENCE_FILES.baseline);
    audio.loop = true;
    audio.volume = readAmbienceVolume();
    baselineRef.current = audio;
    audio.play().catch(() => {});
    return () => {
      audio.pause();
      audio.currentTime = 0;
      baselineRef.current = null;
    };
  }, []);

  const triggerAmbience = useCallback((event: 'cheer' | 'applause') => {
    const audio = new Audio(AMBIENCE_FILES[event]);
    audio.volume = readAmbienceVolume();
    audio.play().catch(() => {});
  }, []);

  return { triggerAmbience };
}
