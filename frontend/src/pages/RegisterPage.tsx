import { useState } from 'react';
import { Link } from 'react-router-dom';
import { register } from '../infrastructure/auth/authApi';
import { useLocale } from '../infrastructure/localization/LocaleContext';
import type { TranslationKey } from '../infrastructure/localization/catalogs';
import { getAuthErrorMessage } from '../infrastructure/localization/authErrors';
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
  const { t } = useLocale();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<TranslationKey | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register(email, password);
      setSuccess(true);
    } catch (err) {
      setError(getAuthErrorMessage(err, 'Registration could not be completed. Please try again.'));
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
            {t('Account created. Please wait for an administrator to approve your account.')}
          </p>
          <p
            style={{
              marginTop: tokens.spacing.lg,
              textAlign: 'center',
              color: tokens.color.textSecondary,
              fontSize: 14,
            }}
          >
            <Link
              to="/login"
              style={{ color: tokens.color.primary, textDecoration: 'none', fontWeight: 600 }}
            >
              {t('Log In')}
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
          {t('Register')}
        </h1>
        <form
          onSubmit={(e) => {
            void handleSubmit(e);
          }}
        >
          <div style={fieldStyle}>
            <label htmlFor="email" style={labelStyle}>
              {t('Email')}
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
              {t('Password')}
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
            <p
              role="alert"
              style={{
                color: tokens.color.error,
                margin: `0 0 ${tokens.spacing.md}px`,
                fontSize: 14,
              }}
            >
              {t(error)}
            </p>
          )}
          <Button type="submit" variant="primary" loading={loading} disabled={loading}>
            {t('Register')}
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
          {t('Already have an account?')}{' '}
          <Link
            to="/login"
            style={{ color: tokens.color.primary, textDecoration: 'none', fontWeight: 600 }}
          >
            {t('Log In')}
          </Link>
        </p>
      </div>
    </div>
  );
}
