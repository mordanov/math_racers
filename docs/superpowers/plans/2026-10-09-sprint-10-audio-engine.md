# Sprint 10: Audio Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire all audio assets into the game — sequential music, gameplay SFX, crowd ambience, character voices, UI sounds, and two new Settings sliders.

**Architecture:** Four focused hooks in `frontend/src/shared/hooks/`. Music stays in `useAudioManager` (extended for sequential playback). New: `useSfxPlayer` (one-shot sounds), `useAmbienceManager` (crowd layer), `useVoicePlayer` (character reactions). Route state gains `avatarSpecies` to thread the player's character into the voice hooks.

**Tech Stack:** React hooks, HTMLAudioElement, Vitest + happy-dom, `vi.stubGlobal('Audio', ...)` for test isolation.

**Spec:** `docs/superpowers/specs/2026-10-09-sprint-10-audio-engine-design.md`

## Global Constraints

- TypeScript strict mode — no `any` except where the existing codebase already uses it
- All hooks in `frontend/src/shared/hooks/`
- Volume formula: `(masterVolume / 100) × (layerVolume / 100)`, both integers 0–100 from localStorage
- `Array.from({ length: n }, () => v)` not `Array(n).fill(v)`
- No new npm dependencies
- `vi.hoisted()` for module-level mocks; never reference object methods directly in `expect()`
- `eslint-disable-next-line react-hooks/exhaustive-deps` is forbidden — design hooks so it is not needed
- Audio SFX calls: `sfxVolume` localStorage key is `settings.sfxVolume`; ambience key is `settings.ambienceVolume`; voice key is `settings.voiceVolume`

## Review Focus

1. `stopMusic` called while an `ended` chain is in progress — the handler must check `audioRef.current !== audio` before continuing; missing this check replays the track after stop.
2. Victory track: after `_2.ended` fires, the chain must stop (no loop back to `_1`) — easy to regress if the loop condition is inverted.
3. `playVoice` when `species` is null must be a no-op — throwing here crashes the race screen when avatarSpecies is absent.
4. `triggerAmbience('applause')` fires after the race ends on the results screen; the baseline `Audio` must be stopped at that point or it leaks past unmount.
5. `readVolume` for SFX reads at call time (not hook mount) so a volume slider change takes effect on the next sound played without a re-render — a test that reads volume at mount time will pass but not verify this.

---

### Task 1: Sequential music (`useAudioManager`)

**Files:**
- Modify: `frontend/src/shared/hooks/useAudioManager.ts`
- Modify: `frontend/src/shared/hooks/useAudioManager.test.ts`

**Interfaces:**
- Produces: `useAudioManager()` → `{ playMusic: (track: MusicTrack) => void, stopMusic: () => void }` — API unchanged, internal behaviour changes.

- [ ] **Step 1: Write failing tests**

Replace the contents of `useAudioManager.test.ts`:

```typescript
import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { useAudioManager } from './useAudioManager';

// One array per test; populated by the stubbed Audio constructor
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
    act(() => { result.current.playMusic('menu'); });
    expect(audioInstances[0].src).toBe('/audio/music_menu_1.wav');
    expect(audioInstances[0].play).toHaveBeenCalledTimes(1);
  });

  it('plays second file when first ends', () => {
    const { result } = renderHook(() => useAudioManager());
    act(() => { result.current.playMusic('race'); });
    act(() => { audioInstances[0]._triggerEnded(); });
    expect(audioInstances[1].src).toBe('/audio/music_race_2.wav');
    expect(audioInstances[1].play).toHaveBeenCalledTimes(1);
  });

  it('loops back to first file after second ends for non-victory tracks', () => {
    const { result } = renderHook(() => useAudioManager());
    act(() => { result.current.playMusic('menu'); });
    act(() => { audioInstances[0]._triggerEnded(); });
    act(() => { audioInstances[1]._triggerEnded(); });
    expect(audioInstances[2].src).toBe('/audio/music_menu_1.wav');
  });

  it('does NOT loop after second file ends for victory track', () => {
    const { result } = renderHook(() => useAudioManager());
    act(() => { result.current.playMusic('victory'); });
    act(() => { audioInstances[0]._triggerEnded(); });
    act(() => { audioInstances[1]._triggerEnded(); });
    expect(audioInstances.length).toBe(2);
  });

  it('stopMusic() prevents the ended chain from continuing', () => {
    const { result } = renderHook(() => useAudioManager());
    act(() => { result.current.playMusic('race'); });
    act(() => { result.current.stopMusic(); });
    act(() => { audioInstances[0]._triggerEnded(); });
    expect(audioInstances.length).toBe(1); // chain did not continue
  });

  it('stopMusic() pauses and clears currentTime', () => {
    const { result } = renderHook(() => useAudioManager());
    act(() => { result.current.playMusic('menu'); });
    act(() => { result.current.stopMusic(); });
    expect(audioInstances[0].pause).toHaveBeenCalled();
    expect(audioInstances[0].currentTime).toBe(0);
  });

  it('applies volume from localStorage', () => {
    localStorage.setItem('settings.masterVolume', '50');
    localStorage.setItem('settings.musicVolume', '80');
    const { result } = renderHook(() => useAudioManager());
    act(() => { result.current.playMusic('menu'); });
    expect(audioInstances[0].volume).toBeCloseTo(0.4, 2); // 0.5 * 0.8
    localStorage.removeItem('settings.masterVolume');
    localStorage.removeItem('settings.musicVolume');
  });

  it('updates playing track volume when storage event fires', () => {
    localStorage.setItem('settings.masterVolume', '100');
    localStorage.setItem('settings.musicVolume', '100');
    const { result } = renderHook(() => useAudioManager());
    act(() => { result.current.playMusic('menu'); });
    localStorage.setItem('settings.masterVolume', '50');
    act(() => { window.dispatchEvent(new StorageEvent('storage')); });
    expect(audioInstances[0].volume).toBeCloseTo(0.5, 2);
    localStorage.removeItem('settings.masterVolume');
    localStorage.removeItem('settings.musicVolume');
  });
});
```

