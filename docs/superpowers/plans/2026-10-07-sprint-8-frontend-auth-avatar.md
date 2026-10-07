# Sprint 8: Auth Page Styling + Avatar Gallery Completion

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply token-based styling to the three auth pages, add a `RequireParent` role guard for `/parent`, and complete the avatar gallery with favourite toggle, rename, regenerate, and delete.

**Architecture:** Auth pages gain a centred card layout using the existing `tokens.ts` inline-style pattern; no new shared component is needed. The gallery hook (`useAvatarGallery`) gains four mutation functions with optimistic updates; `AvatarCard` gains optional callback props that activate the favourite star and manage menu. `AvatarGalleryPage` wires the two together and shows a dismissible error banner on mutation failures.

**Tech Stack:** React 18, TypeScript, Vitest + Testing Library, React Router v6, inline tokens (no CSS files, no new npm dependencies)

**Spec:** `docs/superpowers/specs/2026-10-07-sprint-8-frontend-auth-avatar.md`

## Global Constraints

- All styling via `tokens` (inline `React.CSSProperties`); no new CSS files, no Tailwind.
- No new npm dependencies.
- `<Button>`, `<Card>`, `<ConfirmDialog>`, `<LoadingSpinner>` — use existing, do not re-implement.
- Tests: Vitest + Testing Library. Module-level mocks via `vi.hoisted()`, never via `vi.mock(module, factory)` with inline object references.
- Array helpers: `Array.from({ length: n }, () => v)`, never `Array(n).fill(v)`.
- `eslint-disable-next-line react-hooks/exhaustive-deps` is forbidden.
- Every frontend test file lives alongside its source file in `frontend/src/`.
- Test command (run from `frontend/`): `npm test`

---

## Review Focus

1. **`administrator` role blocked from `/parent`** — a logged-in administrator visiting `/parent` should land on `/`, not an error. Task 1 adds this test.
2. **Rename save disabled on empty input** — pressing Save or Enter on a blank rename field must not call `onRename`. Task 6 adds this test.
3. **`removeAvatar` restores item at correct list index on API error** — avatar removed optimistically must be spliced back in at its original position, not appended. Task 5 adds this test.
4. **Mutation error banner dismissal** — the error banner must have a visible close (×) button that clears `mutationError`; otherwise the only way to clear it is a successful mutation. Task 7 adds this test.
5. **Long avatar name trimmed before `onRename` call** — if the user types leading/trailing spaces in the rename field, `onRename` receives the trimmed string. Task 6 adds this test.

---

## File Map

**Create:**
- `frontend/src/infrastructure/auth/RequireParent.tsx` (Task 1)
- `frontend/src/infrastructure/auth/RequireParent.test.tsx` (Task 1)
- `frontend/src/features/avatar/useAvatarGallery.test.ts` — expand existing file (Task 5)
- `frontend/src/features/avatar/AvatarCard.test.tsx` — expand existing file (Task 6)

**Modify:**
- `frontend/src/router.tsx` — wrap `/parent` in `<RequireParent>` (Task 1)
- `frontend/src/pages/LoginPage.tsx` — card layout + styled inputs + nav link (Task 2)
- `frontend/src/pages/LoginPage.test.tsx` — add nav link test (Task 2)
- `frontend/src/pages/RegisterPage.tsx` — card layout + nav link (Task 3)
- `frontend/src/pages/RegisterPage.test.tsx` — add nav link test (Task 3)
- `frontend/src/pages/ChildProfileSelectPage.tsx` — grid layout + styled profile cards (Task 4)
- `frontend/src/pages/ChildProfileSelectPage.test.tsx` — add grid / add-form tests (Task 4)
- `frontend/src/features/avatar/useAvatarGallery.ts` — add 4 mutations + `mutationError` (Task 5)
- `frontend/src/features/avatar/AvatarCard.tsx` — add favourite star + manage menu (Task 6)
- `frontend/src/pages/AvatarGalleryPage.tsx` — wire mutations + error banner (Task 7)
- `frontend/src/pages/AvatarGalleryPage.test.tsx` — add wiring + banner tests (Task 7)

---

### Task 1: RequireParent guard + router wiring

**Files:**
- Create: `frontend/src/infrastructure/auth/RequireParent.tsx`
- Create: `frontend/src/infrastructure/auth/RequireParent.test.tsx`
- Modify: `frontend/src/router.tsx`

**Interfaces:**
- Consumes: `useAuth` from `./AuthContext` (returns `{ account, isLoading }`)
- Produces: `default export function RequireParent()` — used by Task 7 indirectly via the router

- [ ] **Step 1: Write the failing test**

Create `frontend/src/infrastructure/auth/RequireParent.test.tsx`:

```tsx
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import RequireParent from './RequireParent';
import * as AuthContextModule from './AuthContext';

vi.mock('./AuthContext');
vi.mock('../../shared/components/LoadingSpinner', () => ({
  LoadingSpinner: () => <div data-testid="spinner">Loading</div>,
}));

function setup(role: 'parent' | 'administrator' | null, isLoading = false) {
  vi.mocked(AuthContextModule.useAuth).mockReturnValue({
    account: role ? { id: 'u1', email: 'a@b.com', role } : null,
    isLoading,
    isAuthenticated: role !== null,
    activeChildId: null,
    login: vi.fn(),
    logout: vi.fn(),
    selectChild: vi.fn(),
  });
  return render(
    <MemoryRouter initialEntries={['/parent']}>
      <Routes>
        <Route element={<RequireParent />}>
          <Route path="/parent" element={<div>Parent Dashboard</div>} />
        </Route>
        <Route path="/" element={<div>Home</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('RequireParent', () => {
  it('renders child routes for parent role', () => {
    setup('parent');
    expect(screen.getByText('Parent Dashboard')).toBeInTheDocument();
  });

  it('redirects to / for administrator role (Review Focus #1)', () => {
    setup('administrator');
    expect(screen.getByText('Home')).toBeInTheDocument();
  });

  it('redirects to / when account is null', () => {
    setup(null);
    expect(screen.getByText('Home')).toBeInTheDocument();
  });

  it('shows LoadingSpinner while auth is loading', () => {
    setup(null, true);
    expect(screen.getByTestId('spinner')).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && npm test -- --reporter=verbose src/infrastructure/auth/RequireParent.test.tsx
```

Expected: FAIL — `RequireParent.tsx` does not exist

- [ ] **Step 3: Implement RequireParent**

Create `frontend/src/infrastructure/auth/RequireParent.tsx`:

