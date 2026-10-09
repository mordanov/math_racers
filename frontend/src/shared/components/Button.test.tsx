import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { Button } from './Button';
import * as sfxModule from '../hooks/useSfxPlayer';

vi.mock('../hooks/useSfxPlayer');

describe('Button', () => {
  beforeEach(() => {
    vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx: vi.fn() });
  });

  it('renders children', () => {
    render(<Button variant="primary">Go</Button>);
    expect(screen.getByRole('button', { name: 'Go' })).toBeInTheDocument();
  });

  it('calls onClick when clicked', async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(
      <Button variant="primary" onClick={onClick}>
        Go
      </Button>,
    );
    await user.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledOnce();
  });

  it('does not call onClick when disabled', async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(
      <Button variant="primary" disabled onClick={onClick}>
        Go
      </Button>,
    );
    await user.click(screen.getByRole('button'));
    expect(onClick).not.toHaveBeenCalled();
  });

  it('does not call onClick when loading', async () => {
    const user = userEvent.setup();
    const onClick = vi.fn();
    render(
      <Button variant="primary" loading onClick={onClick}>
        Go
      </Button>,
    );
    await user.click(screen.getByRole('button'));
    expect(onClick).not.toHaveBeenCalled();
  });

  it('has type="button" by default', () => {
    render(<Button variant="primary">Go</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('type', 'button');
  });

  it('renders all three variants without crashing', () => {
    const { rerender } = render(<Button variant="primary">P</Button>);
    rerender(<Button variant="secondary">S</Button>);
    rerender(<Button variant="ghost">G</Button>);
  });

  it('has minimum touch target size', () => {
    render(<Button variant="primary">Go</Button>);
    const btn = screen.getByRole('button');
    expect(parseInt(btn.style.minHeight)).toBeGreaterThanOrEqual(44);
  });

  it('fires ui_click sfx on click when playSound is true', async () => {
    const user = userEvent.setup();
    const playSfx = vi.fn();
    vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
    render(
      <Button variant="primary" playSound>
        Go
      </Button>,
    );
    await user.click(screen.getByRole('button'));
    expect(playSfx).toHaveBeenCalledWith('ui_click');
  });

  it('fires ui_hover sfx on mouse enter when playSound is true', async () => {
    const user = userEvent.setup();
    const playSfx = vi.fn();
    vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
    render(
      <Button variant="primary" playSound>
        Go
      </Button>,
    );
    await user.hover(screen.getByRole('button'));
    expect(playSfx).toHaveBeenCalledWith('ui_hover');
  });

  it('does not fire sfx when playSound is omitted', async () => {
    const user = userEvent.setup();
    const playSfx = vi.fn();
    vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
    render(<Button variant="primary">Go</Button>);
    await user.click(screen.getByRole('button'));
    await user.hover(screen.getByRole('button'));
    expect(playSfx).not.toHaveBeenCalled();
  });
});
