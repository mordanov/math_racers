export type AvatarStatus = 'pending' | 'published' | 'failed';

export type JobStatus =
  | 'queued'
  | 'llm_running'
  | 'prompt_building'
  | 'generating'
  | 'validating'
  | 'storing'
  | 'complete'
  | 'failed';

export interface PortraitSummary {
  id: string;
  version: number;
  prompt_version: string;
  model_version: string;
  full_url: string;
  medium_url: string;
  small_url: string;
  thumb_url: string;
  created_at: string;
}

export interface AvatarCreationResponse {
  avatar_id: string;
  job_id: string;
  status: JobStatus;
}

export interface JobStatusResponse {
  job_id: string;
  avatar_id: string;
  status: JobStatus;
  attempt: number;
  error: string | null;
  created_at: string;
  completed_at: string | null;
}

export interface AvatarListItem {
  avatar_id: string;
  name: string | null;
  species: string;
  status: AvatarStatus;
  is_favourite: boolean;
  portrait: PortraitSummary | null;
  created_at: string;
}

export interface AvatarDetail {
  avatar_id: string;
  species: string;
  fur_color: string;
  eye_color: string;
  hairstyle: string;
  accessories: string[];
  clothes_top_color: string;
  clothes_bottom_color: string;
  name: string | null;
  personality: string | null;
  biography: string | null;
  appearance_summary: string | null;
  favorite_subject: string | null;
  running_style: string | null;
  status: AvatarStatus;
  is_favourite: boolean;
  active_portrait_id: string | null;
  portrait: PortraitSummary | null;
  portrait_history: PortraitSummary[];
  created_at: string;
}

export interface CreateAvatarRequest {
  species: string;
  fur_color?: string;
  eye_color?: string;
  hairstyle?: string;
  accessories?: string[];
  clothes_top_color?: string;
  clothes_bottom_color?: string;
}

export interface PatchAvatarRequest {
  name?: string;
  is_favourite?: boolean;
  active_portrait_id?: string;
}
