import { afterEach, describe, expect, it, vi } from 'vitest';
import { login, logout, refreshToken, register } from './authApi';

function mockFetch(status: number, body: unknown = {}) {
  return vi.fn().mockResolvedValue({
    status,
    ok: status >= 200 && status < 300,
    json: vi.fn().mockResolvedValue(body),
  });
}

describe('authApi', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('login posts credentials and returns access_token', async () => {
    vi.stubGlobal('fetch', mockFetch(200, { access_token: 'tok123' }));
    const result = await login('user@example.com', 'pass');
    expect(result.access_token).toBe('tok123');
    const [url, opts] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit];
    expect(url).toContain('/auth/login');
    expect(opts.method).toBe('POST');
  });

  it('register posts credentials and resolves on 201', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ status: 201, ok: true, json: vi.fn().mockResolvedValue({}) }),
    );
    await expect(register('new@example.com', 'pass')).resolves.not.toThrow();
  });

  it('refreshToken posts to /auth/refresh', async () => {
    vi.stubGlobal('fetch', mockFetch(200, { access_token: 'new-tok' }));
    const result = await refreshToken();
    expect(result.access_token).toBe('new-tok');
    const [url] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit];
    expect(url).toContain('/auth/refresh');
  });

  it('logout posts to /auth/logout', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ status: 204, ok: true, json: vi.fn() }),
    );
    await expect(logout()).resolves.not.toThrow();
    const [url] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit];
    expect(url).toContain('/auth/logout');
  });
});