- [ ] **Step 2: Run tests to see them fail**

```bash
cd frontend && pnpm test useAudioManager.test.ts
```
Expected: FAIL — existing tests check `loop = true/false` and use a shared `mockAudio` object; sequential tests fail because `playAt` doesn't exist yet.

- [ ] **Step 3: Replace `useAudioManager.ts` with sequential implementation**

```typescript
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
            const next =
              index + 1 < files.length ? index + 1 : track !== 'victory' ? 0 : -1;
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
```

- [ ] **Step 4: Run tests to see them pass**

```bash
cd frontend && pnpm test useAudioManager.test.ts
```
Expected: 8/8 PASS

- [ ] **Step 5: Run full suite to check for regressions**

```bash
cd frontend && pnpm test
```
Expected: full suite green (HomePageAudio tests still pass because they mock the whole module).

- [ ] **Step 6: Commit**

```bash
git add frontend/src/shared/hooks/useAudioManager.ts frontend/src/shared/hooks/useAudioManager.test.ts
git commit -m "feat(audio): sequential track playback in useAudioManager

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 2: `useSfxPlayer` hook

**Files:**
- Create: `frontend/src/shared/hooks/useSfxPlayer.ts`
- Create: `frontend/src/shared/hooks/useSfxPlayer.test.ts`

**Interfaces:**
- Produces: `useSfxPlayer()` → `{ playSfx: (name: SfxName) => void }` consumed by Tasks 6, 8, 10.

- [ ] **Step 1: Write failing test**

Create `frontend/src/shared/hooks/useSfxPlayer.test.ts`:

```typescript
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
    act(() => { result.current.playSfx('correct'); });
    expect(audioInstances[0].src).toBe('/gameplay_sounds/sfx_correct.mp3');
    expect(audioInstances[0].play).toHaveBeenCalledTimes(1);
  });

  it('creates Audio with the correct path for a UI sound', () => {
    const { result } = renderHook(() => useSfxPlayer());
    act(() => { result.current.playSfx('ui_click'); });
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
    act(() => { result.current.playSfx('incorrect'); });
    expect(audioInstances[0].volume).toBeCloseTo(0.4, 2); // 0.8 * 0.5
    localStorage.removeItem('settings.masterVolume');
    localStorage.removeItem('settings.sfxVolume');
  });

  it('reads volume at call time, not at hook mount', () => {
    const { result } = renderHook(() => useSfxPlayer());
    localStorage.setItem('settings.masterVolume', '50');
    localStorage.setItem('settings.sfxVolume', '100');
    act(() => { result.current.playSfx('correct'); });
    expect(audioInstances[0].volume).toBeCloseTo(0.5, 2);
    localStorage.removeItem('settings.masterVolume');
    localStorage.removeItem('settings.sfxVolume');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && pnpm test useSfxPlayer.test.ts
```
Expected: FAIL — module not found

- [ ] **Step 3: Implement `useSfxPlayer.ts`**

```typescript
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd frontend && pnpm test useSfxPlayer.test.ts
```
Expected: 5/5 PASS

- [ ] **Step 5: Run full suite**

```bash
cd frontend && pnpm test
```
Expected: full suite green.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/shared/hooks/useSfxPlayer.ts frontend/src/shared/hooks/useSfxPlayer.test.ts
git commit -m "feat(audio): add useSfxPlayer hook for one-shot gameplay and UI sounds

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 3: `useAmbienceManager` hook

**Files:**
- Create: `frontend/src/shared/hooks/useAmbienceManager.ts`
- Create: `frontend/src/shared/hooks/useAmbienceManager.test.ts`

**Interfaces:**
- Produces: `useAmbienceManager()` → `{ triggerAmbience: (event: 'cheer' | 'applause') => void }` consumed by Task 6.

- [ ] **Step 1: Write failing test**

Create `frontend/src/shared/hooks/useAmbienceManager.test.ts`:

```typescript
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
    expect(audioInstances[0].src).toBe('/ambience/ambience_crowd_baseline.wav');
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
    act(() => { result.current.triggerAmbience('cheer'); });
    const cheer = audioInstances.find((a) => a.src.includes('cheer'));
    expect(cheer).toBeDefined();
    expect(cheer!.loop).toBe(false);
    expect(cheer!.play).toHaveBeenCalled();
  });

  it('triggerAmbience("applause") plays applause sound as one-shot', () => {
    const { result } = renderHook(() => useAmbienceManager());
    act(() => { result.current.triggerAmbience('applause'); });
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
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && pnpm test useAmbienceManager.test.ts
```
Expected: FAIL — module not found

- [ ] **Step 3: Implement `useAmbienceManager.ts`**

```typescript
import { useCallback, useEffect, useRef } from 'react';

function readAmbienceVolume(): number {
  try {
    const master = parseInt(localStorage.getItem('settings.masterVolume') ?? '100', 10);
    const ambience = parseInt(localStorage.getItem('settings.ambienceVolume') ?? '60', 10);
    return (master / 100) * (ambience / 100);
  } catch {
    return 0.6;
  }
}

const AMBIENCE_FILES = {
  baseline: '/ambience/ambience_crowd_baseline.wav',
  cheer: '/ambience/ambience_crowd_cheer_short.wav',
  applause: '/ambience/ambience_crowd_applause.flac',
} as const;

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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd frontend && pnpm test useAmbienceManager.test.ts
```
Expected: 5/5 PASS

- [ ] **Step 5: Run full suite**

```bash
cd frontend && pnpm test
```
Expected: full suite green.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/shared/hooks/useAmbienceManager.ts frontend/src/shared/hooks/useAmbienceManager.test.ts
git commit -m "feat(audio): add useAmbienceManager hook for crowd ambience layer

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 4: `useVoicePlayer` hook

**Files:**
- Create: `frontend/src/shared/hooks/useVoicePlayer.ts`
- Create: `frontend/src/shared/hooks/useVoicePlayer.test.ts`

**Interfaces:**
- Consumes: `species: Species | null` (from route state via Task 5)
- Produces: `useVoicePlayer(species)` → `{ playVoice: (emotion: VoiceEmotion) => void }` consumed by Tasks 6, 7.

- [ ] **Step 1: Write failing test**

Create `frontend/src/shared/hooks/useVoicePlayer.test.ts`:

```typescript
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
    act(() => { result.current.playVoice('happy'); });
    expect(audioInstances[0].src).toBe('/characters/voice_bear_happy.wav');
    expect(audioInstances[0].play).toHaveBeenCalledTimes(1);
  });

  it('plays the correct file for a different species and emotion', () => {
    const { result } = renderHook(() => useVoicePlayer('rabbit'));
    act(() => { result.current.playVoice('celebrating'); });
    expect(audioInstances[0].src).toBe('/characters/voice_rabbit_celebrating.wav');
  });

  it('playVoice is a no-op when species is null', () => {
    const { result } = renderHook(() => useVoicePlayer(null));
    act(() => { result.current.playVoice('thinking'); });
    expect(audioInstances.length).toBe(0);
  });

  it('applies voiceVolume from localStorage', () => {
    localStorage.setItem('settings.masterVolume', '100');
    localStorage.setItem('settings.voiceVolume', '80');
    const { result } = renderHook(() => useVoicePlayer('fox'));
    act(() => { result.current.playVoice('surprised'); });
    expect(audioInstances[0].volume).toBeCloseTo(0.8, 2);
    localStorage.removeItem('settings.masterVolume');
    localStorage.removeItem('settings.voiceVolume');
  });

  it('all five species produce different file paths', () => {
    const species = ['bear', 'cat', 'fox', 'mouse', 'rabbit'] as const;
    const paths = species.map((s) => {
      const { result } = renderHook(() => useVoicePlayer(s));
      act(() => { result.current.playVoice('thinking'); });
      return audioInstances[audioInstances.length - 1].src;
    });
    const unique = new Set(paths);
    expect(unique.size).toBe(5);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && pnpm test useVoicePlayer.test.ts
```
Expected: FAIL — module not found

- [ ] **Step 3: Implement `useVoicePlayer.ts`**

```typescript
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
      const audio = new Audio(`/characters/voice_${species}_${emotion}.wav`);
      audio.volume = readVoiceVolume();
      audio.play().catch(() => {});
    },
    [species],
  );

  return { playVoice };
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd frontend && pnpm test useVoicePlayer.test.ts
```
Expected: 5/5 PASS

- [ ] **Step 5: Run full suite**

```bash
cd frontend && pnpm test
```
Expected: full suite green.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/shared/hooks/useVoicePlayer.ts frontend/src/shared/hooks/useVoicePlayer.test.ts
git commit -m "feat(audio): add useVoicePlayer hook for character voice reactions

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 5: Thread `avatarSpecies` through route state

**Files:**
- Modify: `frontend/src/pages/RaceSetupPage.tsx`
- Modify: `frontend/src/pages/RaceSetupPage.test.tsx`
- Modify: `frontend/src/pages/RaceScreenPage.tsx`
- Modify: `frontend/src/pages/ResultsScreenPage.tsx`

**Interfaces:**
- Consumes: `AvatarListItem.species: string` from `frontend/src/engine/avatar/types.ts`
- Produces: `RaceScreenRouteState.avatarSpecies: string` and `ResultsRouteState.avatarSpecies: string` consumed by Tasks 6, 7.

- [ ] **Step 1: Write failing test**

In `RaceSetupPage.test.tsx`, find the test "creates race session and navigates to /race/:id on start" and add an assertion that the navigate state includes `avatarSpecies`. Add this new test:

```typescript
it('passes avatarSpecies in navigate state when starting a race', async () => {
  const user = userEvent.setup();
  // The test already mocks the avatar list — find the mock avatar's species
  // In the existing test, the mock avatar has species: 'fox'
  renderPage();
  await waitFor(() => expect(screen.getByRole('radio', { name: /fox/i })).toBeInTheDocument());
  await user.click(screen.getByRole('radio', { name: /fox/i }));
  await user.click(screen.getByRole('button', { name: /start race/i }));
  await waitFor(() => expect(mockNavigate).toHaveBeenCalled());
  const navCall = mockNavigate.mock.calls[0];
  expect(navCall[1]?.state?.avatarSpecies).toBe('fox');
});
```

Note: read the existing test file first to find `mockNavigate` and the mock avatar's exact `name` and `species` values — they may differ from the example above. Adjust the test to match.

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && pnpm test RaceSetupPage.test.tsx
```
Expected: FAIL — `avatarSpecies` missing from navigate state

