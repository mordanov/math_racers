import React, { useEffect, useRef, useState } from 'react';
import type { Achievement } from '../../engine/achievements/types';
import type { RaceState } from '../../engine/race/types';
import { useSfxPlayer } from '../../shared/hooks/useSfxPlayer';
import { useReducedMotion } from '../../shared/hooks/useReducedMotion';
import { useLocale } from '../../infrastructure/localization/LocaleContext';
import { getAchievementTranslationKeys } from '../../infrastructure/localization/formatters';

interface Props {
  achievements: Achievement[];
  raceState: RaceState;
}

const ANIMATION_DURATION_MS = 2000;
const GAP_BETWEEN_MS = 2000;

export function AchievementToast({ achievements, raceState }: Props): React.ReactElement | null {
  const [queue, setQueue] = useState<Achievement[]>([]);
  const [current, setCurrent] = useState<Achievement | null>(null);
  const [animating, setAnimating] = useState(false);
  const reducedMotion = useReducedMotion();
  const { playSfx } = useSfxPlayer();
  const { t } = useLocale();
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
      playSfx('achievement');
    }

    const displayTimer = setTimeout(() => {
      setAnimating(false);
      setCurrent(null);
      draining.current = false;
    }, ANIMATION_DURATION_MS + GAP_BETWEEN_MS);

    return () => clearTimeout(displayTimer);
  }, [queue, raceState, reducedMotion]);

  if (raceState !== 'RESULTS' || current === null) return null;
  const translation = getAchievementTranslationKeys(current.key);
  const title = translation ? t(translation.title) : current.title;
  const description = translation ? t(translation.description) : current.description;

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
        <img src={`/${current.icon_path}`} alt={title} className="achievement-icon" />
        <div className="achievement-text">
          <span className="achievement-title">{title}</span>
          <span className="achievement-description">{description}</span>
        </div>
      </div>
    </div>
  );
}
