import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { APIError } from '../../infrastructure/api-client';
import { ErrorState } from './ErrorState';

describe('ErrorState', () => {
  it('has role="alert" for immediate screen reader announcement', () => {
    render(<ErrorState error={new Error('oops')} />);
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('shows child-friendly message for network error', () => {
    render(<ErrorState error={new Error('NetworkError')} />);
    expect(screen.getByRole('alert')).toHaveTextContent(/internet|connection/i);
  });

  it('shows child-friendly message for 404', () => {
    render(<ErrorState error={new APIError(404, {})} />);
    expect(screen.getByRole('alert')).toHaveTextContent(/find/i);
  });

  it('shows child-friendly message for 500', () => {
    render(<ErrorState error={new APIError(500, {})} />);
    expect(screen.getByRole('alert')).toHaveTextContent(/wrong|again/i);
  });

  it('shows retry button when onRetry is provided', async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    render(<ErrorState error={new Error('fail')} onRetry={onRetry} />);
    await user.click(screen.getByRole('button', { name: /try again/i }));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it('does not show retry button without onRetry', () => {
    render(<ErrorState error={new Error('fail')} />);
    expect(screen.queryByRole('button')).toBeNull();
  });
});