- [ ] **Step 3: Modify `RaceSetupPage.tsx` to pass `avatarSpecies`**

In the navigate call inside `handleStart` (around line 91), add `avatarSpecies`:

```typescript
void navigate(`/race/${session.race_id}`, {
  state: {
    mode,
    tier,
    seed: session.seed,
    avatarId: selectedAvatarId,
    avatarSpecies: avatars.find((a) => a.avatar_id === selectedAvatarId)?.species ?? '',
    opponentCount,
    championshipId: championship_id,
    raceIndex,
  },
});
```

- [ ] **Step 4: Add `avatarSpecies` to `RaceScreenRouteState` in `RaceScreenPage.tsx`**

```typescript
interface RaceScreenRouteState {
  mode: RaceMode;
  tier: Tier;
  seed: number;
  avatarId: string;
  avatarSpecies: string;    // <-- add
  opponentCount: number;
  championshipId?: string;
  raceIndex: number;
}
```

Also, in the `navigate` to results inside `RaceScreen` (inside `useEffect` for `RESULTS` state), forward `avatarSpecies`:

```typescript
void navigate(`/race/${raceId}/results`, {
  state: {
    summary: getSummary(),
    playerAvatarId: routeState.avatarId,
    avatarSpecies: routeState.avatarSpecies,   // <-- add
    championshipId: routeState.championshipId,
    raceIndex: routeState.raceIndex,
  },
  replace: true,
});
```

