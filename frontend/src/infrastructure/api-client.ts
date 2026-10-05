export class APIError extends Error {
  constructor(
    public readonly status: number,
    public readonly body: unknown,
  ) {
    super(`HTTP ${status}`);
  }
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export class APIClient {
  private baseURL = '/api/v1';

  async get<T>(path: string): Promise<T> {
    return this.request<T>('GET', path);
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('POST', path, body);
  }

  async patch<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('PATCH', path, body);
  }

  async delete<T = void>(path: string): Promise<T> {
    return this.request<T>('DELETE', path);
  }

  private async request<T>(method: string, path: string, body?: unknown, attempt = 1): Promise<T> {
    const response = await fetch(this.baseURL + path, {
      method,
      headers: body !== undefined ? { 'Content-Type': 'application/json' } : {},
      body: body !== undefined ? JSON.stringify(body) : undefined,
      credentials: 'same-origin',
    });

    if (response.status === 204) return undefined as unknown as T;

    if (response.status >= 500 && attempt < 3) {
      await delay(200 * attempt);
      return this.request<T>(method, path, body, attempt + 1);
    }

    if (!response.ok) {
      throw new APIError(response.status, await response.json().catch(() => ({})));
    }

    return response.json() as Promise<T>;
  }
}

export const apiClient = new APIClient();
