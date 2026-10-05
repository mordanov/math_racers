import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';
import { LoadingSpinner } from './LoadingSpinner';

it('has role="status" for screen readers', () => {
  render(<LoadingSpinner />);
  expect(screen.getByRole('status')).toBeInTheDocument();
});

it('has an accessible label', () => {
  render(<LoadingSpinner />);
  const el = screen.getByRole('status');
  expect(el).toHaveAttribute('aria-label');
});

it('renders optional message', () => {
  render(<LoadingSpinner message="Loading race…" />);
  expect(screen.getByText('Loading race…')).toBeInTheDocument();
});

it('renders without message by default', () => {
  render(<LoadingSpinner />);
  expect(screen.queryByText(/./)).toBeNull();
});