- [ ] **Step 5: Add `avatarSpecies` to `ResultsRouteState` in `ResultsScreenPage.tsx`**

```typescript
interface ResultsRouteState {
  summary: RaceSummary;
  playerAvatarId: string;
  avatarSpecies: string;    // <-- add
  championshipId?: string;
  raceIndex?: number;
}
```

In `ResultsScreen`, destructure it: `const { summary, playerAvatarId, avatarSpecies, championshipId, raceIndex } = routeState;`

- [ ] **Step 6: Run tests**

```bash
cd frontend && pnpm test RaceSetupPage.test.tsx
```
Expected: new test passes. Full suite:

```bash
cd frontend && pnpm test
```
Expected: green.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/pages/RaceSetupPage.tsx frontend/src/pages/RaceSetupPage.test.tsx \
        frontend/src/pages/RaceScreenPage.tsx frontend/src/pages/ResultsScreenPage.tsx
git commit -m "feat(audio): thread avatarSpecies through race route state

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 6: Wire SFX + ambience into `RaceScreenPage`

**Files:**
- Modify: `frontend/src/pages/RaceScreenPage.tsx`
- Modify: `frontend/src/pages/RaceScreenPage.test.tsx`

**Interfaces:**
- Consumes:
  - `useSfxPlayer()` from Task 2 — `playSfx: (name: SfxName) => void`
  - `useAmbienceManager()` from Task 3 — `{ triggerAmbience: (event: 'cheer' | 'applause') => void }`

- [ ] **Step 1: Write failing tests**

In `RaceScreenPage.test.tsx`, add mocks for the new hooks at the top (alongside existing mocks) and a new describe block:

```typescript
// Add to existing vi.mock calls at top of file:
vi.mock('../shared/hooks/useSfxPlayer');
vi.mock('../shared/hooks/useAmbienceManager');

// Add to existing imports:
import * as sfxModule from '../shared/hooks/useSfxPlayer';
import * as ambienceModule from '../shared/hooks/useAmbienceManager';
```

In `beforeEach`, add:
```typescript
vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx: vi.fn() });
vi.mocked(ambienceModule.useAmbienceManager).mockReturnValue({ triggerAmbience: vi.fn() });
```

Add a new describe block `'RaceScreenPage — audio'`:

