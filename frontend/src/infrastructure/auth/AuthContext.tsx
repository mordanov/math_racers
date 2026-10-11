import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import { apiClient } from '../api-client';
import { login as apiLogin, logout as apiLogout, refreshToken } from './authApi';
import type { Account } from './types';

interface AuthState {
  account: Account | null;
  activeChildId: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  selectChild: (childId: string | null) => void;
}

interface JwtPayload {
  sub: string;
  email: string;
  role: 'parent' | 'administrator';
  exp: number;
}

const ACTIVE_CHILD_STORAGE_PREFIX = 'math-racers-active-child:';
const MAX_TIMEOUT_MS = 2_147_483_647;

function activeChildStorageKey(accountId: string): string {
  return `${ACTIVE_CHILD_STORAGE_PREFIX}${accountId}`;
}

function decodeToken(token: string): { account: Account; expiresAt: number } {
  const b64url = token.split('.')[1];
  const b64 = b64url.replace(/-/g, '+').replace(/_/g, '/');
  const padded = b64 + '=='.slice(0, (4 - (b64.length % 4)) % 4);
  const payload = JSON.parse(atob(padded)) as JwtPayload;
  if (!Number.isFinite(payload.exp)) throw new Error('JWT expiration is missing.');
  return {
    account: { id: payload.sub, email: payload.email, role: payload.role },
    expiresAt: payload.exp * 1000,
  };
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [account, setAccount] = useState<Account | null>(null);
  const [activeChildId, setActiveChildId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const refreshTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const applyToken = useCallback((token: string) => {
    let decoded: ReturnType<typeof decodeToken>;
    try {
      decoded = decodeToken(token);
    } catch {
      return;
    }
    const storedChildId = sessionStorage.getItem(activeChildStorageKey(decoded.account.id));
    apiClient.setAuthToken(token);
    apiClient.setActiveChildId(storedChildId);
    setAccount(decoded.account);
    setActiveChildId(storedChildId);
    if (refreshTimer.current) clearTimeout(refreshTimer.current);
    refreshTimer.current = setTimeout(
      () => {
        void refreshToken()
          .then(({ access_token }) => {
            applyToken(access_token);
          })
          .catch(() => {
            setAccount(null);
            apiClient.setAuthToken(null);
            apiClient.setActiveChildId(null);
            setActiveChildId(null);
          });
      },
      Math.min(MAX_TIMEOUT_MS, Math.max(0, decoded.expiresAt - Date.now() - 2 * 60 * 1000)),
    );
  }, []);

  useEffect(() => {
    apiClient.setActiveChildId(activeChildId);
  }, [activeChildId]);

  useEffect(() => {
    refreshToken()
      .then(({ access_token }) => applyToken(access_token))
      .catch(() => {})
      .finally(() => setIsLoading(false));
    return () => {
      if (refreshTimer.current) clearTimeout(refreshTimer.current);
    };
  }, [applyToken]);

  const login = useCallback(
    async (email: string, password: string) => {
      const { access_token } = await apiLogin(email, password);
      applyToken(access_token);
    },
    [applyToken],
  );

  const logout = useCallback(async () => {
    await apiLogout().catch(() => {});
    if (refreshTimer.current) clearTimeout(refreshTimer.current);
    if (account) sessionStorage.removeItem(activeChildStorageKey(account.id));
    apiClient.setAuthToken(null);
    apiClient.setActiveChildId(null);
    setAccount(null);
    setActiveChildId(null);
  }, [account]);

  const selectChild = useCallback(
    (childId: string | null) => {
      setActiveChildId(childId);
      apiClient.setActiveChildId(childId);
      if (account) {
        const storageKey = activeChildStorageKey(account.id);
        if (childId) sessionStorage.setItem(storageKey, childId);
        else sessionStorage.removeItem(storageKey);
      }
    },
    [account],
  );

  return (
    <AuthContext.Provider
      value={{
        account,
        activeChildId,
        isAuthenticated: account !== null,
        isLoading,
        login,
        logout,
        selectChild,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
