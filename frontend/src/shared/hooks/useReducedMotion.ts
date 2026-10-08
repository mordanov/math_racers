import { useEffect, useState } from 'react';

function readReducedMotion(): boolean {
  const mq =
    typeof window !== 'undefined' && typeof window.matchMedia === 'function'
      ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
      : false;
  let ls = false;
  try {
    ls = localStorage.getItem('settings.reducedMotion') === 'true';
  } catch {
    // localStorage unavailable
  }
  return mq || ls;
}

export function useReducedMotion(): boolean {
  const [reduced, setReduced] = useState(readReducedMotion);

  useEffect(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return;
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    const handleMq = () => setReduced(readReducedMotion());
    const handleStorage = (e: StorageEvent) => {
      if (e.key === 'settings.reducedMotion') setReduced(readReducedMotion());
    };
    mq.addEventListener('change', handleMq);
    window.addEventListener('storage', handleStorage);
    return () => {
      mq.removeEventListener('change', handleMq);
      window.removeEventListener('storage', handleStorage);
    };
  }, []);

  return reduced;
}