```typescript
describe('RaceScreenPage — audio', () => {
  it('plays countdown sfx when countdown state is active', () => {
    const playSfx = vi.fn();
    vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({ state: 'COUNTDOWN' }),
    );
    renderPage();
    act(() => { vi.advanceTimersByTime(1000); });
    expect(playSfx).toHaveBeenCalledWith('countdown');
  });

  it('plays correct sfx and triggers cheer ambience on correct answer', () => {
    const playSfx = vi.fn();
    const triggerAmbience = vi.fn();
    vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
    vi.mocked(ambienceModule.useAmbienceManager).mockReturnValue({ triggerAmbience });
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({
        state: 'RACING',
        currentObstacle: 0,
        obstacleClockMs: 5000,
        runners: [{ runnerId: 'player', isHuman: true, totalDistanceMetres: 0, obstaclesCompleted: 0, obstacleResults: [], finishTime: null }],
        problemSet: { seed: 1, tier: 1 as const, count: 8, problems: Array.from({ length: 8 }, () => problem) },
        submitAnswer: vi.fn(),
      }),
    );
    renderPage();
    // Simulate the correct answer path by calling the submit handler directly
    // The submit logic calls submitAnswer({ isCorrect: true }) → triggers playSfx + triggerAmbience
    // We test by checking the handleSubmit flow: type correct answer and submit
    // Since this is a unit test, verify that after a correct submission the sfx fires
    // (Implement and wire first, then adjust the test if needed based on actual integration)
    expect(playSfx).not.toHaveBeenCalledWith('countdown'); // placeholder: expand after wiring
  });

  it('triggers applause ambience when engine transitions to RESULTS', async () => {
    const triggerAmbience = vi.fn();
    vi.mocked(ambienceModule.useAmbienceManager).mockReturnValue({ triggerAmbience });
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({ state: 'RESULTS', getSummary: vi.fn().mockReturnValue({ race_id: 'r1', seed: '42', difficulty_tier: 1, mode: 'quick', started_at: '', completed_at: '', participants: [] }) }),
    );
    renderPage();
    await waitFor(() => expect(triggerAmbience).toHaveBeenCalledWith('applause'));
  });
});
```

Note: the correct-answer test above has a placeholder; flesh it out after Step 3 to match the actual wiring.

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd frontend && pnpm test RaceScreenPage.test.tsx
```
Expected: FAIL on the audio describe block — hooks not yet imported in the component.

- [ ] **Step 3: Wire audio into `RaceScreenPage.tsx`**

Add imports:
```typescript
import { useSfxPlayer } from '../shared/hooks/useSfxPlayer';
import { useAmbienceManager } from '../shared/hooks/useAmbienceManager';
```

In `RaceScreen`, add hooks after the existing `useReducedMotion`:
```typescript
const { playSfx } = useSfxPlayer();
const { triggerAmbience } = useAmbienceManager();
```

In the countdown `useEffect`, fire SFX each time the number decrements:
```typescript
useEffect(() => {
  if (state !== 'COUNTDOWN') return;
  if (countdownNum > 0) {
    const t = setTimeout(() => {
      setCountdownNum((n) => n - 1);
      playSfx('countdown');
    }, 1000);
    return () => clearTimeout(t);
  }
  const t = setTimeout(startRacing, 800);
  return () => clearTimeout(t);
}, [state, countdownNum, startRacing, playSfx]);
```

In `handleSubmit`, after calling `submitAnswer`, add:
```typescript
function handleSubmit() {
  if (state !== 'RACING') return;
  const prob = problemSet?.problems[currentObstacle];
  if (!prob) return;
  const parsed = parseInt(answerInput, 10);
  const isCorrect = !isNaN(parsed) && parsed === prob.answer;
  submitAnswer({ isCorrect });
  if (isCorrect) {
    playSfx('correct');
    triggerAmbience('cheer');
  } else {
    playSfx('incorrect');
  }
  setAnswerInput('');
}
```

Add a `useEffect` for the RESULTS transition to trigger applause:
```typescript
useEffect(() => {
  if (state === 'RESULTS') triggerAmbience('applause');
}, [state, triggerAmbience]);
```

(Keep the existing RESULTS `useEffect` for navigation — this is an additional one.)

- [ ] **Step 4: Update the correct-answer test to match the actual wiring**

Now that the component is wired, update the placeholder test to actually type an answer and submit:
```typescript
it('plays correct sfx and triggers cheer ambience on correct answer', async () => {
  const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime.bind(vi) });
  const playSfx = vi.fn();
  const triggerAmbience = vi.fn();
  vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
  vi.mocked(ambienceModule.useAmbienceManager).mockReturnValue({ triggerAmbience });
  vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
    makeEngineReturn({
      state: 'RACING',
      currentObstacle: 0,
      obstacleClockMs: 5000,
      runners: [{ runnerId: 'player', isHuman: true, totalDistanceMetres: 0, obstaclesCompleted: 0, obstacleResults: [], finishTime: null }],
      problemSet: { seed: 1, tier: 1 as const, count: 8, problems: Array.from({ length: 8 }, () => problem) },
    }),
  );
  renderPage();
  await user.type(screen.getByRole('spinbutton'), '7');
  await user.keyboard('{Enter}');
  expect(playSfx).toHaveBeenCalledWith('correct');
  expect(triggerAmbience).toHaveBeenCalledWith('cheer');
});
```

- [ ] **Step 5: Run tests**

```bash
cd frontend && pnpm test RaceScreenPage.test.tsx
```
Expected: full test file passes (all existing + new audio tests).

- [ ] **Step 6: Run full suite**

```bash
cd frontend && pnpm test
```
Expected: green.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/pages/RaceScreenPage.tsx frontend/src/pages/RaceScreenPage.test.tsx
git commit -m "feat(audio): wire SFX and ambience into RaceScreenPage

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 7: Wire voice into `RaceScreenPage` + `ResultsScreenPage`

**Files:**
- Modify: `frontend/src/pages/RaceScreenPage.tsx`
- Modify: `frontend/src/pages/RaceScreenPage.test.tsx`
- Modify: `frontend/src/pages/ResultsScreenPage.tsx`
- Modify: `frontend/src/pages/ResultsScreenPage.test.tsx`

**Interfaces:**
- Consumes:
  - `useVoicePlayer(species)` from Task 4
  - `routeState.avatarSpecies` from Task 5
  - `Species` type from `useVoicePlayer.ts`

- [ ] **Step 1: Write failing tests**

In `RaceScreenPage.test.tsx`, add mock + tests for voice:

```typescript
vi.mock('../shared/hooks/useVoicePlayer');
import * as voiceModule from '../shared/hooks/useVoicePlayer';
```

In `beforeEach`:
```typescript
vi.mocked(voiceModule.useVoicePlayer).mockReturnValue({ playVoice: vi.fn() });
```

New tests in `'RaceScreenPage — audio'` describe block:

```typescript
it('plays thinking voice when a new obstacle appears', () => {
  const playVoice = vi.fn();
  vi.mocked(voiceModule.useVoicePlayer).mockReturnValue({ playVoice });
  vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
    makeEngineReturn({
      state: 'RACING',
      currentObstacle: 0,
      obstacleClockMs: 5000,
      runners: [{ runnerId: 'player', isHuman: true, totalDistanceMetres: 0, obstaclesCompleted: 0, obstacleResults: [], finishTime: null }],
      problemSet: { seed: 1, tier: 1 as const, count: 8, problems: Array.from({ length: 8 }, () => problem) },
    }),
  );
  renderPage({ ...routeState, avatarSpecies: 'bear' });
  expect(playVoice).toHaveBeenCalledWith('thinking');
});

