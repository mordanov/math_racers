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
  selectChild: (childId: string) => void;
}

function decodeToken(token: string): Account {
  const payload = JSON.parse(atob(token.split('.')[1]));
  return { id: payload.sub, email: payload.email, role: payload.role };
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [account, setAccount] = useState<Account | null>(null);
  const [activeChildId, setActiveChildId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const refreshTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const applyToken = useCallback((token: string) => {
    apiClient.setAuthToken(token);
    setAccount(decodeToken(token));
    // Schedule silent refresh 2 min before 15-min TTL
    if (refreshTimer.current) clearTimeout(refreshTimer.current);
    refreshTimer.current = setTimeout(
      async () => {
        try {
          const { access_token } = await refreshToken();
          applyToken(access_token);
        } catch {
          setAccount(null);
          apiClient.setAuthToken(null);
        }
      },
      13 * 60 * 1000,
    );
  }, []);

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
    apiClient.setAuthToken(null);
    setAccount(null);
    setActiveChildId(null);
  }, []);

  const selectChild = useCallback((childId: string) => {
    setActiveChildId(childId);
  }, []);

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
