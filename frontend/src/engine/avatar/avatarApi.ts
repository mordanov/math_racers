import type {
  AvatarCreationResponse,
  AvatarDetail,
  AvatarListItem,
  CreateAvatarRequest,
  JobStatusResponse,
  PatchAvatarRequest,
} from './types';
import { apiClient } from '../../infrastructure/api-client';

export async function createAvatar(data: CreateAvatarRequest): Promise<AvatarCreationResponse> {
  return apiClient.post<AvatarCreationResponse>('/avatars', data);
}

export async function pollGenerationJob(
  avatarId: string,
  jobId: string,
): Promise<JobStatusResponse> {
  return apiClient.get<JobStatusResponse>(`/avatars/${avatarId}/jobs/${jobId}`);
}

export async function listAvatars(): Promise<AvatarListItem[]> {
  return apiClient.get<AvatarListItem[]>('/avatars');
}

export async function getAvatar(avatarId: string): Promise<AvatarDetail> {
  return apiClient.get<AvatarDetail>(`/avatars/${avatarId}`);
}

export async function patchAvatar(
  avatarId: string,
  data: PatchAvatarRequest,
): Promise<AvatarDetail> {
  return apiClient.patch<AvatarDetail>(`/avatars/${avatarId}`, data);
}

export async function regeneratePortrait(avatarId: string): Promise<AvatarCreationResponse> {
  return apiClient.post<AvatarCreationResponse>(`/avatars/${avatarId}/regenerate`);
}

export async function deleteAvatar(avatarId: string): Promise<void> {
  return apiClient.delete(`/avatars/${avatarId}`);
}
