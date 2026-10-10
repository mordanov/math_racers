import { afterEach, describe, expect, it, vi } from 'vitest';

const mockPost = vi.hoisted(() => vi.fn());

vi.mock('../api-client', () => ({
  apiClient: { post: mockPost },
}));

import { login, logout, refreshToken, register } from './authApi';

describe('authApi', () => {
  afterEach(() => vi.clearAllMocks());

  it('posts login credentials through the shared client', async () => {
    mockPost.mockResolvedValue({ access_token: 'tok123' });

    const result = await login('user@example.com', 'pass');

    expect(result.access_token).toBe('tok123');
    expect(mockPost).toHaveBeenCalledWith('/auth/login', {
      email: 'user@example.com',
      password: 'pass',
    });
  });

  it('posts registration credentials through the shared client', async () => {
    mockPost.mockResolvedValue(undefined);

    await expect(register('new@example.com', 'pass')).resolves.toBeUndefined();

    expect(mockPost).toHaveBeenCalledWith('/auth/register', {
      email: 'new@example.com',
      password: 'pass',
    });
  });

  it('refreshes the access token through the shared client', async () => {
    mockPost.mockResolvedValue({ access_token: 'new-tok' });

    const result = await refreshToken();

    expect(result.access_token).toBe('new-tok');
    expect(mockPost).toHaveBeenCalledWith('/auth/refresh');
  });

  it('logs out through the shared client', async () => {
    mockPost.mockResolvedValue(undefined);

    await expect(logout()).resolves.toBeUndefined();

    expect(mockPost).toHaveBeenCalledWith('/auth/logout');
  });
});
