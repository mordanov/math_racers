import type { RaceState } from './types';

export class RaceStateError extends Error {
  constructor(from: RaceState, to: RaceState) {
    super(`Illegal race state transition: ${from} → ${to}`);
    this.name = 'RaceStateError';
  }
}

const LEGAL_TRANSITIONS: Record<RaceState, Set<RaceState>> = {
  IDLE: new Set(['LOBBY']),
  LOBBY: new Set(['COUNTDOWN']),
  COUNTDOWN: new Set(['RACING']),
  RACING: new Set(['FINISHING']),
  FINISHING: new Set(['RESULTS']),
  RESULTS: new Set(['LOBBY']),
};

export function transition(from: RaceState, to: RaceState): void {
  if (!LEGAL_TRANSITIONS[from].has(to)) {
    throw new RaceStateError(from, to);
  }
}
