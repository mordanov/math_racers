import { useCallback, useEffect, useRef, useState } from 'react';
import { createRaceEngine } from '../raceEngine';
import type { ObstacleResult, RaceConfig, RaceEngineState, RaceSummary } from '../types';

export function useRaceEngine(config: RaceConfig) {
  const engineRef = useRef(createRaceEngine(config));
  const rafRef = useRef<number | null>(null);
  const [snapshot, setSnapshot] = useState<RaceEngineState>(() => engineRef.current.getState());

  useEffect(() => {
    const engine = engineRef.current;

    function loop(timestamp: number) {
      engine.tick(timestamp);
      setSnapshot(engine.getState());
      rafRef.current = requestAnimationFrame(loop);
    }

    rafRef.current = requestAnimationFrame(loop);

    function onVisibility() {
      if (document.hidden) engine.pause();
      else engine.resume();
    }

    document.addEventListener('visibilitychange', onVisibility);

    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
      document.removeEventListener('visibilitychange', onVisibility);
    };
  }, []);

  const startCountdown = useCallback(() => {
    engineRef.current.transition('LOBBY');
    engineRef.current.transition('COUNTDOWN');
  }, []);

  const startRacing = useCallback(() => {
    engineRef.current.transition('RACING');
  }, []);

  const submitAnswer = useCallback(
    (input: { answer: string }): ObstacleResult => engineRef.current.submitAnswer(input),
    [],
  );

  const forceComplete = useCallback(() => engineRef.current.forceComplete(), []);

  const getSummary = useCallback((): RaceSummary => engineRef.current.getSummary(), []);

  return { ...snapshot, startCountdown, startRacing, submitAnswer, forceComplete, getSummary };
}
