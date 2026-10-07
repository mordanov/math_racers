import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { AvatarCard } from './AvatarCard';
import type { AvatarListItem } from '../../engine/avatar/types';

const published: AvatarListItem = {
  avatar_id: 'a1',
  name: 'Foxy',
  species: 'fox',
  status: 'published',
  is_favourite: false,
  portrait: {
    id: 'p1',
    version: 1,
    prompt_version: '1.0.0',
    model_version: 'dall-e-3',
    full_url: 'http://example.com/full.png',
    medium_url: 'http://example.com/medium.png',
    small_url: 'http://example.com/small.png',
    thumb_url: 'http://example.com/thumb.png',
    created_at: '2026-01-01T00:00:00Z',
  },
  created_at: '2026-01-01T00:00:00Z',
};

const pending: AvatarListItem = {
  avatar_id: 'a2',
  name: null,
  species: 'rabbit',
  status: 'pending',
  is_favourite: false,
  portrait: null,
  created_at: '2026-01-01T00:00:00Z',
};

describe('AvatarCard', () => {
  it('shows the avatar name when published', () => {
    render(<AvatarCard avatar={published} />);
    expect(screen.getByText('Foxy')).toBeInTheDocument();
  });

  it('shows species as fallback when name is null', () => {
    render(<AvatarCard avatar={{ ...published, name: null }} />);
    // Both the display name and the species label show "fox" — at least one must exist
    expect(screen.getAllByText(/fox/i).length).toBeGreaterThan(0);
  });

  it('renders portrait image for published avatar', () => {
    render(<AvatarCard avatar={published} />);
    const img = screen.getByRole('img');
    expect(img).toHaveAttribute('src', 'http://example.com/small.png');
  });

  it('shows generating indicator for pending avatar', () => {
    render(<AvatarCard avatar={pending} />);
    expect(screen.getByText(/generating/i)).toBeInTheDocument();
  });

  it('calls onSelect with avatar_id when clicked', async () => {
    const onSelect = vi.fn();
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onSelect={onSelect} />);
    await user.click(screen.getByRole('button'));
    expect(onSelect).toHaveBeenCalledWith('a1');
  });

  it('applies selected visual indicator when selected is true', () => {
    render(<AvatarCard avatar={published} selected onSelect={vi.fn()} />);
    const btn = screen.getByRole('button');
    expect(btn).toHaveAttribute('aria-pressed', 'true');
  });

  it('truncates long avatar names at 24 characters with ellipsis', () => {
    const longName = 'A'.repeat(30);
    render(
      <AvatarCard
        avatar={{
          avatar_id: '1',
          name: longName,
          species: 'fox',
          status: 'published',
          is_favourite: false,
          portrait: null,
          created_at: '2024-01-01',
        }}
      />,
    );
    expect(screen.getByText(longName.slice(0, 24) + '…')).toBeInTheDocument();
  });

  it('does not render favourite star when onFavourite is absent', () => {
    render(<AvatarCard avatar={published} />);
    expect(screen.queryByRole('button', { name: /favourites/i })).toBeNull();
  });
});

describe('AvatarCard — favourite', () => {
  it('renders favourite star when onFavourite is provided', () => {
    render(<AvatarCard avatar={published} onFavourite={vi.fn()} />);
    expect(screen.getByRole('button', { name: /add to favourites/i })).toBeInTheDocument();
  });

  it('shows remove label when is_favourite is true', () => {
    render(<AvatarCard avatar={{ ...published, is_favourite: true }} onFavourite={vi.fn()} />);
    expect(screen.getByRole('button', { name: /remove from favourites/i })).toBeInTheDocument();
  });

  it('calls onFavourite with flipped value on star click', async () => {
    const onFavourite = vi.fn();
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onFavourite={onFavourite} />);
    await user.click(screen.getByRole('button', { name: /add to favourites/i }));
    expect(onFavourite).toHaveBeenCalledWith('a1', true);
  });
});

