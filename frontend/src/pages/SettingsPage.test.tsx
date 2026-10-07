import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import SettingsPage from './SettingsPage';

describe('SettingsPage', () => {
  beforeEach(() => localStorage.clear());

  function renderPage() {
    return render(
      <MemoryRouter>
        <SettingsPage />
      </MemoryRouter>,
    );
  }

  it('renders the page container', () => {
    renderPage();
    expect(screen.getByTestId('page-settings')).toBeInTheDocument();
  });

  it('shows audio volume sliders', () => {
    renderPage();
    expect(screen.getByLabelText(/master volume/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/music volume/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/sfx volume/i)).toBeInTheDocument();
  });

  it('shows reduced motion toggle', () => {
    renderPage();
    expect(screen.getByLabelText(/reduce motion/i)).toBeInTheDocument();
  });

  it('persists master volume change to localStorage', () => {
    renderPage();
    const slider = screen.getByLabelText(/master volume/i);
    fireEvent.change(slider, { target: { value: '60' } });
    expect(localStorage.getItem('settings.masterVolume')).toBe('60');
  });

  it('loads saved values from localStorage on mount', () => {
    localStorage.setItem('settings.masterVolume', '42');
    renderPage();
    const slider = screen.getByLabelText(/master volume/i);
    expect((slider as HTMLInputElement).value).toBe('42');
  });

  it('persists reduced motion toggle to localStorage', () => {
    renderPage();
    const toggle = screen.getByLabelText(/reduce motion/i);
    fireEvent.click(toggle);
    expect(localStorage.getItem('settings.reducedMotion')).toBe('true');
  });
});
