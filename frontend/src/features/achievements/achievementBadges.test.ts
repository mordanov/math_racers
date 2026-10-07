import { describe, it, expect } from 'vitest';
import { getBadgeUrl } from './achievementBadges';

describe('getBadgeUrl', () => {
  it('returns correct path for known achievement id', () => {
    expect(getBadgeUrl('first_race')).toBe('/achievements/first_race.png');
  });

  it('returns correct path for level_10', () => {
    expect(getBadgeUrl('level_10')).toBe('/achievements/level_10.png');
  });

  it('falls back to 1-6.png for unknown achievement', () => {
    expect(getBadgeUrl('unknown_achievement_xyz')).toBe('/achievements/1-6.png');
  });
});
