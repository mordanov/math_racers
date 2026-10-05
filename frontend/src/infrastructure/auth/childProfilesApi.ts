import { apiClient } from '../api-client';
import type { ChildProfile } from './types';

interface ChildProfileListResponse {
  profiles: ChildProfile[];
}

export async function fetchChildProfiles(): Promise<ChildProfile[]> {
  const data = await apiClient.get<ChildProfileListResponse>('/child-profiles');
  return data.profiles;
}

export async function createChildProfile(displayName: string): Promise<ChildProfile> {
  return apiClient.post<ChildProfile>('/child-profiles', { display_name: displayName });
}

export async function deleteChildProfile(profileId: string): Promise<void> {
  return apiClient.delete(`/child-profiles/${profileId}`);
}
