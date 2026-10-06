import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import * as avatarApiModule from '../engine/avatar/avatarApi';
import AvatarGalleryPage from './AvatarGalleryPage';
import type { AvatarListItem } from '../engine/avatar/types';

vi.mock('../engine/avatar/avatarApi');

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
    full_url: 'http://x.com/full.png',
    medium_url: 'http://x.com/medium.png',
    small_url: 'http://x.com/small.png',
    thumb_url: 'http://x.com/thumb.png',
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

describe('AvatarGalleryPage', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.clearAllMocks();
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it('shows empty state with create CTA when no avatars', async () => {
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([]);
    render(
      <MemoryRouter>
        <AvatarGalleryPage />
      </MemoryRouter>,
    );
    expect(
      await screen.findByRole('link', { name: /create your first avatar/i }),
    ).toBeInTheDocument();
  });

  it('renders avatar cards when avatars exist', async () => {
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([published]);
    render(
      <MemoryRouter>
        <AvatarGalleryPage />
      </MemoryRouter>,
    );
    expect(await screen.findByText('Foxy')).toBeInTheDocument();
  });

  it('shows generating card (not empty state) when only avatar is pending', async () => {
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([pending]);
    render(
      <MemoryRouter>
        <AvatarGalleryPage />
      </MemoryRouter>,
    );
    expect(await screen.findByText(/generating/i)).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /create your first avatar/i })).toBeNull();
  });

  it('shows error state on fetch failure', async () => {
    vi.mocked(avatarApiModule.listAvatars).mockRejectedValue(new Error('oops'));
    render(
      <MemoryRouter>
        <AvatarGalleryPage />
      </MemoryRouter>,
    );
    expect(await screen.findByRole('alert')).toBeInTheDocument();
  });
});