```tsx
import { Navigate, Outlet } from 'react-router-dom';
import { LoadingSpinner } from '../../shared/components/LoadingSpinner';
import { useAuth } from './AuthContext';

export default function RequireParent() {
  const { account, isLoading } = useAuth();
  if (isLoading) return <LoadingSpinner message="Loading…" />;
  if (account?.role !== 'parent') return <Navigate to="/" replace />;
  return <Outlet />;
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend && npm test -- --reporter=verbose src/infrastructure/auth/RequireParent.test.tsx
```

Expected: PASS (4/4)

- [ ] **Step 5: Wire RequireParent into the router**

In `frontend/src/router.tsx`, add the import:

```tsx
import RequireParent from './infrastructure/auth/RequireParent';
```

Change the `/parent` route inside the `RequireAuth` children array from:

```tsx
{ path: '/parent', element: <ParentDashboardPage /> },
```

to:

```tsx
{
  element: <RequireParent />,
  children: [{ path: '/parent', element: <ParentDashboardPage /> }],
},
```

- [ ] **Step 6: Run the full suite**

```bash
cd frontend && npm test
```

Expected: all tests pass (no regressions in router.test.tsx or ParentDashboardPage.test.tsx)

- [ ] **Step 7: Commit**

```bash
git add frontend/src/infrastructure/auth/RequireParent.tsx \
        frontend/src/infrastructure/auth/RequireParent.test.tsx \
        frontend/src/router.tsx
git commit -m "feat(auth): add RequireParent role guard; wire /parent route

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 2: LoginPage token-based styling

**Files:**
- Modify: `frontend/src/pages/LoginPage.tsx`
- Modify: `frontend/src/pages/LoginPage.test.tsx`

**Interfaces:**
- Consumes: nothing from other tasks
- Produces: styled LoginPage (no new exports)

- [ ] **Step 1: Write the failing test**

Add one test to the existing `describe('LoginPage')` block in `frontend/src/pages/LoginPage.test.tsx`:

```tsx
it('renders a link to the register page', () => {
  render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>,
  );
  expect(screen.getByRole('link', { name: /register/i })).toHaveAttribute('href', '/register');
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && npm test -- --reporter=verbose src/pages/LoginPage.test.tsx
```

Expected: FAIL — no link with name /register/i

- [ ] **Step 3: Restyle LoginPage**

Replace the full contents of `frontend/src/pages/LoginPage.tsx` with:

```tsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../infrastructure/auth/AuthContext';
import { Button } from '../shared/components/Button';
import tokens from '../shared/tokens';

const pageStyle: React.CSSProperties = {
  minHeight: '100vh',
  background: tokens.color.background,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: tokens.spacing.lg,
};

const cardStyle: React.CSSProperties = {
  background: tokens.color.surface,
  borderRadius: tokens.radius.lg,
  padding: tokens.spacing.xl,
  boxShadow: tokens.shadow.card,
  width: '100%',
  maxWidth: 420,
};

const fieldStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: tokens.spacing.xs,
  marginBottom: tokens.spacing.md,
};

