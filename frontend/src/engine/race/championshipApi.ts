import { apiClient } from '../../infrastructure/api-client';

export interface StandingEntry {
  avatar_id: string;
  is_player: boolean;
  points: number;
  podiums: number;
  position: number;
}

export interface ChampionshipState {
  championship_id: string;
  total_races: number;
  races_completed: number;
  status: 'active' | 'completed';
  standings: StandingEntry[];
  completion_xp_awarded?: number;
}

export interface RecordRaceParticipant {
  avatar_id: string;
  is_player: boolean;
  finishing_position: number;
}

export async function createChampionship(totalRaces: number): Promise<ChampionshipState> {
  return apiClient.post<ChampionshipState>('/championships', { total_races: totalRaces });
}

export async function getChampionship(championshipId: string): Promise<ChampionshipState> {
  return apiClient.get<ChampionshipState>(`/championships/${championshipId}`);
}

export async function recordChampionshipRace(
  championshipId: string,
  raceId: string,
  raceIndex: number,
  participants: RecordRaceParticipant[],
): Promise<ChampionshipState> {
  return apiClient.patch<ChampionshipState>(`/championships/${championshipId}/races/${raceId}`, {
    race_index: raceIndex,
    participants,
  });
}
