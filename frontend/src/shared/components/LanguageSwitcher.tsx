import { isLocale, supportedLocales } from '../../infrastructure/localization/catalogs';
import { useLocale } from '../../infrastructure/localization/LocaleContext';
import tokens from '../tokens';

const languageNames = {
  ru: 'Русский',
  en: 'English',
  es: 'Español',
} as const;

export function LanguageSwitcher() {
  const { locale, setLocale, t } = useLocale();

  return (
    <label
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: tokens.spacing.xs,
        color: tokens.color.textPrimary,
        fontSize: 14,
        fontWeight: 600,
      }}
    >
      <span>{t('Language')}</span>
      <select
        value={locale}
        onChange={(event) => {
          if (isLocale(event.target.value)) setLocale(event.target.value);
        }}
        style={{
          minHeight: tokens.touchTarget,
          padding: `0 ${tokens.spacing.sm}px`,
          border: `1px solid ${tokens.color.border}`,
          borderRadius: tokens.radius.sm,
          background: tokens.color.surface,
          color: tokens.color.textPrimary,
          font: 'inherit',
          cursor: 'pointer',
        }}
      >
        {supportedLocales.map((language) => (
          <option key={language} value={language}>
            {languageNames[language]}
          </option>
        ))}
      </select>
    </label>
  );
}
