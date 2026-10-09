import { useCallback } from 'react';

export type SfxName =
  | 'correct'
  | 'incorrect'
  | 'countdown'
  | 'achievement'
  | 'levelup'
  | 'obstacle_hit'
  | 'obstacle_jump'
  | 'ui_click'
  | 'ui_hover'
  | 'ui_window_open'
  | 'ui_window_close'
  | 'ui_card_select'
  | 'ui_avatar_select';

const SFX_FILES: Record<SfxName, string> = {
  correct: '/gameplay_sounds/sfx_correct.mp3',
  incorrect: '/gameplay_sounds/sfx_incorrect.mp3',
  countdown: '/gameplay_sounds/sfx_countdown.mp3',
  achievement: '/gameplay_sounds/sfx_achievement.mp3',
  levelup: '/gameplay_sounds/sfx_levelup.mp3',
  obstacle_hit: '/gameplay_sounds/sfx_obstacle_hit.mp3',
  obstacle_jump: '/gameplay_sounds/sfx_obstacle_jump.mp3',
  ui_click: '/ui_sounds/ui_click.mp3',
  ui_hover: '/ui_sounds/ui_hover.mp3',
  ui_window_open: '/ui_sounds/ui_window_open.mp3',
  ui_window_close: '/ui_sounds/ui_window_close.mp3',
  ui_card_select: '/ui_sounds/ui_card_select.mp3',
  ui_avatar_select: '/ui_sounds/ui_avatar_select.mp3',
};

function readSfxVolume(): number {
  try {
    const master = parseInt(localStorage.getItem('settings.masterVolume') ?? '100', 10);
    const sfx = parseInt(localStorage.getItem('settings.sfxVolume') ?? '80', 10);
    return (master / 100) * (sfx / 100);
  } catch {
    return 0.8;
  }
}

export function useSfxPlayer() {
  const playSfx = useCallback((name: SfxName) => {
    const audio = new Audio(SFX_FILES[name]);
    audio.volume = readSfxVolume();
    audio.play().catch(() => {});
  }, []);

  return { playSfx };
}
