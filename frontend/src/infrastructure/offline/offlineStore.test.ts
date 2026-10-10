import { afterEach, describe, expect, it, vi } from 'vitest';
import type { RaceSummary } from '../../engine/race/types';
import {
  cacheChildData,
  deleteCachedChildData,
  getCachedChildData,
  listPendingTrainingResults,
  queueTrainingResult,
  removePendingTrainingResult,
} from './offlineStore';

const childProfileId = 'child-1';
const summary: RaceSummary = {
  race_id: 'race-1',
  idempotency_key: 'race-1',
  mode: 'training',
  human_avatar_id: 'avatar-1',
  started_at: '2026-01-01T00:00:00.000Z',
  completed_at: '2026-01-01T00:01:00.000Z',
  participants: [],
  answers: [],
};

function installIndexedDbMock(): void {
  const stores = new Map<string, Map<IDBValidKey, unknown>>();
  const keyPaths = new Map<string, string>();
  const storeNames = new Set<string>();
  let initialized = false;
  const database = {
    objectStoreNames: {
      contains: (name: string) => storeNames.has(name),
    },
    createObjectStore: (name: string, options: { keyPath: string }) => {
      storeNames.add(name);
      stores.set(name, new Map());
      keyPaths.set(name, options.keyPath);
      return { name, keyPath: options.keyPath };
    },
    transaction: (_name: string | string[]) => {
      const transaction: {
        oncomplete: (() => void) | null;
        onabort: (() => void) | null;
        onerror: (() => void) | null;
        error: DOMException | null;
        objectStore: (storeName: string) => {
          put: (value: Record<string, unknown>) => void;
          get: (key: IDBValidKey) => IDBRequest;
          getAll: () => IDBRequest;
          delete: (key: IDBValidKey) => void;
        };
      } = {
        oncomplete: null,
        onabort: null,
        onerror: null,
        error: null,
        objectStore: (storeName) => ({
          put(value) {
            const key = value[keyPaths.get(storeName)!];
            stores.get(storeName)!.set(key as IDBValidKey, value);
            queueMicrotask(() => transaction.oncomplete?.());
          },
          get(key) {
            const request: {
              result: unknown;
              onsuccess: (() => void) | null;
              onerror: (() => void) | null;
            } = { result: undefined, onsuccess: null, onerror: null };
            queueMicrotask(() => {
              request.result = stores.get(storeName)!.get(key);
              request.onsuccess?.();
              queueMicrotask(() => transaction.oncomplete?.());
            });
            return request as unknown as IDBRequest;
          },
          getAll() {
            const request: {
              result: unknown;
              onsuccess: (() => void) | null;
              onerror: (() => void) | null;
            } = { result: [], onsuccess: null, onerror: null };
            queueMicrotask(() => {
              request.result = [...stores.get(storeName)!.values()];
              request.onsuccess?.();
              queueMicrotask(() => transaction.oncomplete?.());
            });
            return request as unknown as IDBRequest;
          },
          delete(key) {
            stores.get(storeName)!.delete(key);
            queueMicrotask(() => transaction.oncomplete?.());
          },
        }),
      };
      return transaction as unknown as IDBTransaction;
    },
    close: () => undefined,
  };

  vi.stubGlobal('indexedDB', {
    open: () => {
      const request = {
        result: database,
        onupgradeneeded: null as (() => void) | null,
        onsuccess: null as (() => void) | null,
        onerror: null,
      };
      queueMicrotask(() => {
        if (!initialized) {
          initialized = true;
          request.onupgradeneeded?.();
        }
        request.onsuccess?.();
      });
      return request as unknown as IDBOpenDBRequest;
    },
  } as unknown as IDBFactory);
}

describe('offlineStore', () => {
  afterEach(() => vi.unstubAllGlobals());

  it('stores child-specific avatars, statistics, and a reserved Training session', async () => {
    installIndexedDbMock();
    const data = {
      child_profile_id: childProfileId,
      avatars: [],
      statistics: null,
      training_session: {
        race_id: 'reserved-race',
        seed: 123,
        tier: 1 as const,
        avatar_id: 'avatar-1',
        avatar_species: 'fox',
      },
    };

    await cacheChildData(data);

    expect(await getCachedChildData(childProfileId)).toEqual(data);
    expect(await getCachedChildData('another-child')).toBeNull();
  });

  it('keeps queued Training results until they are confirmed', async () => {
    installIndexedDbMock();
    const pending = {
      idempotency_key: 'result-1',
      child_profile_id: childProfileId,
      summary,
      player_avatar_id: 'avatar-1',
      avatar_species: 'fox',
      created_at: '2026-01-01T00:01:00.000Z',
    };

    await queueTrainingResult(pending);
    await queueTrainingResult(pending);
    expect(await listPendingTrainingResults()).toEqual([pending]);

    await removePendingTrainingResult(pending.idempotency_key);
    expect(await listPendingTrainingResults()).toEqual([]);
  });

  it('deletes one child cache and pending results without deleting another child data', async () => {
    installIndexedDbMock();
    await cacheChildData({
      child_profile_id: childProfileId,
      avatars: [],
      statistics: null,
      training_session: null,
    });
    await cacheChildData({
      child_profile_id: 'child-2',
      avatars: [],
      statistics: null,
      training_session: null,
    });
    await queueTrainingResult({
      idempotency_key: 'result-1',
      child_profile_id: childProfileId,
      summary,
      player_avatar_id: 'avatar-1',
      avatar_species: 'fox',
      created_at: '2026-01-01T00:01:00.000Z',
    });
    await queueTrainingResult({
      idempotency_key: 'result-2',
      child_profile_id: 'child-2',
      summary,
      player_avatar_id: 'avatar-2',
      avatar_species: 'fox',
      created_at: '2026-01-01T00:02:00.000Z',
    });

    await deleteCachedChildData(childProfileId);

    expect(await getCachedChildData(childProfileId)).toBeNull();
    expect(await getCachedChildData('child-2')).not.toBeNull();
    expect(await listPendingTrainingResults()).toEqual([
      expect.objectContaining({ idempotency_key: 'result-2' }),
    ]);
  });
});
