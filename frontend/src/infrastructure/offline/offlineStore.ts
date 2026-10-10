import type { AvatarListItem } from '../../engine/avatar/types';
import type { Tier } from '../../engine/math/types';
import type { RaceSummary } from '../../engine/race/types';
import type { PlayerStats } from '../../features/statistics/statisticsApi';

const DATABASE_NAME = 'math-racers-offline';
const DATABASE_VERSION = 1;
const CHILD_DATA_STORE = 'child-data';
const PENDING_RESULTS_STORE = 'pending-training-results';

export interface CachedTrainingSession {
  race_id: string;
  seed: number;
  tier: Tier;
  avatar_id: string;
  avatar_species: string;
}

export interface CachedChildData {
  child_profile_id: string;
  avatars: AvatarListItem[];
  statistics: PlayerStats | null;
  training_session: CachedTrainingSession | null;
}

export interface PendingTrainingResult {
  idempotency_key: string;
  child_profile_id: string;
  summary: RaceSummary;
  player_avatar_id: string;
  avatar_species: string;
  created_at: string;
}

function openDatabase(): Promise<IDBDatabase> {
  if (typeof indexedDB === 'undefined') {
    return Promise.reject(new Error('Offline storage is not available in this browser.'));
  }

  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DATABASE_NAME, DATABASE_VERSION);
    request.onupgradeneeded = () => {
      const database = request.result;
      if (!database.objectStoreNames.contains(CHILD_DATA_STORE)) {
        database.createObjectStore(CHILD_DATA_STORE, { keyPath: 'child_profile_id' });
      }
      if (!database.objectStoreNames.contains(PENDING_RESULTS_STORE)) {
        database.createObjectStore(PENDING_RESULTS_STORE, { keyPath: 'idempotency_key' });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error ?? new Error('Could not open offline storage.'));
  });
}

function transactionDone(transaction: IDBTransaction): Promise<void> {
  return new Promise((resolve, reject) => {
    transaction.oncomplete = () => resolve();
    transaction.onabort = () =>
      reject(transaction.error ?? new Error('Offline storage transaction was aborted.'));
    transaction.onerror = () =>
      reject(transaction.error ?? new Error('Offline storage transaction failed.'));
  });
}

export async function getCachedChildData(childProfileId: string): Promise<CachedChildData | null> {
  const database = await openDatabase();
  try {
    const transaction = database.transaction(CHILD_DATA_STORE, 'readonly');
    const done = transactionDone(transaction);
    const result = await new Promise<CachedChildData | null>((resolve, reject) => {
      const request = transaction.objectStore(CHILD_DATA_STORE).get(childProfileId);
      request.onsuccess = () => resolve((request.result as CachedChildData | undefined) ?? null);
      request.onerror = () =>
        reject(request.error ?? new Error('Could not read cached child data.'));
    });
    await done;
    return result;
  } finally {
    database.close();
  }
}

export async function cacheChildData(data: CachedChildData): Promise<void> {
  const database = await openDatabase();
  try {
    const transaction = database.transaction(CHILD_DATA_STORE, 'readwrite');
    transaction.objectStore(CHILD_DATA_STORE).put(data);
    await transactionDone(transaction);
  } finally {
    database.close();
  }
}

export async function queueTrainingResult(result: PendingTrainingResult): Promise<void> {
  const database = await openDatabase();
  try {
    const transaction = database.transaction(PENDING_RESULTS_STORE, 'readwrite');
    transaction.objectStore(PENDING_RESULTS_STORE).put(result);
    await transactionDone(transaction);
  } finally {
    database.close();
  }
}

export async function listPendingTrainingResults(): Promise<PendingTrainingResult[]> {
  const database = await openDatabase();
  try {
    const transaction = database.transaction(PENDING_RESULTS_STORE, 'readonly');
    const done = transactionDone(transaction);
    const results = await new Promise<PendingTrainingResult[]>((resolve, reject) => {
      const request = transaction.objectStore(PENDING_RESULTS_STORE).getAll();
      request.onsuccess = () => resolve(request.result as PendingTrainingResult[]);
      request.onerror = () =>
        reject(request.error ?? new Error('Could not read pending Training results.'));
    });
    await done;
    return results;
  } finally {
    database.close();
  }
}

export async function removePendingTrainingResult(idempotencyKey: string): Promise<void> {
  const database = await openDatabase();
  try {
    const transaction = database.transaction(PENDING_RESULTS_STORE, 'readwrite');
    transaction.objectStore(PENDING_RESULTS_STORE).delete(idempotencyKey);
    await transactionDone(transaction);
  } finally {
    database.close();
  }
}

export async function deleteCachedChildData(childProfileId: string): Promise<void> {
  const database = await openDatabase();
  try {
    const transaction = database.transaction(
      [CHILD_DATA_STORE, PENDING_RESULTS_STORE],
      'readwrite',
    );
    const done = transactionDone(transaction);
    transaction.objectStore(CHILD_DATA_STORE).delete(childProfileId);
    const pendingStore = transaction.objectStore(PENDING_RESULTS_STORE);
    await new Promise<void>((resolve, reject) => {
      const request = pendingStore.getAll();
      request.onsuccess = () => {
        const pending = request.result as PendingTrainingResult[];
        pending
          .filter((result) => result.child_profile_id === childProfileId)
          .forEach((result) => pendingStore.delete(result.idempotency_key));
        resolve();
      };
      request.onerror = () =>
        reject(request.error ?? new Error('Could not read pending Training results.'));
    });
    await done;
  } finally {
    database.close();
  }
}
