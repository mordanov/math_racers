import { useState } from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Link, MemoryRouter, Route, Routes } from 'react-router-dom';
import App from './App';
import { LocaleProvider } from './infrastructure/localization/LocaleContext';

vi.mock('./infrastructure/offline/OfflineResultSync', () => ({ default: () => null }));

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
  });

  it('keeps the language selector available while routes change and preserves current state', async () => {
    const user = userEvent.setup();
    render(
      <LocaleProvider>
        <MemoryRouter initialEntries={['/']}>
          <Routes>
            <Route element={<App />}>
              <Route path="/" element={<HomeTestPage />} />
              <Route path="/next" element={<p>Next route content</p>} />
            </Route>
          </Routes>
        </MemoryRouter>
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
