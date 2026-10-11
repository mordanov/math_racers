import { useState } from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Link, MemoryRouter, Route, Routes } from 'react-router-dom';
import App from './App';
import { AuthProvider } from './infrastructure/auth/AuthContext';
import * as authApi from './infrastructure/auth/authApi';
import { LocaleProvider } from './infrastructure/localization/LocaleContext';

vi.mock('./infrastructure/offline/OfflineResultSync', () => ({ default: () => null }));
vi.mock('./infrastructure/auth/authApi');

function HomeTestPage() {
  const [draft, setDraft] = useState('');
  return (
    <>
      <label htmlFor="draft">Draft</label>
      <input id="draft" value={draft} onChange={(event) => setDraft(event.target.value)} />
      <Link to="/next">Next screen</Link>
    </>
  );
}

describe('App shell', () => {
  beforeEach(() => {
    localStorage.setItem('math-racers-locale', 'en');
    vi.mocked(authApi.refreshToken).mockRejectedValue(new Error('no session'));
  });

  it('keeps the language selector available while routes change and preserves current state', async () => {
    const user = userEvent.setup();
    render(
      <LocaleProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={['/']}>
            <Routes>
              <Route element={<App />}>
                <Route path="/" element={<HomeTestPage />} />
                <Route path="/next" element={<p>Next route content</p>} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </LocaleProvider>,
    );

    fireEvent.change(screen.getByLabelText('Draft'), { target: { value: 'keep me' } });
    await user.selectOptions(screen.getByRole('combobox', { name: 'Language' }), 'ru');
    expect(screen.getByLabelText('Draft')).toHaveValue('keep me');

    await user.click(screen.getByRole('link', { name: 'Next screen' }));

    expect(screen.getByText('Next route content')).toBeInTheDocument();
    expect(screen.getByRole('combobox', { name: 'Язык' })).toHaveValue('ru');
  });
});
