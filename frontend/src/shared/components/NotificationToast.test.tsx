import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { NotificationToast } from './NotificationToast';

describe('NotificationToast', () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it('renders the message', () => {
    render(<NotificationToast message="Race saved!" onClose={vi.fn()} />);
    expect(screen.getByText('Race saved!')).toBeInTheDocument();
  });

  it('has role="status" for screen readers', () => {
    render(<NotificationToast message="Done" onClose={vi.fn()} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  // Review Focus #5: timer must be cleared on unmount
  it('does NOT call onClose when unmounted before 3 seconds', () => {
    const onClose = vi.fn();
    const { unmount } = render(<NotificationToast message="Hi" onClose={onClose} />);
    unmount();
    vi.advanceTimersByTime(3000);
    expect(onClose).not.toHaveBeenCalled();
  });

  it('calls onClose after 3 seconds', () => {
    const onClose = vi.fn();
    render(<NotificationToast message="Hi" onClose={onClose} />);
    vi.advanceTimersByTime(3000);
    expect(onClose).toHaveBeenCalledOnce();
  });

  it('calls onClose when close button is clicked before timeout', async () => {
    vi.useRealTimers();
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<NotificationToast message="Hi" onClose={onClose} />);
    await user.click(screen.getByRole('button', { name: /dismiss/i }));
    expect(onClose).toHaveBeenCalledOnce();
  });
});