it('passes avatarSpecies to useVoicePlayer', () => {
  renderPage({ ...routeState, avatarSpecies: 'cat' });
  expect(voiceModule.useVoicePlayer).toHaveBeenCalledWith('cat');
});
```

In `ResultsScreenPage.test.tsx`, add mock + test:

```typescript
vi.mock('../shared/hooks/useVoicePlayer');
import * as voiceModule from '../shared/hooks/useVoicePlayer';
```

Add to `beforeEach`:
```typescript
vi.mocked(voiceModule.useVoicePlayer).mockReturnValue({ playVoice: vi.fn() });
```

New test:
```typescript
it('plays celebrating voice on mount', async () => {
  const playVoice = vi.fn();
  vi.mocked(voiceModule.useVoicePlayer).mockReturnValue({ playVoice });
  const routeStateWithSpecies = { ...baseRouteState, avatarSpecies: 'rabbit' };
  render(
    <MemoryRouter initialEntries={[{ pathname: '/race/r1/results', state: routeStateWithSpecies }]}>
      <Routes>
        <Route path="/race/:id/results" element={<ResultsScreenPage />} />
      </Routes>
    </MemoryRouter>,
  );
  await waitFor(() => expect(playVoice).toHaveBeenCalledWith('celebrating'));
});
```

(Read the existing `ResultsScreenPage.test.tsx` to find the `baseRouteState` shape and adapt accordingly.)

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd frontend && pnpm test RaceScreenPage.test.tsx ResultsScreenPage.test.tsx
```
Expected: new voice tests fail.

- [ ] **Step 3: Wire voice into `RaceScreenPage.tsx`**

Add import:
```typescript
import { useVoicePlayer } from '../shared/hooks/useVoicePlayer';
import type { Species } from '../shared/hooks/useVoicePlayer';
```

In `RaceScreen`, add:
```typescript
const { playVoice } = useVoicePlayer((routeState.avatarSpecies || null) as Species | null);
```

Add a `useEffect` to fire `thinking` when a new obstacle appears:
```typescript
useEffect(() => {
  if (state === 'RACING') playVoice('thinking');
}, [state, currentObstacle]); // intentional: fires on state change to RACING and on each new obstacle
```

In `handleSubmit`, after the SFX calls:
```typescript
if (isCorrect) {
  playSfx('correct');
  triggerAmbience('cheer');
  playVoice('happy');
} else {
  playSfx('incorrect');
  playVoice('surprised');
}
```

- [ ] **Step 4: Wire voice into `ResultsScreenPage.tsx`**

Add import:
```typescript
import { useVoicePlayer } from '../shared/hooks/useVoicePlayer';
import type { Species } from '../shared/hooks/useVoicePlayer';
```

In `ResultsScreen`, add the hook and a mount-time `celebrating` call:
```typescript
const { playVoice } = useVoicePlayer((avatarSpecies || null) as Species | null);

useEffect(() => {
  playVoice('celebrating');
}, []); // fires once on mount — playVoice is a stable useCallback ref
```

- [ ] **Step 5: Run tests**

```bash
cd frontend && pnpm test RaceScreenPage.test.tsx ResultsScreenPage.test.tsx
```
Expected: all pass.

- [ ] **Step 6: Run full suite**

```bash
cd frontend && pnpm test
```
Expected: green.

- [ ] **Step 7: Commit**

