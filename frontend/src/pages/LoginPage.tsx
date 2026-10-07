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
            <p
              role="alert"
              style={{
                color: tokens.color.error,
                margin: `0 0 ${tokens.spacing.md}px`,
                fontSize: 14,
              }}
            >
              {error}
            </p>
          )}
          <Button type="submit" variant="primary" loading={loading} disabled={loading}>
            Log In
          </Button>
        </form>
        <p
          style={{
            marginTop: tokens.spacing.lg,
            textAlign: 'center',
            color: tokens.color.textSecondary,
            fontSize: 14,
          }}
        >
          Don&apos;t have an account?{' '}
          <Link
            to="/register"
            style={{ color: tokens.color.primary, textDecoration: 'none', fontWeight: 600 }}
          >
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
