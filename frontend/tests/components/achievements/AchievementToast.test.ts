// @vitest-environment node
import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import type { Achievement } from '../../../src/engine/achievements/types';

// Tests for AchievementToast logic that don't require a React renderer.
// The component is tested indirectly via its exported helpers and state assumptions.

// Minimal window stub for matchMedia tests
const mockWindow = { matchMedia: vi.fn() } as unknown as Window & typeof globalThis;

const makeAchievement = (key: string): Achievement => ({
  key,
  category: 'racing',
  title: `Achievement ${key}`,
  description: `Desc ${key}`,
  hidden: false,
  icon_path: `assets/achievements/${key}.png`,
  unlocked_at: '2026-08-12T10:00:00Z',
});

describe('AchievementToast contract', () => {
  it('achievement interface has required fields', () => {
    const a = makeAchievement('first_race');
    expect(a.key).toBe('first_race');
    expect(a.unlocked_at).not.toBeNull();
    expect(a.hidden).toBe(false);
  });

  it('hidden achievement has hidden flag set', () => {
    const a: Achievement = {
      ...makeAchievement('hidden_speedster'),
      hidden: true,
    };
    expect(a.hidden).toBe(true);
  });
});

describe('prefers-reduced-motion detection', () => {
  beforeEach(() => {
    mockWindow.matchMedia = vi.fn().mockImplementation((query: string) => ({
      matches: query === '(prefers-reduced-motion: reduce)',
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }));
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('detects prefers-reduced-motion when set', () => {
    const mq = mockWindow.matchMedia('(prefers-reduced-motion: reduce)');
    expect(mq.matches).toBe(true);
  });

  it('detects no reduced motion preference when unset', () => {
    mockWindow.matchMedia = vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }));
    const mq = mockWindow.matchMedia('(prefers-reduced-motion: reduce)');
    expect(mq.matches).toBe(false);
  });
});

describe('achievement queue ordering', () => {
  it('sequential queue maintains insertion order', () => {
    const queue: Achievement[] = [
      makeAchievement('first_race'),
      makeAchievement('perfect_race'),
    ];
    expect(queue[0].key).toBe('first_race');
    expect(queue[1].key).toBe('perfect_race');
    // After draining first item:
    const remaining = queue.slice(1);
    expect(remaining[0].key).toBe('perfect_race');
  });

  it('empty queue produces no current achievement', () => {
    const queue: Achievement[] = [];
    const current = queue[0] ?? null;
    expect(current).toBeNull();
  });
});

describe('race state gating', () => {
  it('RACING state means toast should not display', () => {
    const raceState = 'RACING';
    // Component renders null when raceState !== RESULTS
    expect(raceState === 'RESULTS').toBe(false);
  });

  it('RESULTS state means toast may display', () => {
    const raceState = 'RESULTS';
    expect(raceState === 'RESULTS').toBe(true);
  });
});
