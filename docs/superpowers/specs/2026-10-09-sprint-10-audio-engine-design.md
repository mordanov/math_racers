# Sprint 10: Full Audio Engine

**Date:** 2026-10-09
**Branch:** `worktree-014-sprint-6-ui-polish`
**Status:** Approved design — ready for implementation planning

---

## Problem Statement

The game has a working music layer (`useAudioManager`) but it picks tracks randomly instead of playing them sequentially, and the three remaining audio layers (SFX, ambience, character voices) do not exist yet. Sound effects are synthesized (achievement chime only). UI sounds, crowd ambience, and character voice reactions are absent entirely.

All audio assets are present in `assets/` (Vite `publicDir`, so served directly):
- `assets/audio/` — `music_menu_1.wav`, `music_menu_2.wav`, `music_race_1.wav`, `music_race_2.wav`, `music_victory_1.wav`, `music_victory_2.wav`
- `assets/gameplay_sounds/` — 7 MP3s: `sfx_correct`, `sfx_incorrect`, `sfx_countdown`, `sfx_achievement`, `sfx_levelup`, `sfx_obstacle_hit`, `sfx_obstacle_jump`
- `assets/ui_sounds/` — 6 MP3s: `ui_click`, `ui_hover`, `ui_window_open`, `ui_window_close`, `ui_card_select`, `ui_avatar_select`
- `assets/ambience/` — `ambience_crowd_baseline.wav`, `ambience_crowd_cheer_short.wav`, `ambience_crowd_applause.flac`
- `assets/characters/` — 20 WAVs: `voice_{bear,cat,fox,mouse,rabbit}_{celebrating,happy,surprised,thinking}`

---

## Section 1: Architecture

Four focused hooks, all in `frontend/src/shared/hooks/`:

| Hook | Responsibility |
|---|---|
| `useAudioManager` (extend) | Music only — sequential track playback |
| `useSfxPlayer` (new) | Gameplay + UI one-shot sounds |
| `useAmbienceManager` (new) | Crowd baseline loop + triggered crowd events |
| `useVoicePlayer` (new) | Character voice reactions |

This keeps each hook under ~60 lines and independently testable. Cross-layer coordination (e.g., duck music under voice) is not needed and not added.

All hooks compute effective volume as `masterVolume × layerVolume` where both are integers 0–100 from localStorage.

---

## Section 2: Sequential Music (`useAudioManager`)

**Current behaviour:** random track selection, loop on non-victory.

**New behaviour:**

1. `playMusic(track)` creates `Audio` for `TRACK_FILES[track][0]`.
2. On `ended`, creates `Audio` for `TRACK_FILES[track][1]`.
3. On `ended` of index 1:
   - If `track !== 'victory'`: loop back to index 0.
   - If `track === 'victory'`: stop (no loop).
4. `stopMusic()` behaviour unchanged — pause + reset currentTime.

**API unchanged.** Callers (`HomePage`, `RaceScreenPage`, `ResultsScreenPage`) require no changes.

The current `audio.loop = track !== 'victory'` is removed in favour of the `ended` handler chain.

---

## Section 3: SFX + UI Sounds (`useSfxPlayer`)

```typescript
type SfxName =
  | 'correct' | 'incorrect' | 'countdown' | 'achievement'
  | 'levelup' | 'obstacle_hit' | 'obstacle_jump'
  | 'ui_click' | 'ui_hover' | 'ui_window_open' | 'ui_window_close'
  | 'ui_card_select' | 'ui_avatar_select';

// Returns:
interface SfxPlayer {
  playSfx: (name: SfxName) => void;
}
```

- Each call creates a fresh `new Audio(path)` for true one-shot overlap.
- Volume = `(masterVolume / 100) × (sfxVolume / 100)`. Reads from localStorage at call time (not at hook mount), so volume slider changes take effect immediately.
- No loop. No cleanup ref needed (one-shot Audio GCs after playback).
- Silent failure on autoplay block (`.catch(() => {})`).

**File map** (served paths):
```typescript
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
```

**Call sites:**

| Sound | Where | Trigger |
|---|---|---|
| `countdown` | `RaceScreenPage` | countdown timer reaches each number |
| `correct` | `RaceScreenPage` | correct answer submitted |
| `incorrect` | `RaceScreenPage` | wrong answer submitted |
| `obstacle_hit` / `obstacle_jump` | `RaceScreenPage` | not in scope — obstacle interaction not implemented yet; **deferred** |
| `achievement` | `AchievementToast` | replaces existing synthesized chime (`playChime`) |
| `levelup` | `ResultsScreenPage` | when a level-up is detected |
| `ui_click` | `Button` component | on click, opt-in via `playSound?: boolean` prop (default false) |
| `ui_hover` | `Button` component | on mouseenter, same opt-in prop |
| `ui_window_open` / `ui_window_close` | `ConfirmDialog` | on open/close |
| `ui_card_select` | `RaceSetupPage` avatar grid | on avatar hover |
| `ui_avatar_select` | `RaceSetupPage` | on avatar select (confirm button) |

