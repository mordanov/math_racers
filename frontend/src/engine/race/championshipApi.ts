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
}

export interface RecordRaceParticipant {
  avatar_id: string;
  is_player: boolean;
  finishing_position: number;
}

async function request<T>(url: string, init: RequestInit): Promise<T> {
  const resp = await fetch(url, { ...init, credentials: 'include' });
  if (!resp.ok) {
    throw new Error(`${init.method ?? 'GET'} ${url} failed: ${resp.status}`);
  }
  return resp.json() as Promise<T>;
}

export async function createChampionship(totalRaces: number): Promise<ChampionshipState> {
  return request<ChampionshipState>('/api/v1/championships', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ total_races: totalRaces }),
  });
}

export async function getChampionship(championshipId: string): Promise<ChampionshipState> {
  return request<ChampionshipState>(`/api/v1/championships/${championshipId}`, {
    method: 'GET',
  });
}

export async function recordChampionshipRace(
  championshipId: string,
  raceId: string,
  raceIndex: number,
  participants: RecordRaceParticipant[],
): Promise<ChampionshipState> {
  return request<ChampionshipState>(`/api/v1/championships/${championshipId}/races/${raceId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ race_index: raceIndex, participants }),
  });
}