describe('AvatarCard — manage menu', () => {
  it('renders manage button when any manage callback is provided', () => {
    render(<AvatarCard avatar={published} onDelete={vi.fn()} />);
    expect(screen.getByRole('button', { name: /manage avatar/i })).toBeInTheDocument();
  });

  it('clicking manage button shows rename/regenerate/delete actions', async () => {
    const user = userEvent.setup();
    render(
      <AvatarCard avatar={published} onRename={vi.fn()} onRegenerate={vi.fn()} onDelete={vi.fn()} />,
    );
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    expect(screen.getByRole('menuitem', { name: /rename/i })).toBeInTheDocument();
    expect(screen.getByRole('menuitem', { name: /regenerate/i })).toBeInTheDocument();
    expect(screen.getByRole('menuitem', { name: /delete/i })).toBeInTheDocument();
  });

  it('clicking Rename enters inline edit mode', async () => {
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onRename={vi.fn()} />);
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    await user.click(screen.getByRole('menuitem', { name: /rename/i }));
    expect(screen.getByRole('textbox', { name: /rename avatar/i })).toBeInTheDocument();
  });

  it('Save button is disabled when rename input is empty (Review Focus #2)', async () => {
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onRename={vi.fn()} />);
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    await user.click(screen.getByRole('menuitem', { name: /rename/i }));
    const input = screen.getByRole('textbox', { name: /rename avatar/i });
    await user.clear(input);
    expect(screen.getByRole('button', { name: /save/i })).toBeDisabled();
  });

  it('long name trimmed before onRename call (Review Focus #5)', async () => {
    const onRename = vi.fn();
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onRename={onRename} />);
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    await user.click(screen.getByRole('menuitem', { name: /rename/i }));
    const input = screen.getByRole('textbox', { name: /rename avatar/i });
    await user.clear(input);
    await user.type(input, '  Padded  ');
    await user.click(screen.getByRole('button', { name: /save/i }));
    expect(onRename).toHaveBeenCalledWith('a1', 'Padded');
  });

  it('Escape cancels rename without calling onRename', async () => {
    const onRename = vi.fn();
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onRename={onRename} />);
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    await user.click(screen.getByRole('menuitem', { name: /rename/i }));
    const input = screen.getByRole('textbox', { name: /rename avatar/i });
    await user.clear(input);
    await user.type(input, 'NewName');
    await user.keyboard('{Escape}');
    expect(onRename).not.toHaveBeenCalled();
    expect(screen.queryByRole('textbox')).toBeNull();
  });

  it('clicking Delete opens ConfirmDialog', async () => {
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onDelete={vi.fn()} />);
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    await user.click(screen.getByRole('menuitem', { name: /delete/i }));
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('confirming delete calls onDelete with avatar_id', async () => {
    const onDelete = vi.fn();
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onDelete={onDelete} />);
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    await user.click(screen.getByRole('menuitem', { name: /delete/i }));
    await user.click(screen.getByRole('button', { name: /^delete$/i }));
    expect(onDelete).toHaveBeenCalledWith('a1');
  });

  it('clicking Regenerate calls onRegenerate with avatar_id', async () => {
    const onRegenerate = vi.fn();
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onRegenerate={onRegenerate} />);
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    await user.click(screen.getByRole('menuitem', { name: /regenerate/i }));
    expect(onRegenerate).toHaveBeenCalledWith('a1');
  });

  it('pressing Escape closes the manage menu (WAI-ARIA keyboard nav)', async () => {
    const user = userEvent.setup();
    render(
      <AvatarCard avatar={published} onRename={vi.fn()} onRegenerate={vi.fn()} onDelete={vi.fn()} />,
    );
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    expect(screen.getByRole('menu')).toBeInTheDocument();
    await user.keyboard('{Escape}');
    expect(screen.queryByRole('menu')).toBeNull();
  });

  it('ArrowDown moves focus to next menuitem (WAI-ARIA keyboard nav)', async () => {
    const user = userEvent.setup();
    render(
      <AvatarCard avatar={published} onRename={vi.fn()} onRegenerate={vi.fn()} onDelete={vi.fn()} />,
    );
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    const renameItem = screen.getByRole('menuitem', { name: /rename/i });
    const regenItem = screen.getByRole('menuitem', { name: /regenerate/i });
    renameItem.focus();
    await user.keyboard('{ArrowDown}');
    expect(document.activeElement).toBe(regenItem);
  });
});

describe('AvatarCard — continued', () => {
  it('uses full name (not truncated) for image alt text', () => {
    const longName = 'B'.repeat(30);
    render(
      <AvatarCard
        avatar={{
          avatar_id: '2',
          name: longName,
          species: 'fox',
          status: 'published',
          is_favourite: false,
          portrait: {
            id: 'p1',
            version: 1,
            prompt_version: '1.0.0',
            model_version: 'dall-e-3',
            full_url: 'http://example.com/full.png',
            medium_url: 'http://example.com/medium.png',
            small_url: 'http://example.com/small.png',
            thumb_url: 'http://example.com/thumb.png',
            created_at: '2024-01-01T00:00:00Z',
          },
          created_at: '2024-01-01',
        }}
      />,
    );
    expect(screen.getByRole('img')).toHaveAttribute('alt', longName);
  });
});
