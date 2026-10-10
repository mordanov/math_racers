import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { resolveLocale } from './catalogs';
import { LocaleProvider, useLocale } from './LocaleContext';

function CurrentLanguage() {
  const { locale, setLocale, t } = useLocale();
  return (
    <>
      <span>{t('Language')}</span>
      <span data-testid="locale">{locale}</span>
      <button type="button" onClick={() => setLocale('es')}>
        Español
      </button>
    </>
  );
}

describe('locale resolution and context', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('prefers a supported saved language over the browser language', () => {
    expect(resolveLocale('es', 'ru-RU')).toBe('es');
  });

  it('normalizes a supported browser language and falls back to Russian', () => {
    expect(resolveLocale(null, 'ES-mx')).toBe('es');
    expect(resolveLocale('unsupported', 'fr-FR')).toBe('ru');
  });

  it('updates translated content, persists the choice, and sets the document language', async () => {
    localStorage.setItem('math-racers-locale', 'en');
    const user = userEvent.setup();

    render(
      <LocaleProvider>
        <CurrentLanguage />
      </LocaleProvider>,
    );

    expect(screen.getByTestId('locale')).toHaveTextContent('en');
    await user.click(screen.getByRole('button', { name: 'Español' }));

    expect(screen.getByTestId('locale')).toHaveTextContent('es');
    expect(screen.getByText('Idioma')).toBeInTheDocument();
    expect(localStorage.getItem('math-racers-locale')).toBe('es');
    expect(document.documentElement).toHaveAttribute('lang', 'es');
  });
});
