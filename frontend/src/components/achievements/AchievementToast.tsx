import React, { useEffect, useRef, useState } from 'react';
import type { Achievement } from '../../engine/achievements/types';
import type { RaceState } from '../../engine/race/types';

interface Props {
  achievements: Achievement[];
  raceState: RaceState;
}

function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(
    () => window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  );
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handler = (e: MediaQueryListEvent) => setReduced(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);
  return reduced;
}

function playChime(): void {
  try {
    const ctx = new AudioContext();
    const notes = [523.25, 659.25, 783.99]; // C5, E5, G5
    notes.forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.value = freq;
      osc.type = 'sine';
      const start = ctx.currentTime + i * 0.15;
      gain.gain.setValueAtTime(0.3, start);
      gain.gain.exponentialRampToValueAtTime(0.001, start + 0.3);
      osc.start(start);
      osc.stop(start + 0.4);
    });
  } catch {
    // AudioContext not available in test environments
  }
}

const ANIMATION_DURATION_MS = 2000;
const GAP_BETWEEN_MS = 2000;

export function AchievementToast({ achievements, raceState }: Props): React.ReactElement | null {
  const [queue, setQueue] = useState<Achievement[]>([]);
  const [current, setCurrent] = useState<Achievement | null>(null);
  const [animating, setAnimating] = useState(false);
  const reducedMotion = useReducedMotion();
  const draining = useRef(false);

  // Load new achievements into queue when they arrive
  useEffect(() => {
    if (achievements.length > 0) {
      setQueue((prev) => [...prev, ...achievements]);
    }
  }, [achievements]);

  // Drain queue one at a time, only when in RESULTS state
  useEffect(() => {
    if (raceState !== 'RESULTS' || draining.current || queue.length === 0) return;

    draining.current = true;
    const next = queue[0];
    setQueue((prev) => prev.slice(1));
    setCurrent(next);
    setAnimating(true);

    if (!reducedMotion) {
      playChime();
    }

    const displayTimer = setTimeout(() => {
      setAnimating(false);
      setCurrent(null);
      draining.current = false;
    }, ANIMATION_DURATION_MS + GAP_BETWEEN_MS);

    return () => clearTimeout(displayTimer);
  }, [queue, raceState, reducedMotion]);

  if (raceState !== 'RESULTS' || current === null) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className={`achievement-toast${animating && !reducedMotion ? ' achievement-toast--animating' : ''}`}
    >
      <div
        className={`achievement-badge${animating && !reducedMotion ? ' achievement-badge--bounce' : ''}`}
      >
        {animating && !reducedMotion && <span className="achievement-sparkle" aria-hidden="true" />}
        <img src={`/${current.icon_path}`} alt={current.title} className="achievement-icon" />
        <div className="achievement-text">
          <span className="achievement-title">{current.title}</span>
          <span className="achievement-description">{current.description}</span>
        </div>
      </div>
    </div>
  );
}