const labelStyle: React.CSSProperties = {
  fontSize: 14,
  fontWeight: 600,
  color: tokens.color.textSecondary,
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: tokens.spacing.sm,
  border: `1px solid ${tokens.color.border}`,
  borderRadius: tokens.radius.sm,
  fontSize: 16,
  color: tokens.color.textPrimary,
  background: tokens.color.surface,
  boxSizing: 'border-box',
};

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      void navigate('/child-profiles');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={pageStyle}>
      <div style={cardStyle}>
        <h1
          style={{
            margin: `0 0 ${tokens.spacing.lg}px`,
            color: tokens.color.textPrimary,
            fontSize: 28,
            fontWeight: 700,
          }}
        >
          Log In
        </h1>
        <form
          onSubmit={(e) => {
            void handleSubmit(e);
          }}
        >
          <div style={fieldStyle}>
            <label htmlFor="email" style={labelStyle}>
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={inputStyle}
              autoComplete="email"
            />
          </div>
          <div style={fieldStyle}>
            <label htmlFor="password" style={labelStyle}>
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={inputStyle}
              autoComplete="current-password"
            />
          </div>
          {error && (
            <p role="alert" style={{ color: tokens.color.error, margin: `0 0 ${tokens.spacing.md}px`, fontSize: 14 }}>
              {error}
            </p>
          )}
          <Button type="submit" variant="primary" loading={loading} disabled={loading}>
            Log In
          </Button>
        </form>
        <p style={{ marginTop: tokens.spacing.lg, textAlign: 'center', color: tokens.color.textSecondary, fontSize: 14 }}>
          Don&apos;t have an account?{' '}
          <Link to="/register" style={{ color: tokens.color.primary, textDecoration: 'none', fontWeight: 600 }}>
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend && npm test -- --reporter=verbose src/pages/LoginPage.test.tsx
```

Expected: PASS (5/5)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/LoginPage.tsx frontend/src/pages/LoginPage.test.tsx
git commit -m "feat(ui): apply token-based styling to LoginPage

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 3: RegisterPage token-based styling

**Files:**
- Modify: `frontend/src/pages/RegisterPage.tsx`
- Modify: `frontend/src/pages/RegisterPage.test.tsx`

**Interfaces:**
- Consumes: same style constants as Task 2 (inline — no shared module)
- Produces: styled RegisterPage (no new exports)

- [ ] **Step 1: Write the failing test**

Add one test to the existing `describe('RegisterPage')` block in `frontend/src/pages/RegisterPage.test.tsx`:

```tsx
it('renders a link to the login page', () => {
  render(
    <MemoryRouter>
      <RegisterPage />
    </MemoryRouter>,
  );
  expect(screen.getByRole('link', { name: /log in/i })).toHaveAttribute('href', '/login');
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && npm test -- --reporter=verbose src/pages/RegisterPage.test.tsx
```

Expected: FAIL — no link with name /log in/i

- [ ] **Step 3: Restyle RegisterPage**

Replace the full contents of `frontend/src/pages/RegisterPage.tsx` with:

```tsx
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { register } from '../infrastructure/auth/authApi';
import { Button } from '../shared/components/Button';
import tokens from '../shared/tokens';

const pageStyle: React.CSSProperties = {
  minHeight: '100vh',
  background: tokens.color.background,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: tokens.spacing.lg,
};

const cardStyle: React.CSSProperties = {
  background: tokens.color.surface,
  borderRadius: tokens.radius.lg,
  padding: tokens.spacing.xl,
  boxShadow: tokens.shadow.card,
  width: '100%',
  maxWidth: 420,
};

const fieldStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: tokens.spacing.xs,
  marginBottom: tokens.spacing.md,
};

const labelStyle: React.CSSProperties = {
  fontSize: 14,
  fontWeight: 600,
  color: tokens.color.textSecondary,
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: tokens.spacing.sm,
  border: `1px solid ${tokens.color.border}`,
  borderRadius: tokens.radius.sm,
  fontSize: 16,
  color: tokens.color.textPrimary,
  background: tokens.color.surface,
  boxSizing: 'border-box',
};

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register(email, password);
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setLoading(false);
    }
  }

  if (success) {
    return (
      <div style={pageStyle}>
        <div style={cardStyle}>
          <p
            role="status"
            style={{ color: tokens.color.success, margin: 0, fontWeight: 600, textAlign: 'center' }}
          >
            Account created. Please wait for an administrator to approve your account.
          </p>
          <p style={{ marginTop: tokens.spacing.lg, textAlign: 'center', color: tokens.color.textSecondary, fontSize: 14 }}>
            <Link to="/login" style={{ color: tokens.color.primary, textDecoration: 'none', fontWeight: 600 }}>
              Log In
            </Link>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={pageStyle}>
      <div style={cardStyle}>
        <h1
          style={{
            margin: `0 0 ${tokens.spacing.lg}px`,
            color: tokens.color.textPrimary,
            fontSize: 28,
            fontWeight: 700,
          }}
        >
          Register
        </h1>
        <form
          onSubmit={(e) => {
            void handleSubmit(e);
          }}
        >
          <div style={fieldStyle}>
            <label htmlFor="email" style={labelStyle}>
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={inputStyle}
              autoComplete="email"
            />
          </div>
          <div style={fieldStyle}>
            <label htmlFor="password" style={labelStyle}>
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={inputStyle}
              autoComplete="new-password"
            />
          </div>
          {error && (
            <p role="alert" style={{ color: tokens.color.error, margin: `0 0 ${tokens.spacing.md}px`, fontSize: 14 }}>
              {error}
            </p>
          )}
          <Button type="submit" variant="primary" loading={loading} disabled={loading}>
            Register
          </Button>
        </form>
        <p style={{ marginTop: tokens.spacing.lg, textAlign: 'center', color: tokens.color.textSecondary, fontSize: 14 }}>
          Already have an account?{' '}
          <Link to="/login" style={{ color: tokens.color.primary, textDecoration: 'none', fontWeight: 600 }}>
            Log In
          </Link>
        </p>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend && npm test -- --reporter=verbose src/pages/RegisterPage.test.tsx
```

Expected: PASS (5/5)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/RegisterPage.tsx frontend/src/pages/RegisterPage.test.tsx
git commit -m "feat(ui): apply token-based styling to RegisterPage

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 4: ChildProfileSelectPage token-based styling

**Files:**
- Modify: `frontend/src/pages/ChildProfileSelectPage.tsx`
- Modify: `frontend/src/pages/ChildProfileSelectPage.test.tsx`

**Interfaces:**
- Consumes: nothing from other tasks
- Produces: styled ChildProfileSelectPage (no new exports)

- [ ] **Step 1: Write the failing test**

Add one test to the existing `describe('ChildProfileSelectPage')` block in `frontend/src/pages/ChildProfileSelectPage.test.tsx`:

```tsx
it('renders each profile inside a button with the display name', async () => {
  vi.mocked(childProfilesApi.fetchChildProfiles).mockResolvedValue([
    { id: 'p1', account_id: 'acc-1', display_name: 'Alice', created_at: '2026-01-01T00:00:00Z' },
  ]);
  render(
    <MemoryRouter>
      <ChildProfileSelectPage />
    </MemoryRouter>,
  );
  const btn = await screen.findByRole('button', { name: /alice/i });
  expect(btn).toBeInTheDocument();
});
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd frontend && npm test -- --reporter=verbose src/pages/ChildProfileSelectPage.test.tsx
```

Expected: FAIL — no button with name /alice/i (current renders an `<li><button>` but the existing test finds it by text not role, so this may actually pass — read the failure message carefully; if it already passes, replace with:)

```tsx
it('renders page heading "Who\'s Playing?"', async () => {
  vi.mocked(childProfilesApi.fetchChildProfiles).mockResolvedValue([]);
  render(
    <MemoryRouter>
      <ChildProfileSelectPage />
    </MemoryRouter>,
  );
  expect(await screen.findByRole('heading', { name: /who's playing/i })).toBeInTheDocument();
});
```

Run again and confirm FAIL if the heading is not in a semantic `<h1>` today, or pick the test that does fail.

- [ ] **Step 3: Restyle ChildProfileSelectPage**

Replace the full contents of `frontend/src/pages/ChildProfileSelectPage.tsx` with:

```tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../infrastructure/auth/AuthContext';
import { createChildProfile, fetchChildProfiles } from '../infrastructure/auth/childProfilesApi';
import type { ChildProfile } from '../infrastructure/auth/types';
import { Button } from '../shared/components/Button';
import { LoadingSpinner } from '../shared/components/LoadingSpinner';
import tokens from '../shared/tokens';

const pageStyle: React.CSSProperties = {
  minHeight: '100vh',
  background: tokens.color.background,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: tokens.spacing.lg,
};

const cardStyle: React.CSSProperties = {
  background: tokens.color.surface,
  borderRadius: tokens.radius.lg,
  padding: tokens.spacing.xl,
  boxShadow: tokens.shadow.card,
  width: '100%',
  maxWidth: 560,
};

const profileButtonStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: tokens.spacing.sm,
  padding: tokens.spacing.md,
  background: tokens.color.surface,
  border: `1px solid ${tokens.color.border}`,
  borderRadius: tokens.radius.md,
  cursor: 'pointer',
  width: '100%',
  transition: `box-shadow ${tokens.animation.quick}`,
};

const avatarCircleStyle: React.CSSProperties = {
  width: 48,
  height: 48,
  borderRadius: '50%',
  background: tokens.color.border,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: 20,
};

const inputStyle: React.CSSProperties = {
  flex: 1,
  padding: tokens.spacing.sm,
  border: `1px solid ${tokens.color.border}`,
  borderRadius: tokens.radius.sm,
  fontSize: 16,
  color: tokens.color.textPrimary,
  background: tokens.color.surface,
};

export default function ChildProfileSelectPage() {
  const { selectChild } = useAuth();
  const navigate = useNavigate();
  const [profiles, setProfiles] = useState<ChildProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newName, setNewName] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchChildProfiles()
      .then(setProfiles)
      .catch(() => setError('Could not load profiles.'))
      .finally(() => setLoading(false));
  }, []);

  const handleSelect = (profile: ChildProfile) => {
    selectChild(profile.id);
    void navigate('/', { replace: true });
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    setCreating(true);
    try {
      const created = await createChildProfile(newName.trim());
      setProfiles((prev) => [...prev, created]);
      setNewName('');
    } catch {
      setError('Could not create profile.');
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading profiles…" />;
  if (error) return <p role="alert">{error}</p>;

  return (
    <div style={pageStyle}>
      <div style={cardStyle}>
        <h1
          style={{
            margin: `0 0 ${tokens.spacing.xl}px`,
            color: tokens.color.textPrimary,
            textAlign: 'center',
            fontSize: 28,
            fontWeight: 700,
          }}
        >
          Who&apos;s Playing?
        </h1>

        {profiles.length === 0 ? (
          <p style={{ color: tokens.color.textSecondary, textAlign: 'center', margin: `0 0 ${tokens.spacing.xl}px` }}>
            No profiles yet — add one below.
          </p>
        ) : (
          <div
            data-testid="profile-list"
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))',
              gap: tokens.spacing.md,
              marginBottom: tokens.spacing.xl,
            }}
          >
            {profiles.map((p) => (
              <button
                key={p.id}
                type="button"
                style={profileButtonStyle}
                onClick={() => handleSelect(p)}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.boxShadow = tokens.shadow.cardHover;
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.boxShadow = 'none';
                }}
              >
                <div style={avatarCircleStyle} aria-hidden="true">
                  {p.display_name.charAt(0).toUpperCase()}
                </div>
                <span style={{ fontWeight: 600, color: tokens.color.textPrimary, fontSize: 14 }}>
                  {p.display_name}
                </span>
              </button>
            ))}
          </div>
        )}

        {profiles.length < 5 && (
          <div
            style={{
              borderTop: `1px solid ${tokens.color.border}`,
              paddingTop: tokens.spacing.lg,
            }}
          >
            <p style={{ color: tokens.color.textSecondary, fontSize: 14, marginBottom: tokens.spacing.sm }}>
              Add a profile
            </p>
            <form
              onSubmit={(e) => {
                void handleCreate(e);
              }}
              style={{ display: 'flex', gap: tokens.spacing.sm, alignItems: 'center' }}
            >
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Profile name"
                maxLength={50}
                aria-label="New profile name"
                style={inputStyle}
              />
              <Button type="submit" variant="primary" disabled={creating || !newName.trim()}>
                Add
              </Button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd frontend && npm test -- --reporter=verbose src/pages/ChildProfileSelectPage.test.tsx
```

Expected: PASS (all tests including the new one)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/ChildProfileSelectPage.tsx \
        frontend/src/pages/ChildProfileSelectPage.test.tsx
git commit -m "feat(ui): apply token-based styling to ChildProfileSelectPage

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 5: useAvatarGallery mutation functions

**Files:**
- Modify: `frontend/src/features/avatar/useAvatarGallery.ts`
- Modify: `frontend/src/features/avatar/useAvatarGallery.test.ts`

**Interfaces:**
- Consumes: `patchAvatar`, `regeneratePortrait`, `deleteAvatar` from `../../engine/avatar/avatarApi`
- Produces:
  ```ts
  // Added to the hook's return value:
  mutationError: string | null
  clearMutationError: () => void
  toggleFavourite: (avatarId: string, isFavourite: boolean) => Promise<void>
  renameAvatar:    (avatarId: string, name: string) => Promise<void>
  startRegenerate: (avatarId: string) => Promise<void>
  removeAvatar:    (avatarId: string) => Promise<void>
  ```

- [ ] **Step 1: Write the failing tests**

Add the following tests to the existing `describe('useAvatarGallery')` block in `frontend/src/features/avatar/useAvatarGallery.test.ts`:

```ts
// Add these imports at the top of the existing file (merge with existing imports):
// import * as avatarApiModule from '../../engine/avatar/avatarApi';
// (already present — just add the new API functions to the mock awareness)

describe('useAvatarGallery mutations', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([published]);
  });
  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  it('toggleFavourite optimistically flips is_favourite then calls patchAvatar', async () => {
    vi.mocked(avatarApiModule.patchAvatar).mockResolvedValue({ ...published, is_favourite: true } as never);
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));

    act(() => {
      void result.current.toggleFavourite('a1', true);
    });

    expect(result.current.avatars[0].is_favourite).toBe(true);
    expect(avatarApiModule.patchAvatar).toHaveBeenCalledWith('a1', { is_favourite: true });
  });

  it('toggleFavourite reverts on API error', async () => {
    vi.mocked(avatarApiModule.patchAvatar).mockRejectedValue(new Error('fail'));
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.toggleFavourite('a1', true);
    });

    expect(result.current.avatars[0].is_favourite).toBe(false);
    expect(result.current.mutationError).toBeTruthy();
  });

  it('renameAvatar optimistically updates name then calls patchAvatar', async () => {
    vi.mocked(avatarApiModule.patchAvatar).mockResolvedValue({ ...published, name: 'Renamed' } as never);
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));

    act(() => {
      void result.current.renameAvatar('a1', 'Renamed');
    });

    expect(result.current.avatars[0].name).toBe('Renamed');
    expect(avatarApiModule.patchAvatar).toHaveBeenCalledWith('a1', { name: 'Renamed' });
  });

  it('renameAvatar reverts on API error', async () => {
    vi.mocked(avatarApiModule.patchAvatar).mockRejectedValue(new Error('fail'));
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.renameAvatar('a1', 'Renamed');
    });

    expect(result.current.avatars[0].name).toBe('Foxy');
    expect(result.current.mutationError).toBeTruthy();
  });

  it('removeAvatar optimistically removes avatar then calls deleteAvatar', async () => {
    vi.mocked(avatarApiModule.deleteAvatar).mockResolvedValue(undefined);
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.removeAvatar('a1');
    });

    expect(result.current.avatars).toHaveLength(0);
    expect(avatarApiModule.deleteAvatar).toHaveBeenCalledWith('a1');
  });

  it('removeAvatar restores item at original index on API error (Review Focus #3)', async () => {
    const second: AvatarListItem = { ...published, avatar_id: 'a2', name: 'Bear', species: 'bear' };
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([published, second]);
    vi.mocked(avatarApiModule.deleteAvatar).mockRejectedValue(new Error('fail'));
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));

    await act(async () => {
      await result.current.removeAvatar('a1');
    });

    expect(result.current.avatars[0].avatar_id).toBe('a1');
    expect(result.current.mutationError).toBeTruthy();
  });

  it('clearMutationError clears the error string', async () => {
    vi.mocked(avatarApiModule.patchAvatar).mockRejectedValue(new Error('fail'));
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));
    await act(async () => { await result.current.toggleFavourite('a1', true); });
    expect(result.current.mutationError).toBeTruthy();

    act(() => { result.current.clearMutationError(); });

    expect(result.current.mutationError).toBeNull();
  });

  it('startRegenerate sets avatar to pending and calls regeneratePortrait', async () => {
    vi.mocked(avatarApiModule.regeneratePortrait).mockResolvedValue({
      avatar_id: 'a1', job_id: 'j1', status: 'queued',
    });
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([published]);
    const { result } = renderHook(() => useAvatarGallery());
    await waitFor(() => expect(result.current.loading).toBe(false));

    act(() => { void result.current.startRegenerate('a1'); });

    expect(result.current.avatars[0].status).toBe('pending');
    expect(avatarApiModule.regeneratePortrait).toHaveBeenCalledWith('a1');
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd frontend && npm test -- --reporter=verbose src/features/avatar/useAvatarGallery.test.ts
```

Expected: FAIL — `toggleFavourite`, `renameAvatar`, etc. are not defined on hook result

- [ ] **Step 3: Implement the mutations**

Replace the full contents of `frontend/src/features/avatar/useAvatarGallery.ts` with:

```ts
import { useCallback, useEffect, useRef, useState } from 'react';
import {
  deleteAvatar,
  listAvatars,
  patchAvatar,
  regeneratePortrait,
} from '../../engine/avatar/avatarApi';
import type { AvatarListItem, AvatarStatus } from '../../engine/avatar/types';

export function useAvatarGallery() {
  const [avatars, setAvatars] = useState<AvatarListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [mutationError, setMutationError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchAvatars = useCallback(async (fromPoll = false) => {
    try {
      const data = await listAvatars();
      setAvatars(data);
      if (!fromPoll) setLoading(false);

      const hasPending = data.some((a) => a.status === 'pending');
      if (hasPending && !intervalRef.current) {
        intervalRef.current = setInterval(() => {
          void fetchAvatars(true);
        }, 3000);
      } else if (!hasPending && intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
        if (fromPoll) setLoading(false);
      }
    } catch {
      setError('Looks like we lost the signal. Check your connection!');
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchAvatars();
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [fetchAvatars]);

  const clearMutationError = useCallback(() => setMutationError(null), []);

  const toggleFavourite = useCallback(async (avatarId: string, isFavourite: boolean) => {
    setAvatars((list) =>
      list.map((a) => (a.avatar_id === avatarId ? { ...a, is_favourite: isFavourite } : a)),
    );
    try {
      await patchAvatar(avatarId, { is_favourite: isFavourite });
      setMutationError(null);
    } catch {
      setAvatars((list) =>
        list.map((a) => (a.avatar_id === avatarId ? { ...a, is_favourite: !isFavourite } : a)),
      );
      setMutationError('Could not update favourite. Try again.');
    }
  }, []);

  const renameAvatar = useCallback(async (avatarId: string, name: string) => {
    let previousName: string | null = null;
    setAvatars((list) => {
      previousName = list.find((a) => a.avatar_id === avatarId)?.name ?? null;
      return list.map((a) => (a.avatar_id === avatarId ? { ...a, name } : a));
    });
    try {
      await patchAvatar(avatarId, { name });
      setMutationError(null);
    } catch {
      setAvatars((list) =>
        list.map((a) => (a.avatar_id === avatarId ? { ...a, name: previousName } : a)),
      );
      setMutationError('Could not rename avatar. Try again.');
    }
  }, []);

  const startRegenerate = useCallback(
    async (avatarId: string) => {
      let previousStatus: AvatarStatus = 'published';
      setAvatars((list) => {
        previousStatus = list.find((a) => a.avatar_id === avatarId)?.status ?? 'published';
        return list.map((a) => (a.avatar_id === avatarId ? { ...a, status: 'pending' as AvatarStatus } : a));
      });
      try {
        await regeneratePortrait(avatarId);
        setMutationError(null);
        void fetchAvatars(true);
      } catch {
        setAvatars((list) =>
          list.map((a) => (a.avatar_id === avatarId ? { ...a, status: previousStatus } : a)),
        );
        setMutationError('Could not regenerate portrait. Try again.');
      }
    },
    [fetchAvatars],
  );

  const removeAvatar = useCallback(async (avatarId: string) => {
    let removedItem: AvatarListItem | undefined;
    let removedIndex = -1;
    setAvatars((list) => {
      removedIndex = list.findIndex((a) => a.avatar_id === avatarId);
      removedItem = list[removedIndex];
      return list.filter((a) => a.avatar_id !== avatarId);
    });
    try {
      await deleteAvatar(avatarId);
      setMutationError(null);
    } catch {
      setAvatars((list) => {
        if (removedItem === undefined || removedIndex === -1) return list;
        const next = [...list];
        next.splice(removedIndex, 0, removedItem);
        return next;
      });
      setMutationError('Could not delete avatar. Try again.');
    }
  }, []);

  return {
    avatars,
    loading,
    error,
    mutationError,
    clearMutationError,
    toggleFavourite,
    renameAvatar,
    startRegenerate,
    removeAvatar,
  };
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd frontend && npm test -- --reporter=verbose src/features/avatar/useAvatarGallery.test.ts
```

Expected: PASS (all existing + all new tests)

- [ ] **Step 5: Run full suite**

```bash
cd frontend && npm test
```

Expected: all tests pass (AvatarGalleryPage.test.tsx still passes because it only uses `avatars`/`loading`/`error` — the new fields are additive)

- [ ] **Step 6: Commit**

```bash
git add frontend/src/features/avatar/useAvatarGallery.ts \
        frontend/src/features/avatar/useAvatarGallery.test.ts
git commit -m "feat(gallery): add mutation functions to useAvatarGallery hook

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 6: AvatarCard favourite star + manage menu

**Files:**
- Modify: `frontend/src/features/avatar/AvatarCard.tsx`
- Modify: `frontend/src/features/avatar/AvatarCard.test.tsx`

**Interfaces:**
- Consumes: `ConfirmDialog` from `../../shared/components/ConfirmDialog`
- Produces: Updated `AvatarCardProps` with optional callbacks:
  ```ts
  onFavourite?: (avatarId: string, isFavourite: boolean) => void;
  onRename?:    (avatarId: string, name: string) => void;
  onRegenerate?:(avatarId: string) => void;
  onDelete?:    (avatarId: string) => void;
  ```

- [ ] **Step 1: Write the failing tests**

Add the following tests to the existing `describe('AvatarCard')` block in `frontend/src/features/avatar/AvatarCard.test.tsx`:

```tsx
// Add this import at the top if not present:
// import { act } from '@testing-library/react';

describe('AvatarCard — favourite', () => {
  it('renders favourite star when onFavourite is provided', () => {
    render(<AvatarCard avatar={published} onFavourite={vi.fn()} />);
    expect(screen.getByRole('button', { name: /add to favourites/i })).toBeInTheDocument();
  });

  it('shows filled star when is_favourite is true', () => {
    render(<AvatarCard avatar={{ ...published, is_favourite: true }} onFavourite={vi.fn()} />);
    expect(screen.getByRole('button', { name: /remove from favourites/i })).toBeInTheDocument();
  });

  it('calls onFavourite with flipped value on star click', async () => {
    const onFavourite = vi.fn();
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onFavourite={onFavourite} />);
    await user.click(screen.getByRole('button', { name: /add to favourites/i }));
    expect(onFavourite).toHaveBeenCalledWith('a1', true);
  });

  it('does not render favourite star when onFavourite is absent', () => {
    render(<AvatarCard avatar={published} />);
    expect(screen.queryByRole('button', { name: /favourites/i })).toBeNull();
  });
});

describe('AvatarCard — manage menu', () => {
  it('renders manage button when any manage callback is provided', () => {
    render(<AvatarCard avatar={published} onDelete={vi.fn()} />);
    expect(screen.getByRole('button', { name: /manage avatar/i })).toBeInTheDocument();
  });

  it('clicking manage button shows rename/regenerate/delete actions', async () => {
    const user = userEvent.setup();
    render(
      <AvatarCard avatar={published} onRename={vi.fn()} onRegenerate={vi.fn()} onDelete={vi.fn()} />,
    );
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    expect(screen.getByRole('menuitem', { name: /rename/i })).toBeInTheDocument();
    expect(screen.getByRole('menuitem', { name: /regenerate/i })).toBeInTheDocument();
    expect(screen.getByRole('menuitem', { name: /delete/i })).toBeInTheDocument();
  });

  it('clicking Rename enters inline edit mode', async () => {
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onRename={vi.fn()} />);
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    await user.click(screen.getByRole('menuitem', { name: /rename/i }));
    expect(screen.getByRole('textbox', { name: /rename avatar/i })).toBeInTheDocument();
  });

  it('Save button is disabled when rename input is empty (Review Focus #2)', async () => {
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onRename={vi.fn()} />);
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    await user.click(screen.getByRole('menuitem', { name: /rename/i }));
    const input = screen.getByRole('textbox', { name: /rename avatar/i });
    await user.clear(input);
    expect(screen.getByRole('button', { name: /save/i })).toBeDisabled();
  });

  it('long name trimmed before onRename call (Review Focus #5)', async () => {
    const onRename = vi.fn();
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onRename={onRename} />);
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    await user.click(screen.getByRole('menuitem', { name: /rename/i }));
    const input = screen.getByRole('textbox', { name: /rename avatar/i });
    await user.clear(input);
    await user.type(input, '  Padded  ');
    await user.click(screen.getByRole('button', { name: /save/i }));
    expect(onRename).toHaveBeenCalledWith('a1', 'Padded');
  });

  it('Escape cancels rename without calling onRename', async () => {
    const onRename = vi.fn();
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onRename={onRename} />);
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    await user.click(screen.getByRole('menuitem', { name: /rename/i }));
    const input = screen.getByRole('textbox', { name: /rename avatar/i });
    await user.clear(input);
    await user.type(input, 'NewName');
    await user.keyboard('{Escape}');
    expect(onRename).not.toHaveBeenCalled();
    expect(screen.queryByRole('textbox')).toBeNull();
  });

  it('clicking Delete opens ConfirmDialog', async () => {
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onDelete={vi.fn()} />);
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    await user.click(screen.getByRole('menuitem', { name: /delete/i }));
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('confirming delete calls onDelete with avatar_id', async () => {
    const onDelete = vi.fn();
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onDelete={onDelete} />);
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    await user.click(screen.getByRole('menuitem', { name: /delete/i }));
    await user.click(screen.getByRole('button', { name: /delete/i }));
    expect(onDelete).toHaveBeenCalledWith('a1');
  });

  it('clicking Regenerate calls onRegenerate with avatar_id', async () => {
    const onRegenerate = vi.fn();
    const user = userEvent.setup();
    render(<AvatarCard avatar={published} onRegenerate={onRegenerate} />);
    await user.click(screen.getByRole('button', { name: /manage avatar/i }));
    await user.click(screen.getByRole('menuitem', { name: /regenerate/i }));
    expect(onRegenerate).toHaveBeenCalledWith('a1');
  });
});
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd frontend && npm test -- --reporter=verbose src/features/avatar/AvatarCard.test.tsx
```

Expected: FAIL — new buttons and manage menu do not exist yet

- [ ] **Step 3: Implement the new AvatarCard**

Replace the full contents of `frontend/src/features/avatar/AvatarCard.tsx` with:

```tsx
import { useState } from 'react';
import type { AvatarListItem } from '../../engine/avatar/types';
import { Button } from '../../shared/components/Button';
import { ConfirmDialog } from '../../shared/components/ConfirmDialog';
import tokens from '../../shared/tokens';

interface AvatarCardProps {
  avatar: AvatarListItem;
  selected?: boolean;
  onSelect?: (avatarId: string) => void;
  onFavourite?: (avatarId: string, isFavourite: boolean) => void;
  onRename?: (avatarId: string, name: string) => void;
  onRegenerate?: (avatarId: string) => void;
  onDelete?: (avatarId: string) => void;
}

const menuItemBase: React.CSSProperties = {
  background: 'transparent',
  border: 'none',
  cursor: 'pointer',
  padding: `${tokens.spacing.xs}px ${tokens.spacing.sm}px`,
  textAlign: 'left',
  borderRadius: tokens.radius.sm,
  fontSize: 14,
  width: '100%',
  color: tokens.color.textPrimary,
};

export function AvatarCard({
  avatar,
  selected = false,
  onSelect,
  onFavourite,
  onRename,
  onRegenerate,
  onDelete,
}: AvatarCardProps) {
  const isPending = avatar.status === 'pending';
  const isFailed = avatar.status === 'failed';
  const rawName = avatar.name ?? avatar.species;
  const displayName = rawName.length > 24 ? rawName.slice(0, 24) + '…' : rawName;

  const [showManage, setShowManage] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState(rawName);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const hasManage = !!(onRename || onRegenerate || onDelete);

  const cardStyle: React.CSSProperties = {
    position: 'relative',
    background: tokens.color.surface,
    borderRadius: tokens.radius.lg,
    padding: tokens.spacing.md,
    boxShadow: selected ? `0 0 0 3px ${tokens.color.primary}` : tokens.shadow.card,
    cursor: onSelect ? 'pointer' : 'default',
    border: 'none',
    textAlign: 'left',
    width: '100%',
    transition: `box-shadow ${tokens.animation.quick}`,
  };

  const nameRow = isEditing ? (
    <div style={{ display: 'flex', gap: tokens.spacing.xs, alignItems: 'center', marginTop: tokens.spacing.xs }}>
      <input
        autoFocus
        value={editName}
        onChange={(e) => setEditName(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && editName.trim()) {
            onRename?.(avatar.avatar_id, editName.trim());
            setIsEditing(false);
          }
          if (e.key === 'Escape') {
            setEditName(rawName);
            setIsEditing(false);
          }
        }}
        aria-label="Rename avatar"
        style={{
          flex: 1,
          padding: tokens.spacing.xs,
          border: `1px solid ${tokens.color.border}`,
          borderRadius: tokens.radius.sm,
          fontSize: 14,
          color: tokens.color.textPrimary,
        }}
      />
      <Button
        variant="primary"
        disabled={!editName.trim()}
        onClick={() => {
          if (!editName.trim()) return;
          onRename?.(avatar.avatar_id, editName.trim());
          setIsEditing(false);
        }}
      >
        Save
      </Button>
    </div>
  ) : (
    <div
      title={rawName}
      style={{ fontWeight: 600, color: tokens.color.textPrimary, overflow: 'hidden', whiteSpace: 'nowrap' }}
    >
      {displayName}
    </div>
  );

  const content = (
    <>
      {onFavourite && (
        <button
          type="button"
          aria-label={avatar.is_favourite ? 'Remove from favourites' : 'Add to favourites'}
          style={{
            position: 'absolute',
            top: tokens.spacing.xs,
            right: tokens.spacing.xs,
            width: tokens.touchTarget,
            height: tokens.touchTarget,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'transparent',
            border: 'none',
            cursor: 'pointer',
            fontSize: 20,
            color: avatar.is_favourite ? tokens.color.warning : tokens.color.textSecondary,
            zIndex: 1,
          }}
          onClick={(e) => {
            e.stopPropagation();
            onFavourite(avatar.avatar_id, !avatar.is_favourite);
          }}
        >
          {avatar.is_favourite ? '★' : '☆'}
        </button>
      )}

      {isPending ? (
        <div
          style={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            background: tokens.color.border,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: tokens.spacing.sm,
          }}
        >
          <span aria-hidden="true" style={{ fontSize: 24 }}>⏳</span>
        </div>
      ) : (
        <img
          src={avatar.portrait?.small_url}
          alt={rawName}
          style={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            objectFit: 'cover',
            marginBottom: tokens.spacing.sm,
          }}
        />
      )}

      {nameRow}

      <div style={{ fontSize: 14, color: tokens.color.textSecondary, textTransform: 'capitalize' }}>
        {avatar.species}
      </div>

      {isPending && (
        <div style={{ fontSize: 12, color: tokens.color.primary, marginTop: tokens.spacing.xs }}>
          Generating…
        </div>
      )}
      {isFailed && (
        <div style={{ fontSize: 12, color: tokens.color.error, marginTop: tokens.spacing.xs }}>
          Hmm, something went wobbly.
        </div>
      )}

      {hasManage && !isEditing && (
        <button
          type="button"
          aria-label="Manage avatar"
          style={{
            position: 'absolute',
            bottom: tokens.spacing.xs,
            right: tokens.spacing.xs,
            width: tokens.touchTarget,
            height: tokens.touchTarget,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'transparent',
            border: 'none',
            cursor: 'pointer',
            fontSize: 18,
            color: tokens.color.textSecondary,
          }}
          onClick={(e) => {
            e.stopPropagation();
            setShowManage((v) => !v);
          }}
        >
          ⋯
        </button>
      )}

      {showManage && (
        <div
          role="menu"
          style={{
            position: 'absolute',
            bottom: tokens.spacing.xl + tokens.spacing.sm,
            right: tokens.spacing.xs,
            background: tokens.color.surface,
            borderRadius: tokens.radius.md,
            boxShadow: tokens.shadow.overlay,
            padding: tokens.spacing.sm,
            zIndex: 10,
            display: 'flex',
            flexDirection: 'column',
            gap: tokens.spacing.xs,
            minWidth: 120,
          }}
        >
          {onRename && (
            <button
              type="button"
              role="menuitem"
              style={menuItemBase}
              onClick={() => { setIsEditing(true); setShowManage(false); }}
            >
              Rename
            </button>
          )}
          {onRegenerate && (
            <button
              type="button"
              role="menuitem"
              style={menuItemBase}
              onClick={() => { onRegenerate(avatar.avatar_id); setShowManage(false); }}
            >
              Regenerate
            </button>
          )}
          {onDelete && (
            <button
              type="button"
              role="menuitem"
              style={{ ...menuItemBase, color: tokens.color.error }}
              onClick={() => { setShowDeleteConfirm(true); setShowManage(false); }}
            >
              Delete
            </button>
          )}
        </div>
      )}

      <ConfirmDialog
        open={showDeleteConfirm}
        title="Delete avatar?"
        message="This cannot be undone."
        confirmLabel="Delete"
        onConfirm={() => { onDelete?.(avatar.avatar_id); setShowDeleteConfirm(false); }}
        onClose={() => setShowDeleteConfirm(false)}
      />
    </>
  );

  if (onSelect) {
    return (
      <button
        type="button"
        style={cardStyle}
        aria-pressed={selected}
        onClick={() => onSelect(avatar.avatar_id)}
        onFocus={(e) => {
          (e.currentTarget as HTMLElement).style.outline = `2px solid ${tokens.color.focus}`;
          (e.currentTarget as HTMLElement).style.outlineOffset = '2px';
        }}
        onBlur={(e) => {
          (e.currentTarget as HTMLElement).style.outline = 'none';
        }}
      >
        {content}
      </button>
    );
  }

  return <div style={cardStyle}>{content}</div>;
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd frontend && npm test -- --reporter=verbose src/features/avatar/AvatarCard.test.tsx
```

Expected: PASS (all existing + all new tests)

- [ ] **Step 5: Run full suite**

```bash
cd frontend && npm test
```

Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
git add frontend/src/features/avatar/AvatarCard.tsx \
        frontend/src/features/avatar/AvatarCard.test.tsx
git commit -m "feat(gallery): add favourite star and manage menu to AvatarCard

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

### Task 7: AvatarGalleryPage wiring + mutation error banner

**Files:**
- Modify: `frontend/src/pages/AvatarGalleryPage.tsx`
- Modify: `frontend/src/pages/AvatarGalleryPage.test.tsx`

**Interfaces:**
- Consumes (from Task 5): `mutationError`, `clearMutationError`, `toggleFavourite`, `renameAvatar`, `startRegenerate`, `removeAvatar` from `useAvatarGallery`
- Consumes (from Task 6): `AvatarCard` props `onFavourite`, `onRename`, `onRegenerate`, `onDelete`
- Produces: nothing new exported

- [ ] **Step 1: Write the failing tests**

Add the following tests to the existing `describe('AvatarGalleryPage')` block in `frontend/src/pages/AvatarGalleryPage.test.tsx`.

First, add a mock for `useAvatarGallery` to the top of the file (the existing file mocks `avatarApi` module-level, which is still needed for the hook; add a direct hook mock for the new tests):

```tsx
// Add after the existing vi.mock('../../engine/avatar/avatarApi') line — used only for the new mutation tests:
const { mockToggleFavourite, mockClearMutationError } = vi.hoisted(() => ({
  mockToggleFavourite: vi.fn(),
  mockClearMutationError: vi.fn(),
}));
```

Then add the tests:

```tsx
describe('AvatarGalleryPage — mutations', () => {
  it('shows mutation error banner when mutationError is set', async () => {
    // Use the real hook but stub the API to return an avatar, then trigger a mutation error
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([published]);
    vi.mocked(avatarApiModule.patchAvatar).mockRejectedValue(new Error('fail'));
    render(
      <MemoryRouter>
        <AvatarGalleryPage />
      </MemoryRouter>,
    );
    // Favourite the avatar to trigger the error
    const starBtn = await screen.findByRole('button', { name: /add to favourites/i });
    await userEvent.setup().click(starBtn);
    expect(await screen.findByRole('alert', { name: /mutation error/i })).toBeInTheDocument();
  });

  it('mutation error banner has a close button (Review Focus #4)', async () => {
    vi.mocked(avatarApiModule.listAvatars).mockResolvedValue([published]);
    vi.mocked(avatarApiModule.patchAvatar).mockRejectedValue(new Error('fail'));
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <AvatarGalleryPage />
      </MemoryRouter>,
    );
    await user.click(await screen.findByRole('button', { name: /add to favourites/i }));
    const banner = await screen.findByRole('alert', { name: /mutation error/i });
    const closeBtn = within(banner).getByRole('button', { name: /dismiss/i });
    await user.click(closeBtn);
    expect(screen.queryByRole('alert', { name: /mutation error/i })).toBeNull();
  });
});
```

Also add `import { within } from '@testing-library/react';` and `import userEvent from '@testing-library/user-event';` to the imports if not already present.

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd frontend && npm test -- --reporter=verbose src/pages/AvatarGalleryPage.test.tsx
```

Expected: FAIL — no mutation error banner

- [ ] **Step 3: Wire mutations and error banner into AvatarGalleryPage**

Replace the full contents of `frontend/src/pages/AvatarGalleryPage.tsx` with:

```tsx
import { Link } from 'react-router-dom';
import { AvatarCard } from '../features/avatar/AvatarCard';
import { useAvatarGallery } from '../features/avatar/useAvatarGallery';
import { LoadingSpinner } from '../shared/components/LoadingSpinner';
import tokens from '../shared/tokens';

export default function AvatarGalleryPage() {
  const {
    avatars,
    loading,
    error,
    mutationError,
    clearMutationError,
    toggleFavourite,
    renameAvatar,
    startRegenerate,
    removeAvatar,
  } = useAvatarGallery();

  if (loading)
    return (
      <div data-testid="page-avatar-gallery">
        <LoadingSpinner />
      </div>
    );

  if (error) {
    return (
      <div
        role="alert"
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: tokens.spacing.md,
          padding: tokens.spacing.xl,
          textAlign: 'center',
          color: tokens.color.textPrimary,
        }}
      >
        <span style={{ fontSize: 32 }} aria-hidden="true">😕</span>
        <p style={{ margin: 0 }}>{error}</p>
      </div>
    );
  }

  if (avatars.length === 0) {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: tokens.spacing.lg,
          padding: tokens.spacing.xl,
        }}
      >
        <h1 style={{ color: tokens.color.textPrimary }}>Your Avatars</h1>
        <p style={{ color: tokens.color.textSecondary }}>
          You don&apos;t have any avatars yet. Create your first one!
        </p>
        <Link
          to="/avatars/new"
          style={{
            padding: `${tokens.spacing.sm}px ${tokens.spacing.lg}px`,
            background: tokens.color.primary,
            color: '#fff',
            borderRadius: tokens.radius.md,
            textDecoration: 'none',
            fontWeight: 600,
          }}
        >
          Create Your First Avatar
        </Link>
      </div>
    );
  }

  return (
    <div style={{ padding: tokens.spacing.xl }}>
      {mutationError && (
        <div
          role="alert"
          aria-label="mutation error"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: tokens.spacing.md,
            padding: `${tokens.spacing.sm}px ${tokens.spacing.md}px`,
            background: '#FEF2F2',
            border: `1px solid ${tokens.color.error}`,
            borderRadius: tokens.radius.md,
            color: tokens.color.error,
            marginBottom: tokens.spacing.md,
            fontSize: 14,
          }}
        >
          <span>{mutationError}</span>
          <button
            type="button"
            aria-label="Dismiss"
            onClick={clearMutationError}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: tokens.color.error,
              fontSize: 18,
              lineHeight: 1,
              padding: tokens.spacing.xs,
            }}
          >
            ×
          </button>
        </div>
      )}

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: tokens.spacing.lg,
        }}
      >
        <h1 style={{ color: tokens.color.textPrimary }}>Your Avatars</h1>
        <Link
          to="/avatars/new"
          style={{
            padding: `${tokens.spacing.sm}px ${tokens.spacing.lg}px`,
            background: tokens.color.primary,
            color: '#fff',
            borderRadius: tokens.radius.md,
            textDecoration: 'none',
            fontWeight: 600,
          }}
        >
          + New Avatar
        </Link>
      </div>

      <div
        role="list"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
          gap: tokens.spacing.md,
        }}
      >
        {avatars.map((avatar) => (
          <div key={avatar.avatar_id} role="listitem">
            <AvatarCard
              avatar={avatar}
              onFavourite={(id, val) => void toggleFavourite(id, val)}
              onRename={(id, name) => void renameAvatar(id, name)}
              onRegenerate={(id) => void startRegenerate(id)}
              onDelete={(id) => void removeAvatar(id)}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd frontend && npm test -- --reporter=verbose src/pages/AvatarGalleryPage.test.tsx
```

Expected: PASS (all existing + all new tests)

- [ ] **Step 5: Run full suite**

```bash
cd frontend && npm test
```

Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/AvatarGalleryPage.tsx \
        frontend/src/pages/AvatarGalleryPage.test.tsx
git commit -m "feat(gallery): wire mutations and error banner into AvatarGalleryPage

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```
