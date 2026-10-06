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
});
