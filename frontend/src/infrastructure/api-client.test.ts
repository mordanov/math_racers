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
      headers: { 'Content-Type': 'application/json' },
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
      }),
    );
  });
});
