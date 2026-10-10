import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LocaleProvider } from '../../infrastructure/localization/LocaleContext';
import { LanguageSwitcher } from './LanguageSwitcher';

describe('LanguageSwitcher', () => {
  beforeEach(() => {
    localStorage.setItem('math-racers-locale', 'en');
  });

  it('offers all supported languages and applies a keyboard-accessible selection', async () => {
    const user = userEvent.setup();
    render(
      <LocaleProvider>
        <LanguageSwitcher />
      </LocaleProvider>,
    );

    const selector = screen.getByRole('combobox', { name: 'Language' });
    expect(selector).toHaveValue('en');
    expect(screen.getByRole('option', { name: 'Русский' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'English' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Español' })).toBeInTheDocument();

    await user.selectOptions(selector, 'es');

    expect(screen.getByRole('combobox', { name: 'Idioma' })).toHaveValue('es');
    expect(document.documentElement).toHaveAttribute('lang', 'es');
    expect(localStorage.getItem('math-racers-locale')).toBe('es');
  });
});
