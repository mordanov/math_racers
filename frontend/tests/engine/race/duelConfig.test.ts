// @vitest-environment node
import { describe, expect, it } from 'vitest';
import { buildDuelConfig } from '../../../src/engine/race/duelConfig';

describe('buildDuelConfig', () => {
  it('returns exactly one AI participant', () => {
    const { aiParticipants } = buildDuelConfig(3);
    expect(aiParticipants).toHaveLength(1);
    expect(aiParticipants[0].isHuman).toBe(false);
  });

  it('selects Balanced personality (id: balanced)', () => {
    const { aiParticipants } = buildDuelConfig(3);
    expect(aiParticipants[0].personality?.id).toBe('balanced');
  });

  it('tier offset is 0', () => {
    const { aiParticipants } = buildDuelConfig(3);
    expect(aiParticipants[0].personality?.tierOffset).toBe(0);
  });

  it('tier matches playerTier for mid-range values', () => {
    for (const tier of [1, 2, 3, 4, 5, 6] as const) {
      expect(buildDuelConfig(tier).tier).toBe(tier);
    }
  });

  it('clamps tier to minimum 1 when player tier is below 1', () => {
    expect(buildDuelConfig(0).tier).toBe(1);
    expect(buildDuelConfig(-5).tier).toBe(1);
  });

  it('clamps tier to maximum 6 when player tier is above 6', () => {
    expect(buildDuelConfig(7).tier).toBe(6);
    expect(buildDuelConfig(100).tier).toBe(6);
  });

  it('returns distinct config objects on each call (no shared reference)', () => {
    const a = buildDuelConfig(2);
    const b = buildDuelConfig(2);
    expect(a.aiParticipants[0]).not.toBe(b.aiParticipants[0]);
  });
});
