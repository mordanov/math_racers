const KNOWN_BADGE_IDS = new Set([
  'new_achievement',
  'champion',
  'first_race',
  'hidden_speedster',
  'level_10',
  'level_20',
  'level_5',
  'perfect_race',
  'podium_finisher',
]);

export function getBadgeUrl(achievementId: string): string {
  const id = KNOWN_BADGE_IDS.has(achievementId) ? achievementId : 'new_achievement';
  return `/achievements/${id}.png`;
}
