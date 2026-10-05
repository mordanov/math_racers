import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import { XPBar } from './XPBar';

it('sets aria-valuenow to current xp', () => {
  render(<XPBar current={300} max={1000} level={3} />);
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '300');
});

it('sets aria-valuemax to max xp', () => {
  render(<XPBar current={300} max={1000} level={3} />);
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuemax', '1000');
});

it('shows level in accessible label', () => {
  render(<XPBar current={300} max={1000} level={3} />);
  expect(screen.getByRole('progressbar')).toHaveAttribute(
    'aria-label',
    expect.stringContaining('3'),
  );
});

it('clamps fill to 100% when current > max', () => {
  render(<XPBar current={1200} max={1000} level={5} />);
  const fill = screen.getByTestId('xpbar-fill');
  expect(fill.style.width).toBe('100%');
});

it('shows 0% fill for 0 current', () => {
  render(<XPBar current={0} max={1000} level={1} />);
  expect(screen.getByTestId('xpbar-fill').style.width).toBe('0%');
});
