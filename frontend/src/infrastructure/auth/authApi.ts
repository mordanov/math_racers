import { APIError } from '../api-client';

const BASE = '/api/v1/auth';

async function authPost<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(BASE + path, {
    method: 'POST',
    headers: body !== undefined ? { 'Content-Type': 'application/json' } : {},
    body: body !== undefined ? JSON.stringify(body) : undefined,
    credentials: 'same-origin',
  });
  if (response.status === 204) return undefined as unknown as T;
  if (!response.ok) throw new APIError(response.status, await response.json().catch(() => ({})));
  return response.json() as Promise<T>;
}

export function login(email: string, password: string): Promise<{ access_token: string }> {
  return authPost('/login', { email, password });
}

export function register(email: string, password: string): Promise<void> {
  return authPost('/register', { email, password });
}

export function refreshToken(): Promise<{ access_token: string }> {
  return authPost('/refresh');
}

export function logout(): Promise<void> {
  return authPost('/logout');
}
