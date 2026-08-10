import { useCallback, useEffect, useRef, useState } from 'react';
import { postRaceSummary } from '../raceApi';
import { createRaceEngine } from '../raceEngine';
import type { ObstacleResult, RaceConfig, RaceEngineState } from '../types';

type SummaryStatus = 'idle' | 'pending' | 'saved' | 'error';

export function useRaceEngine(config: RaceConfig) {
  const engineRef = useRef(createRaceEngine(config));
  const rafRef = useRef<number | null>(null);
  const [snapshot, setSnapshot] = useState<RaceEngineState>(() => engineRef.current.getState());
  const [summaryStatus, setSummaryStatus] = useState<SummaryStatus>('idle');
  const summaryPostedRef = useRef(false);

  useEffect(() => {
    const engine = engineRef.current;

    function loop(timestamp: number) {
      engine.tick(timestamp);
      const state = engine.getState();
      setSnapshot(state);

      if (state.state === 'RESULTS' && !summaryPostedRef.current) {
        summaryPostedRef.current = true;
        setSummaryStatus('pending');
        postRaceSummary(engine.getSummary())
          .then(() => setSummaryStatus('saved'))
          .catch(() => setSummaryStatus('error'));
      }

      rafRef.current = requestAnimationFrame(loop);
    }

    rafRef.current = requestAnimationFrame(loop);

    function onVisibility() {
      if (document.hidden) {
        engine.pause();
      } else {
        engine.resume();
      }
    }

    document.addEventListener('visibilitychange', onVisibility);

    return () => {
      if (rafRef.current !== null) cancelAnimationFrame(rafRef.current);
      document.removeEventListener('visibilitychange', onVisibility);
    };
  }, []);

  const submitAnswer = useCallback(
    (input: { isCorrect: boolean }): ObstacleResult => engineRef.current.submitAnswer(input),
    [],
  );

  return { ...snapshot, submitAnswer, summaryStatus };
}
