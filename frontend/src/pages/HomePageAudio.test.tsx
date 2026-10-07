import { render } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter } from 'react-router-dom';

const mockPlayMusic = vi.hoisted(() => vi.fn());
const mockStopMusic = vi.hoisted(() => vi.fn());

vi.mock('../shared/hooks/useAudioManager', () => ({
  useAudioManager: () => ({ playMusic: mockPlayMusic, stopMusic: mockStopMusic }),
}));

vi.mock('../engine/race/championshipApi', () => ({
  getChampionship: () => Promise.reject(new Error('no')),
}));

import HomePage from './HomePage';

beforeEach(() => {
  mockPlayMusic.mockClear();
  mockStopMusic.mockClear();
});

describe('HomePage audio', () => {
  it('plays menu music on mount', () => {
    render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    );
    expect(mockPlayMusic).toHaveBeenCalledWith('menu');
  });

  it('stops music on unmount', () => {
    const { unmount } = render(
      <MemoryRouter>
        <HomePage />
      </MemoryRouter>,
    );
    unmount();
    expect(mockStopMusic).toHaveBeenCalled();
  });
});
