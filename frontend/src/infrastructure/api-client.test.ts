import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { APIClient, APIError } from './api-client';

function mockFetch(status: number, body: unknown = {}) {
  return vi.fn().mockResolvedValue({
    status,
    ok: status >= 200 && status < 300,
    json: vi.fn().mockResolvedValue(body),
  });
}

describe('APIClient', () => {
  let client: APIClient;

  beforeEach(() => {
    client = new APIClient();
    vi.useFakeTimers();
    Object.defineProperty(document, 'cookie', {
      configurable: true,
      value: 'csrf_token=test-csrf',
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it('returns parsed JSON on 200', async () => {
    vi.stubGlobal('fetch', mockFetch(200, { value: 42 }));
    const result = await client.get<{ value: number }>('/test');
    expect(result).toEqual({ value: 42 });
  });

  // Review Focus #1: retry exactly 3 total attempts on 5xx
  it('retries on 5xx up to 3 total attempts then throws APIError', async () => {
    vi.stubGlobal('fetch', mockFetch(500));
    const promise = client.get('/test');
    // Attach rejection handler before running timers to avoid unhandled rejection
    const check = expect(promise).rejects.toBeInstanceOf(APIError);
    await vi.runAllTimersAsync();
    await check;
    expect(vi.mocked(fetch)).toHaveBeenCalledTimes(3);
  });

  it('does not retry on 4xx', async () => {
    vi.stubGlobal('fetch', mockFetch(404));
    // 4xx rejects immediately (no timer), await directly
    await expect(client.get('/test')).rejects.toBeInstanceOf(APIError);
    expect(vi.mocked(fetch)).toHaveBeenCalledTimes(1);
  });

  it('throws APIError with correct status on 4xx', async () => {
    vi.stubGlobal('fetch', mockFetch(401, { detail: 'Unauthorized' }));
    // 4xx rejects immediately (no timer), await directly
    try {
      await client.get('/test');
      expect.fail('should have thrown');
    } catch (e) {
      expect(e).toBeInstanceOf(APIError);
      expect((e as APIError).status).toBe(401);
    }
  });

  // Review Focus #2: 204 must return undefined without calling .json()
  it('returns undefined for 204 without parsing body', async () => {
    const fakeFetch = vi.fn().mockResolvedValue({ status: 204, ok: true });
    vi.stubGlobal('fetch', fakeFetch);
    const result = await client.delete('/test');
    expect(result).toBeUndefined();
    // json() was never called — fakeFetch response has no .json()
    // If it were called, this test would throw "json is not a function"
  });

  it('sends correct method and body for POST', async () => {
    const fake = mockFetch(200, { id: '1' });
    vi.stubGlobal('fetch', fake);
    await client.post('/items', { name: 'test' });
    expect(fake).toHaveBeenCalledWith('/api/v1/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': 'test-csrf' },
      body: JSON.stringify({ name: 'test' }),
      credentials: 'same-origin',
    });
  });

  it('sends PATCH with body', async () => {
    const fake = mockFetch(200, { id: '1' });
    vi.stubGlobal('fetch', fake);
    await client.patch('/items/1', { name: 'updated' });
    expect(fake).toHaveBeenCalledWith(
      '/api/v1/items/1',
      expect.objectContaining({
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': 'test-csrf',
        },
      }),
    );
  });

  it('fetches a CSRF cookie before the first state-changing request', async () => {
    Object.defineProperty(document, 'cookie', {
      configurable: true,
      value: '',
    });
    const fake = vi
      .fn<typeof fetch>()
      .mockImplementationOnce(() => {
        Object.defineProperty(document, 'cookie', {
          configurable: true,
          value: 'csrf_token=issued-token',
        });
        return Promise.resolve(new Response(null, { status: 204 }));
      })
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ ok: true }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        }),
      );
    vi.stubGlobal('fetch', fake);

    await client.post('/races', {});

    const [csrfUrl, csrfOptions] = fake.mock.calls[0];
    expect(csrfUrl).toBe('/api/v1/auth/csrf');
    expect(csrfOptions?.method).toBe('GET');

    const [raceUrl, raceOptions] = fake.mock.calls[1];
    expect(raceUrl).toBe('/api/v1/races');
    expect(new Headers(raceOptions?.headers).get('X-CSRF-Token')).toBe('issued-token');
  });

  it('sends the active child profile header', async () => {
    const fake = mockFetch(200, {});
    vi.stubGlobal('fetch', fake);
    client.setActiveChildId('child-1');
    await client.post('/races', {});
    const [, options] = fake.mock.calls[0] as [string, RequestInit];
    expect((options.headers as Record<string, string>)['X-Child-Profile-ID']).toBe('child-1');
    expect((options.headers as Record<string, string>)['X-CSRF-Token']).toBe('test-csrf');
  });

  describe('auth token', () => {
    it('sends Authorization header when token is set', async () => {
      const fake = mockFetch(200, { ok: true });
      vi.stubGlobal('fetch', fake);
      client.setAuthToken('test-token');
      await client.get('/test');
      const [, options] = fake.mock.calls[0] as [string, RequestInit];
      expect((options.headers as Record<string, string>)['Authorization']).toBe(
        'Bearer test-token',
      );
    });

    it('omits Authorization header when no token set', async () => {
      const fake = mockFetch(200, { ok: true });
      vi.stubGlobal('fetch', fake);
      await client.get('/test');
      const [, options] = fake.mock.calls[0] as [string, RequestInit];
      expect((options.headers as Record<string, string>)['Authorization']).toBeUndefined();
    });

    it('clears Authorization header after setAuthToken(null)', async () => {
      const fake = mockFetch(200, { ok: true });
      vi.stubGlobal('fetch', fake);
      client.setAuthToken('test-token');
      client.setAuthToken(null);
      await client.get('/test');
      const [, options] = fake.mock.calls[0] as [string, RequestInit];
      expect((options.headers as Record<string, string>)['Authorization']).toBeUndefined();
    });
  });
});
