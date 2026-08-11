import type {
  AvatarCreationResponse,
  AvatarDetail,
  AvatarListItem,
  CreateAvatarRequest,
  JobStatusResponse,
  PatchAvatarRequest,
} from './types';

const BASE = '/api/v1/avatars';

interface ApiError {
  message?: string;
  error_code?: string;
}

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(url, { credentials: 'include', ...init });
  if (!resp.ok) {
    const body = (await resp.json().catch(() => ({}))) as ApiError;
    throw Object.assign(new Error(body.message ?? `HTTP ${resp.status}`), {
      status: resp.status,
      error_code: body.error_code,
    });
  }
  if (resp.status === 204) return undefined as unknown as T;
  return resp.json() as Promise<T>;
}

export async function createAvatar(data: CreateAvatarRequest): Promise<AvatarCreationResponse> {
  return request<AvatarCreationResponse>(BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}

export async function pollGenerationJob(
  avatarId: string,
  jobId: string,
): Promise<JobStatusResponse> {
  return request<JobStatusResponse>(`${BASE}/${avatarId}/jobs/${jobId}`);
}

export async function listAvatars(): Promise<AvatarListItem[]> {
  return request<AvatarListItem[]>(BASE);
}

export async function getAvatar(avatarId: string): Promise<AvatarDetail> {
  return request<AvatarDetail>(`${BASE}/${avatarId}`);
}

export async function patchAvatar(
  avatarId: string,
  data: PatchAvatarRequest,
): Promise<AvatarDetail> {
  return request<AvatarDetail>(`${BASE}/${avatarId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
}

export async function regeneratePortrait(avatarId: string): Promise<AvatarCreationResponse> {
  return request<AvatarCreationResponse>(`${BASE}/${avatarId}/regenerate`, {
    method: 'POST',
  });
}

export async function deleteAvatar(avatarId: string): Promise<void> {
  return request<void>(`${BASE}/${avatarId}`, { method: 'DELETE' });
}
