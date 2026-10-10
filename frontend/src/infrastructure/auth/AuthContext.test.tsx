import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider, useAuth } from './AuthContext';
import * as authApi from './authApi';

vi.mock('./authApi');

const { mockSetAuthToken } = vi.hoisted(() => ({ mockSetAuthToken: vi.fn() }));

vi.mock('../api-client', () => ({
  apiClient: { setAuthToken: mockSetAuthToken, setActiveChildId: vi.fn() },
  APIError: class extends Error {
    constructor(
      public status: number,
      public body: unknown,
    ) {
      super(`HTTP ${status}`);
    }
  },
}));

function TestConsumer() {
  const auth = useAuth();
  return (
    <div>
      <span data-testid="email">{auth.account?.email ?? 'none'}</span>
      <span data-testid="child">{auth.activeChildId ?? 'none'}</span>
      <span data-testid="loading">{String(auth.isLoading)}</span>
      <button
        onClick={() => {
          void auth.login('a@b.com', 'pass');
        }}
      >
        login
      </button>
      <button
        onClick={() => {
          void auth.logout();
        }}
      >
        logout
      </button>
      <button onClick={() => auth.selectChild('child-1')}>select</button>
    </div>
  );
}

// Minimal valid JWT with payload {"sub":"u1","email":"a@b.com","role":"parent","exp":9999999999}
const PAYLOAD = btoa(
  JSON.stringify({ sub: 'u1', email: 'a@b.com', role: 'parent', exp: 9999999999 }),
);
const HEADER = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
const FAKE_TOKEN = `${HEADER}.${PAYLOAD}.sig`;

describe('AuthContext', () => {
  beforeEach(() => {
    vi.mocked(authApi.refreshToken).mockRejectedValue(new Error('no session'));
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('starts unauthenticated after failed silent refresh', async () => {
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );
    await screen.findByTestId('email');
    // Wait for isLoading to settle
    expect(await screen.findByTestId('loading')).toHaveTextContent('false');
    expect(screen.getByTestId('email')).toHaveTextContent('none');
  });

  it('login sets account and calls setAuthToken', async () => {
    vi.mocked(authApi.login).mockResolvedValue({ access_token: FAKE_TOKEN });
    const user = userEvent.setup();
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );
    await screen.findByTestId('loading');
    expect(await screen.findByTestId('loading')).toHaveTextContent('false');

    await user.click(screen.getByText('login'));
    expect(screen.getByTestId('email')).toHaveTextContent('a@b.com');
    expect(mockSetAuthToken).toHaveBeenCalledWith(FAKE_TOKEN);
  });

  it('selectChild updates activeChildId', async () => {
    vi.mocked(authApi.login).mockResolvedValue({ access_token: FAKE_TOKEN });
    const user = userEvent.setup();
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );
    expect(await screen.findByTestId('loading')).toHaveTextContent('false');

    await user.click(screen.getByText('select'));
    expect(screen.getByTestId('child')).toHaveTextContent('child-1');
  });

  it('logout clears account and calls setAuthToken(null)', async () => {
    vi.mocked(authApi.logout).mockResolvedValue(undefined);
    const user = userEvent.setup();
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );
    expect(await screen.findByTestId('loading')).toHaveTextContent('false');

    await user.click(screen.getByText('logout'));
    expect(mockSetAuthToken).toHaveBeenCalledWith(null);
    expect(screen.getByTestId('email')).toHaveTextContent('none');
  });

  it('silent refresh on mount sets account when token found', async () => {
    vi.mocked(authApi.refreshToken).mockResolvedValue({ access_token: FAKE_TOKEN });
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );
    expect(await screen.findByTestId('email')).toHaveTextContent('a@b.com');
  });

  it('handles base64url tokens (production JWT format)', async () => {
    // Real JWTs use base64url: '+' → '-', '/' → '_', no '=' padding.
    // btoa(JSON.stringify({...extra:'>>>>'})) produces standard base64 with '+' in it.
    const payloadObj = {
      sub: 'u1',
      email: 'a@b.com',
      role: 'parent',
      exp: 9999999999,
      extra: '>>>>',
    };
    const b64url = btoa(JSON.stringify(payloadObj))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '');
    const base64urlToken = `${HEADER}.${b64url}.sig`;
    vi.mocked(authApi.login).mockResolvedValue({ access_token: base64urlToken });
    const user = userEvent.setup();
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );
    expect(await screen.findByTestId('loading')).toHaveTextContent('false');
    await user.click(screen.getByText('login'));
    expect(screen.getByTestId('email')).toHaveTextContent('a@b.com');
  });

  it('does not call setAuthToken for malformed JWT', async () => {
    vi.mocked(authApi.login).mockResolvedValue({ access_token: 'header.INVALID!.sig' });
    const user = userEvent.setup();
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>,
    );
    expect(await screen.findByTestId('loading')).toHaveTextContent('false');
    await user.click(screen.getByText('login'));
    expect(mockSetAuthToken).not.toHaveBeenCalledWith('header.INVALID!.sig');
  });
});
