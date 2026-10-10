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
  private authToken: string | null = null;
  private activeChildId: string | null = null;

  setAuthToken(token: string | null): void {
    this.authToken = token;
  }

  setActiveChildId(childId: string | null): void {
    this.activeChildId = childId;
  }

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
    const headers: Record<string, string> = {};
    if (body !== undefined) headers['Content-Type'] = 'application/json';
    if (this.activeChildId) headers['X-Child-Profile-ID'] = this.activeChildId;
    if (this.authToken) headers['Authorization'] = `Bearer ${this.authToken}`;
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method.toUpperCase())) {
      const csrfToken = await this.ensureCsrfToken();
      headers['X-CSRF-Token'] = csrfToken;
    }

    const response = await fetch(this.baseURL + path, {
      method,
      headers,
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

  private async ensureCsrfToken(): Promise<string> {
    const current = this.readCsrfCookie();
    if (current) return current;

    const response = await fetch(`${this.baseURL}/auth/csrf`, {
      method: 'GET',
      credentials: 'same-origin',
    });
    if (!response.ok) {
      throw new APIError(response.status, await response.json().catch(() => ({})));
    }
    const issued = this.readCsrfCookie();
    if (!issued) {
      throw new Error('The server did not issue a CSRF token.');
    }
    return issued;
  }

  private readCsrfCookie(): string | null {
    if (typeof document === 'undefined') return null;
    const token = document.cookie
      .split('; ')
      .find((cookie) => cookie.startsWith('csrf_token='))
      ?.slice('csrf_token='.length);
    return token ? decodeURIComponent(token) : null;
  }
}

export const apiClient = new APIClient();
