import { catalogs, supportedLocales, translate, type TranslationKey } from './catalogs';

describe('translation catalogs', () => {
  it('contains the same non-empty message keys in every supported locale', () => {
    const expectedKeys = Object.keys(catalogs.en).sort();

    for (const locale of supportedLocales) {
      expect(Object.keys(catalogs[locale]).sort()).toEqual(expectedKeys);
      expect(Object.values(catalogs[locale]).every((message) => message.trim().length > 0)).toBe(
        true,
      );
      for (const key of expectedKeys) {
        const translationKey = key as TranslationKey;
        const englishPlaceholders = [...catalogs.en[translationKey].matchAll(/\{\{(\w+)\}\}/g)]
          .map((match) => match[1])
          .sort();
        const localizedPlaceholders = [
          ...catalogs[locale][translationKey].matchAll(/\{\{(\w+)\}\}/g),
        ]
          .map((match) => match[1])
          .sort();
        expect(localizedPlaceholders).toEqual(englishPlaceholders);
      }
    }
  });

  it('interpolates dynamic values in the selected language', () => {
    expect(translate('ru', '{{runner}}: {{distance}}m', { runner: 'Вы', distance: 42 })).toBe(
      'Вы: 42м',
    );
  });
});