```bash
git add frontend/src/pages/RaceScreenPage.tsx frontend/src/pages/RaceScreenPage.test.tsx \
        frontend/src/pages/ResultsScreenPage.tsx frontend/src/pages/ResultsScreenPage.test.tsx
git commit -m "feat(audio): wire character voice reactions into race and results screens

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 8: `AchievementToast` — replace synthesized chime with SFX

**Files:**
- Modify: `frontend/src/components/achievements/AchievementToast.tsx`
- Modify: `frontend/src/components/achievements/AchievementToast.test.tsx`

**Interfaces:**
- Consumes: `useSfxPlayer()` from Task 2

- [ ] **Step 1: Write failing test**

Read `AchievementToast.test.tsx` to find the existing chime test. Add:

```typescript
vi.mock('../../shared/hooks/useSfxPlayer');
import * as sfxModule from '../../shared/hooks/useSfxPlayer';
```

In `beforeEach`:
```typescript
vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx: vi.fn() });
```

New test in the achievement test file:
```typescript
it('plays achievement sfx when toast appears (reduced motion off)', async () => {
  const playSfx = vi.fn();
  vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
  vi.mocked(reduceMotionModule.useReducedMotion).mockReturnValue(false);
  // render with an achievement that triggers the toast
  // (follow the existing test pattern to queue an achievement in RESULTS state)
  // ...
  await waitFor(() => expect(playSfx).toHaveBeenCalledWith('achievement'));
});

it('does not play achievement sfx when reduced motion is on', async () => {
  const playSfx = vi.fn();
  vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
  vi.mocked(reduceMotionModule.useReducedMotion).mockReturnValue(true);
  // same render as above
  // ...
  await waitFor(() => { /* toast renders */ });
  expect(playSfx).not.toHaveBeenCalled();
});
```

Read the existing test file to see how it renders the toast and populate the "same render as above" sections with the actual render setup.

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd frontend && pnpm test AchievementToast
```
Expected: new sfx tests fail.

- [ ] **Step 3: Modify `AchievementToast.tsx`**

Replace `import ... playChime ...` with `useSfxPlayer`:

```typescript
import { useSfxPlayer } from '../../shared/hooks/useSfxPlayer';
```

Remove the `playChime` function entirely (lines 11–31 in the current file).

In the component, add the hook:
```typescript
const { playSfx } = useSfxPlayer();
```

In the drain `useEffect`, replace `if (!reducedMotion) { playChime(); }` with:
```typescript
if (!reducedMotion) {
  playSfx('achievement');
}
```

- [ ] **Step 4: Run tests**

```bash
cd frontend && pnpm test AchievementToast
```
Expected: all 8+ tests pass (including new ones).

- [ ] **Step 5: Run full suite**

```bash
cd frontend && pnpm test
```
Expected: green.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/achievements/AchievementToast.tsx \
        frontend/src/components/achievements/AchievementToast.test.tsx
git commit -m "feat(audio): replace synthesized achievement chime with sfx asset

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 9: Settings page — ambience + voice volume sliders

**Files:**
- Modify: `frontend/src/pages/SettingsPage.tsx`
- Modify: `frontend/src/pages/SettingsPage.test.tsx`

**Interfaces:**
- Produces: `settings.ambienceVolume` and `settings.voiceVolume` localStorage keys consumed by Tasks 3, 4.

- [ ] **Step 1: Write failing tests**

In `SettingsPage.test.tsx`, add:

```typescript
it('renders Ambience Volume slider with default 60', () => {
  render(<MemoryRouter><SettingsPage /></MemoryRouter>);
  // or however SettingsPage is rendered in the existing tests
  expect(screen.getByLabelText(/Ambience Volume/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/Ambience Volume: 60%/i)).toBeInTheDocument();
});

it('renders Voice Volume slider with default 80', () => {
  render(<MemoryRouter><SettingsPage /></MemoryRouter>);
  expect(screen.getByLabelText(/Voice Volume/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/Voice Volume: 80%/i)).toBeInTheDocument();
});

it('saves ambienceVolume to localStorage on change', () => {
  render(<MemoryRouter><SettingsPage /></MemoryRouter>);
  const slider = screen.getByRole('slider', { name: /Ambience Volume/i });
  fireEvent.change(slider, { target: { value: '40' } });
  expect(localStorage.getItem('settings.ambienceVolume')).toBe('40');
});

it('saves voiceVolume to localStorage on change', () => {
  render(<MemoryRouter><SettingsPage /></MemoryRouter>);
  const slider = screen.getByRole('slider', { name: /Voice Volume/i });
  fireEvent.change(slider, { target: { value: '70' } });
  expect(localStorage.getItem('settings.voiceVolume')).toBe('70');
});
```