`Button` gets a `playSound?: boolean` prop. When true, it imports `useSfxPlayer` and fires `ui_click`/`ui_hover`. Existing `Button` usage is unaffected (default false).

---

## Section 4: Ambience (`useAmbienceManager`)

Used in `RaceScreenPage` only.

```typescript
interface AmbienceManager {
  triggerAmbience: (event: 'cheer' | 'applause') => void;
}
```

- **Mount**: starts `ambience_crowd_baseline.wav` looping (`audio.loop = true`).
- **Unmount**: stops and clears baseline audio.
- `triggerAmbience('cheer')`: fires `ambience_crowd_cheer_short.wav` (one-shot, overlapping baseline).
- `triggerAmbience('applause')`: fires `ambience_crowd_applause.flac` (one-shot).
- Volume = `(masterVolume / 100) × (ambienceVolume / 100)`. New localStorage key: `settings.ambienceVolume`, default 60.

**Call sites in `RaceScreenPage`:**
- `cheer`: when `submitAnswer({ isCorrect: true })` is called.
- `applause`: when engine state transitions to `RESULTS`.

---

## Section 5: Character Voices (`useVoicePlayer`)

```typescript
type Species = 'bear' | 'cat' | 'fox' | 'mouse' | 'rabbit';
type VoiceEmotion = 'thinking' | 'happy' | 'surprised' | 'celebrating';

function useVoicePlayer(species: Species | null): {
  playVoice: (emotion: VoiceEmotion) => void;
}
```

- Creates `new Audio(path)` per call (one-shot).
- Volume = `(masterVolume / 100) × (voiceVolume / 100)`. New localStorage key: `settings.voiceVolume`, default 80.
- Returns a no-op `playVoice` when `species` is null.

**File map** pattern: `/characters/voice_${species}_${emotion}.wav`

**Emotion triggers:**

| Emotion | Trigger | Where |
|---|---|---|
| `thinking` | Each new obstacle question (currentObstacle increments while state === 'RACING') | `RaceScreenPage` |
| `happy` | Correct answer submitted | `RaceScreenPage` |
| `surprised` | Wrong answer submitted | `RaceScreenPage` |
| `celebrating` | Player reached RESULTS (finished race) | `ResultsScreenPage` |

### Route state change

`useVoicePlayer` takes a `species`, not an `avatarId`. The species must be threaded from the avatar selection into the race flow.

**`RaceSetupPage`:** At navigation time, look up the selected avatar from the gallery list and add `avatarSpecies: string` to the route state:
```typescript
// navigation payload addition:
avatarSpecies: selectedAvatar.species,
```

**`RaceScreenRouteState`** (in `RaceScreenPage.tsx`): add `avatarSpecies: string`.

**`ResultsScreenRouteState`** (in `ResultsScreenPage.tsx`): add `avatarSpecies: string`.

**Navigate from `RaceScreenPage` to results**: forward `avatarSpecies` in the navigate state.

---

## Section 6: Settings Page — New Volume Sliders

Two new sliders added below the existing "SFX Volume" slider, following the exact same pattern (label, range input, percentage display):

| Key | Label | localStorage key | Default |
|---|---|---|---|
| `ambienceVolume` | Ambience Volume | `settings.ambienceVolume` | 60 |
| `voiceVolume` | Voice Volume | `settings.voiceVolume` | 80 |

`useAmbienceManager` and `useVoicePlayer` read the `storage` event (same pattern as `useAudioManager`'s volume listener) so sliders take effect immediately without a page reload.

---

## Section 7: What is NOT in scope

- Obstacle hit/jump sounds: obstacle interaction is not yet implemented in game logic. `sfx_obstacle_hit` and `sfx_obstacle_jump` exist in the map but have no call site. They are deferred.
- Audio ducking (lowering music when voice plays): not requested, not added.
- Cross-tab volume sync for new layers: the `storage` event listener covers this identically to the existing music layer.
- Hetzner Object Storage: `generation_service.py` already uses `cfg.STORAGE_ENDPOINT` generically (S3-compatible). No code changes needed — the user updates `.env` only.

---

## Testing Strategy

All hooks in `frontend/src/shared/hooks/`. Tests use `vi.hoisted()` stubs for `Audio` (existing pattern from `HomePageAudio.test.tsx`).

- `useAudioManager.test.ts`: extend existing tests — add sequential playback tests (watch `ended` fire, verify second track plays, verify loop back on non-victory, verify no loop on victory).
- `useSfxPlayer.test.ts`: verify `playSfx(name)` creates Audio with correct path; verify volume calculation; verify a second call creates a second Audio (not the same ref).
- `useAmbienceManager.test.ts`: verify baseline starts on mount, stops on unmount; verify `triggerAmbience` creates correct one-shot Audio.
- `useVoicePlayer.test.ts`: verify correct file path from species + emotion; verify no-op when species is null.
- `SettingsPage.test.tsx`: add tests for new sliders present with correct labels and defaults.
- `RaceScreenPage.test.tsx`: extend to verify SFX, ambience, voice calls on correct events.
- `ResultsScreenPage.test.tsx`: extend to verify `celebrating` voice on mount.
