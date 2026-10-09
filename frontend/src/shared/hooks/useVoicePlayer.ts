import { useCallback } from 'react';

export type Species = 'bear' | 'cat' | 'fox' | 'mouse' | 'rabbit';
export type VoiceEmotion = 'thinking' | 'happy' | 'surprised' | 'celebrating';

function readVoiceVolume(): number {
  try {
    const master = parseInt(localStorage.getItem('settings.masterVolume') ?? '100', 10);
    const voice = parseInt(localStorage.getItem('settings.voiceVolume') ?? '80', 10);
    return (master / 100) * (voice / 100);
  } catch {
    return 0.8;
  }
}

export function useVoicePlayer(species: Species | null) {
  const playVoice = useCallback(
    (emotion: VoiceEmotion) => {
      if (!species) return;
      const audio = new Audio(`/characters/voice_${species}_${emotion}.ogg`);
      audio.volume = readVoiceVolume();
      audio.play().catch(() => {});
    },
    [species],
  );

  return { playVoice };
}
