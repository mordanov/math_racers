import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { ConfirmDialog } from './ConfirmDialog';

function setup(open = true, onConfirm = vi.fn(), onClose = vi.fn()) {
  const user = userEvent.setup();
  render(
    <ConfirmDialog
      open={open}
      title="Delete avatar?"
      message="This cannot be undone."
      onConfirm={onConfirm}
      onClose={onClose}
    />,
  );
  return { user, onConfirm, onClose };
}

describe('ConfirmDialog', () => {
  it('renders title and message when open', () => {
    setup();
    expect(screen.getByText('Delete avatar?')).toBeInTheDocument();
    expect(screen.getByText('This cannot be undone.')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    setup(false);
    expect(screen.queryByText('Delete avatar?')).toBeNull();
  });

  it('calls onConfirm when Confirm is clicked', async () => {
    const { user, onConfirm } = setup();
    await user.click(screen.getByRole('button', { name: /confirm/i }));
    expect(onConfirm).toHaveBeenCalledOnce();
  });

  it('calls onClose when Cancel is clicked', async () => {
    const { user, onClose } = setup();
    await user.click(screen.getByRole('button', { name: /cancel/i }));
    expect(onClose).toHaveBeenCalledOnce();
  });

  it('calls onClose when Escape is pressed', async () => {
    const { user, onClose } = setup();
    await user.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalledOnce();
  });

  // Review Focus #4: focus is returned to the triggering element on close
  it('restores focus to the previously focused element on close', async () => {
    const user = userEvent.setup();
    const trigger = document.createElement('button');
    trigger.textContent = 'Open';
    document.body.appendChild(trigger);
    trigger.focus();

    const onClose = vi.fn();
    render(
      <ConfirmDialog open title="T" message="M" onConfirm={vi.fn()} onClose={onClose} />,
    );
    // Focus should have moved into the dialog
    expect(document.activeElement).not.toBe(trigger);

    // Press Escape to close
    await user.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalled();

    document.body.removeChild(trigger);
  });

  it('has role="dialog" with aria-modal', () => {
    setup();
    expect(screen.getByRole('dialog')).toHaveAttribute('aria-modal', 'true');
  });
});
