import type { TranslationKey } from './catalogs';

type Translate = (key: TranslationKey) => string;

export function translateOperation(operation: string | null, t: Translate): string {
  switch (operation) {
    case 'addition':
    case 'subtraction':
    case 'multiplication':
    case 'division':
      return t(operation);
    default:
      return operation ?? '—';
  }
}

export function translateAvatarSpecies(species: string, t: Translate): string {
  switch (species) {
    case 'fox':
    case 'rabbit':
    case 'bear':
    case 'cat':
    case 'mouse':
    case 'panda':
      return t(species);
    default:
      return species;
  }
}

export function translateRaceMode(mode: string, t: Translate): string {
  switch (mode) {
    case 'quick':
      return t('Quick Race');
    case 'championship':
      return t('Championship');
    case 'training':
      return t('Training');
    case 'duel':
      return t('Duel');
    default:
      return mode;
  }
}

export function translateLegacyRecordType(
  type:
    'avatar' | 'avatar_stats' | 'achievement' | 'race' | 'statistics' | 'xp_event' | 'championship',
  t: Translate,
): string {
  switch (type) {
    case 'avatar':
      return t('Avatar');
    case 'avatar_stats':
      return t('Avatar statistics');
    case 'achievement':
      return t('Achievement');
    case 'race':
      return t('Race');
    case 'statistics':
      return t('Statistics');
    case 'xp_event':
      return t('XP event');
    case 'championship':
      return t('Championship');
  }
}

export function getAchievementTranslationKeys(key: string): {
  title: TranslationKey;
  description: TranslationKey;
} | null {
  const achievements: Record<string, { title: TranslationKey; description: TranslationKey }> = {
    first_race: { title: 'Off to the Races!', description: 'Complete your first race.' },
    perfect_race: {
      title: 'Perfect Score',
      description: 'Answer all 8 problems correctly in a single race.',
    },
    podium_finisher: {
      title: 'Podium Finisher',
      description: 'Finish in the top 3 in a race.',
    },
    champion: { title: 'Champion', description: 'Finish in 1st place in a race.' },
    level_5: { title: 'Rising Star', description: 'Reach level 5.' },
    level_10: { title: 'Veteran Racer', description: 'Reach level 10.' },
    level_20: { title: 'Math Legend', description: 'Reach level 20.' },
    hidden_speedster: {
      title: 'Speed Demon',
      description: 'Win a race with an average response time under 500ms.',
    },
  };
  return achievements[key] ?? null;
}
