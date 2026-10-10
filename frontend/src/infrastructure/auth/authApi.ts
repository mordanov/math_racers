import { apiClient } from '../api-client';

export function login(email: string, password: string): Promise<{ access_token: string }> {
  return apiClient.post<{ access_token: string }>('/auth/login', { email, password });
}

export function register(email: string, password: string): Promise<void> {
  return apiClient.post<void>('/auth/register', { email, password });
}

export function refreshToken(): Promise<{ access_token: string }> {
  return apiClient.post<{ access_token: string }>('/auth/refresh');
}

export function logout(): Promise<void> {
  return apiClient.post<void>('/auth/logout');
}
