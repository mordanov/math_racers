import { useState } from 'react';
import tokens from '../shared/tokens';

const KEYS = {
  masterVolume: 'settings.masterVolume',
  musicVolume: 'settings.musicVolume',
  sfxVolume: 'settings.sfxVolume',
  ambienceVolume: 'settings.ambienceVolume',
  voiceVolume: 'settings.voiceVolume',
  reducedMotion: 'settings.reducedMotion',
} as const;

function loadInt(key: string, fallback: number): number {
  try {
    const v = localStorage.getItem(key);
    if (v === null) return fallback;
    const n = parseInt(v, 10);
    return isNaN(n) ? fallback : n;
  } catch {
    return fallback;
  }
}

function loadBool(key: string, fallback: boolean): boolean {
  try {
    const v = localStorage.getItem(key);
    if (v === null) return fallback;
    return v === 'true';
  } catch {
    return fallback;
  }
}

function saveKey(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch {
    // localStorage unavailable (private mode, storage full) — silently ignore
  }
}

export default function SettingsPage() {
  const [masterVolume, setMasterVolume] = useState(() => loadInt(KEYS.masterVolume, 80));
  const [musicVolume, setMusicVolume] = useState(() => loadInt(KEYS.musicVolume, 70));
  const [sfxVolume, setSfxVolume] = useState(() => loadInt(KEYS.sfxVolume, 80));
  const [ambienceVolume, setAmbienceVolume] = useState(() => loadInt(KEYS.ambienceVolume, 60));
  const [voiceVolume, setVoiceVolume] = useState(() => loadInt(KEYS.voiceVolume, 80));
  const [reducedMotion, setReducedMotion] = useState(() => loadBool(KEYS.reducedMotion, false));

  function handleVolume(key: string, setter: (v: number) => void, value: string) {
    const n = parseInt(value, 10);
    setter(n);
    saveKey(key, value);
  }

  function handleReducedMotion(checked: boolean) {
    setReducedMotion(checked);
    saveKey(KEYS.reducedMotion, String(checked));
  }

  return (
    <div
      data-testid="page-settings"
      style={{ maxWidth: 500, margin: '0 auto', padding: tokens.spacing.xl }}
    >
      <h1 style={{ fontSize: 28, fontWeight: 900, marginBottom: tokens.spacing.lg }}>Settings</h1>

      <section aria-label="Audio settings" style={{ marginBottom: tokens.spacing.xl }}>
        <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: tokens.spacing.md }}>Audio</h2>
        {[
          {
            id: 'master-volume',
            label: 'Master Volume',
            value: masterVolume,
            setter: (v: string) => handleVolume(KEYS.masterVolume, setMasterVolume, v),
          },
          {
            id: 'music-volume',
            label: 'Music Volume',
            value: musicVolume,
            setter: (v: string) => handleVolume(KEYS.musicVolume, setMusicVolume, v),
          },
          {
            id: 'sfx-volume',
            label: 'SFX Volume',
            value: sfxVolume,
            setter: (v: string) => handleVolume(KEYS.sfxVolume, setSfxVolume, v),
          },
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
        ].map(({ id, label, value, setter }) => (
          <div key={id} style={{ marginBottom: tokens.spacing.md }}>
            <label
              htmlFor={id}
              style={{
                display: 'block',
                marginBottom: tokens.spacing.xs,
                fontWeight: 600,
                fontSize: 14,
              }}
            >
              {label}: {value}%
            </label>
            <input
              id={id}
              type="range"
              min={0}
              max={100}
              value={value}
              onChange={(e) => setter(e.target.value)}
              style={{ width: '100%', accentColor: tokens.color.primary }}
            />
          </div>
        ))}
      </section>

      <section aria-label="Accessibility settings">
        <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: tokens.spacing.md }}>
          Accessibility
        </h2>
        <label
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: tokens.spacing.sm,
            cursor: 'pointer',
          }}
        >
          <input
            type="checkbox"
            aria-label="Reduce motion"
            checked={reducedMotion}
            onChange={(e) => handleReducedMotion(e.target.checked)}
          />
          <span>Reduce motion</span>
        </label>
      </section>
    </div>
  );
}
