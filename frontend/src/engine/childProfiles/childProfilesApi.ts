import { apiClient } from '../../infrastructure/api-client';

export type LegacyRecordType =
  'avatar' | 'avatar_stats' | 'achievement' | 'race' | 'statistics' | 'xp_event' | 'championship';

export interface LegacyRecord {
  record_type: LegacyRecordType;
  record_id: string;
  label: string;
}

export interface LegacyRecordAssignment {
  record_type: LegacyRecordType;
  record_id: string;
}

export async function listLegacyData(childProfileId: string): Promise<LegacyRecord[]> {
  const response = await apiClient.get<{ records: LegacyRecord[] }>(
    `/child-profiles/${childProfileId}/legacy-data`,
  );
  return response.records;
}

export function assignLegacyData(
  childProfileId: string,
  records: LegacyRecordAssignment[],
): Promise<{ assigned: number }> {
  return apiClient.post<{ assigned: number }>(
    `/child-profiles/${childProfileId}/legacy-data/assign`,
    { records },
  );
}

export function exportChildData(childProfileId: string): Promise<Record<string, unknown>> {
  return apiClient.get<Record<string, unknown>>(`/child-profiles/${childProfileId}/export`);
}

export function deleteChildProfile(childProfileId: string): Promise<void> {
  return apiClient.delete(`/child-profiles/${childProfileId}`);
}
