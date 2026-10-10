import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import {
  resolveLocale,
  translate,
  type Locale,
  type TranslationKey,
  type TranslationValues,
} from './catalogs';

const LANGUAGE_STORAGE_KEY = 'math-racers-locale';

interface LocaleContextValue {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: TranslationKey, values?: TranslationValues) => string;
}

const LocaleContext = createContext<LocaleContextValue>({
  locale: 'en',
  setLocale: () => {
    throw new Error('LanguageSwitcher must be rendered within LocaleProvider.');
  },
  t: (key, values) => translate('en', key, values),
});

function readStoredLocale(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    return window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
  } catch (error) {
    if (error instanceof DOMException && error.name === 'SecurityError') return null;
    throw error;
  }
}

function saveLocale(locale: Locale): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, locale);
  } catch (error) {
    if (
      error instanceof DOMException &&
      (error.name === 'SecurityError' || error.name === 'QuotaExceededError')
    ) {
      // The locale still changes for this session when browser storage is unavailable.
      // eslint-disable-next-line no-console
      console.warn('The language preference could not be saved in this browser.', error);
      return;
    }
    throw error;
  }
}

export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState(() =>
    resolveLocale(readStoredLocale(), typeof navigator === 'undefined' ? null : navigator.language),
  );

  const setLocale = useCallback((nextLocale: Locale) => {
    saveLocale(nextLocale);
    setLocaleState(nextLocale);
  }, []);

  const t = useCallback(
    (key: TranslationKey, values?: TranslationValues) => translate(locale, key, values),
    [locale],
  );

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  const value = useMemo(() => ({ locale, setLocale, t }), [locale, setLocale, t]);

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useLocale(): LocaleContextValue {
  return useContext(LocaleContext);
}