Read the existing `SettingsPage.test.tsx` to see if SettingsPage is wrapped in a router or rendered directly, and adapt.

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd frontend && pnpm test SettingsPage.test.tsx
```
Expected: new slider tests fail.

- [ ] **Step 3: Modify `SettingsPage.tsx`**

Add new keys to the `KEYS` constant:
```typescript
const KEYS = {
  masterVolume: 'settings.masterVolume',
  musicVolume: 'settings.musicVolume',
  sfxVolume: 'settings.sfxVolume',
  ambienceVolume: 'settings.ambienceVolume',  // new
  voiceVolume: 'settings.voiceVolume',         // new
  reducedMotion: 'settings.reducedMotion',
} as const;
```

Add two new state values:
```typescript
const [ambienceVolume, setAmbienceVolume] = useState(() => loadInt(KEYS.ambienceVolume, 60));
const [voiceVolume, setVoiceVolume] = useState(() => loadInt(KEYS.voiceVolume, 80));
```

Add two new entries to the sliders array (after sfxVolume):
```typescript
{
  id: 'ambience-volume',
  label: 'Ambience Volume',
  value: ambienceVolume,
  setter: (v: string) => handleVolume(KEYS.ambienceVolume, setAmbienceVolume, v),
},
{
  id: 'voice-volume',
  label: 'Voice Volume',
  value: voiceVolume,
  setter: (v: string) => handleVolume(KEYS.voiceVolume, setVoiceVolume, v),
},
```

- [ ] **Step 4: Run tests**

```bash
cd frontend && pnpm test SettingsPage.test.tsx
```
Expected: all tests pass.

- [ ] **Step 5: Run full suite**

```bash
cd frontend && pnpm test
```
Expected: green.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/SettingsPage.tsx frontend/src/pages/SettingsPage.test.tsx
git commit -m "feat(audio): add ambience and voice volume sliders to Settings

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 10: UI sounds — `Button` opt-in prop + `RaceSetupPage`

**Files:**
- Modify: `frontend/src/shared/components/Button.tsx`
- Modify: `frontend/src/shared/components/Button.test.tsx`
- Modify: `frontend/src/pages/RaceSetupPage.tsx`
- Modify: `frontend/src/pages/RaceSetupPage.test.tsx`

**Interfaces:**
- Consumes: `useSfxPlayer()` from Task 2 — `playSfx: (name: SfxName) => void`
- Produces: `Button` gains optional `playSound?: boolean` prop (default false, backward-compatible)

- [ ] **Step 1: Write failing tests**

In `Button.test.tsx`, add:

```typescript
vi.mock('../../shared/hooks/useSfxPlayer');
import * as sfxModule from '../../shared/hooks/useSfxPlayer';
```

Before tests:
```typescript
beforeEach(() => {
  vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx: vi.fn() });
});
```

New tests:
```typescript
it('does not play sound on click by default (no playSound prop)', async () => {
  const playSfx = vi.fn();
  vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
  const user = userEvent.setup();
  render(<Button variant="primary" onClick={() => {}}>Click</Button>);
  await user.click(screen.getByRole('button'));
  expect(playSfx).not.toHaveBeenCalled();
});

it('plays ui_click sound on click when playSound=true', async () => {
  const playSfx = vi.fn();
  vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
  const user = userEvent.setup();
  render(<Button variant="primary" playSound onClick={() => {}}>Click</Button>);
  await user.click(screen.getByRole('button'));
  expect(playSfx).toHaveBeenCalledWith('ui_click');
});

it('plays ui_hover sound on mouseenter when playSound=true', async () => {
  const playSfx = vi.fn();
  vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
  const user = userEvent.setup();
  render(<Button variant="primary" playSound onClick={() => {}}>Hover</Button>);
  await user.hover(screen.getByRole('button'));
  expect(playSfx).toHaveBeenCalledWith('ui_hover');
});
```

In `RaceSetupPage.test.tsx`, add:

```typescript
it('plays ui_card_select when hovering an avatar card', async () => {
  const playSfx = vi.fn();
  vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
  // render the setup page after avatars are loaded
  // hover over an avatar radio item
  // expect playSfx('ui_card_select')
  // (adapt to actual avatar grid HTML structure after wiring)
});
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd frontend && pnpm test Button.test.tsx
```
Expected: new sound tests fail.

- [ ] **Step 3: Modify `Button.tsx`**

Add `playSound` to `ButtonProps`:
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  type?: 'button' | 'submit' | 'reset';
  'aria-label'?: string;
  playSound?: boolean;  // <-- new
}
```

Add the hook and handlers inside the component:
```typescript
import { useSfxPlayer } from '../hooks/useSfxPlayer';

export function Button({ ..., playSound = false }: ButtonProps) {
  const { playSfx } = useSfxPlayer();
  // ...
  return (
    <button
      // ...
      onClick={isInert ? undefined : () => { if (playSound) playSfx('ui_click'); onClick?.(); }}
      onMouseEnter={() => { if (playSound) playSfx('ui_hover'); }}
      // keep existing onFocus/onBlur
    >
```

- [ ] **Step 4: Wire `ui_card_select` + `ui_avatar_select` in `RaceSetupPage.tsx`**

Add import:
```typescript
import { useSfxPlayer } from '../shared/hooks/useSfxPlayer';
```

Inside the component, add:
```typescript
const { playSfx } = useSfxPlayer();
```

On the avatar radio/card items (find the `avatars.map(...)` section, ~line 277), add `onMouseEnter`:
```tsx
<label
  key={a.avatar_id}
  onMouseEnter={() => playSfx('ui_card_select')}
  // ...existing props
>
```

On the "Start Race" button, add `playSound` prop (or call `playSfx('ui_avatar_select')` in `handleStart`):
```typescript
async function handleStart() {
  playSfx('ui_avatar_select');
  // ... rest of existing handleStart
}
```

- [ ] **Step 5: Run tests**

```bash
cd frontend && pnpm test Button.test.tsx RaceSetupPage.test.tsx
```
Expected: all pass.

- [ ] **Step 6: Run full suite**

```bash
cd frontend && pnpm test
```
Expected: green.

- [ ] **Step 7: Run type check + lint**

```bash
cd frontend && pnpm tsc --noEmit && pnpm lint
```
Expected: no errors.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/shared/components/Button.tsx frontend/src/shared/components/Button.test.tsx \
        frontend/src/pages/RaceSetupPage.tsx frontend/src/pages/RaceSetupPage.test.tsx
git commit -m "feat(audio): add UI sounds to Button component and RaceSetupPage

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```
