// @vitest-environment node
import { describe, expect, it } from 'vitest';
import { RaceStateError, transition } from '../../../src/engine/race/stateMachine';

describe('transition — legal paths', () => {
  it('allows IDLE → LOBBY', () => {
    expect(() => transition('IDLE', 'LOBBY')).not.toThrow();
  });
  it('allows LOBBY → COUNTDOWN', () => {
    expect(() => transition('LOBBY', 'COUNTDOWN')).not.toThrow();
  });
  it('allows COUNTDOWN → RACING', () => {
    expect(() => transition('COUNTDOWN', 'RACING')).not.toThrow();
  });
  it('allows RACING → FINISHING', () => {
    expect(() => transition('RACING', 'FINISHING')).not.toThrow();
  });
  it('allows FINISHING → RESULTS', () => {
    expect(() => transition('FINISHING', 'RESULTS')).not.toThrow();
  });
  it('allows RESULTS → LOBBY', () => {
    expect(() => transition('RESULTS', 'LOBBY')).not.toThrow();
  });
});

describe('transition — illegal paths (spec examples)', () => {
  it('rejects IDLE → RACING', () => {
    expect(() => transition('IDLE', 'RACING')).toThrow(RaceStateError);
  });
  it('rejects RESULTS → RACING', () => {
    expect(() => transition('RESULTS', 'RACING')).toThrow(RaceStateError);
  });
  it('rejects COUNTDOWN → IDLE', () => {
    expect(() => transition('COUNTDOWN', 'IDLE')).toThrow(RaceStateError);
  });
  it('rejects RACING → LOBBY', () => {
    expect(() => transition('RACING', 'LOBBY')).toThrow(RaceStateError);
  });
  it('rejects IDLE → RESULTS', () => {
    expect(() => transition('IDLE', 'RESULTS')).toThrow(RaceStateError);
  });
  it('rejects self-transitions (IDLE → IDLE)', () => {
    expect(() => transition('IDLE', 'IDLE')).toThrow(RaceStateError);
  });
});

describe('transition — error details', () => {
  it('throws RaceStateError with message naming the states', () => {
    let caught: unknown;
    try {
      transition('IDLE', 'RACING');
    } catch (e) {
      caught = e;
    }
    expect(caught).toBeInstanceOf(RaceStateError);
    expect((caught as RaceStateError).message).toContain('IDLE');
    expect((caught as RaceStateError).message).toContain('RACING');
  });
});
