import { Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from './infrastructure/auth/AuthContext';
import { useLocale } from './infrastructure/localization/LocaleContext';
import OfflineResultSync from './infrastructure/offline/OfflineResultSync';
import { LanguageSwitcher } from './shared/components/LanguageSwitcher';
import tokens from './shared/tokens';

export default function App() {
  const { account, logout } = useAuth();
  const { t } = useLocale();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    await navigate('/login', { replace: true });
  };

  return (
    <div style={{ minHeight: '100vh' }}>
      <header
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 900,
          display: 'flex',
          justifyContent: 'flex-end',
          alignItems: 'center',
          minHeight: 56,
          padding: `0 ${tokens.spacing.md}px`,
          background: tokens.color.surface,
          borderBottom: `1px solid ${tokens.color.border}`,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: tokens.spacing.sm }}>
          {account && (
            <button
              type="button"
              aria-label={t('Log out')}
              onClick={() => {
                void handleLogout();
              }}
              style={{
                minHeight: tokens.touchTarget,
                padding: `0 ${tokens.spacing.md}px`,
                color: tokens.color.textPrimary,
                background: 'transparent',
                border: `1px solid ${tokens.color.border}`,
                borderRadius: tokens.radius.md,
                cursor: 'pointer',
                font: 'inherit',
              }}
            >
              {t('Log out')}
            </button>
          )}
          <LanguageSwitcher />
        </div>
      </header>
      <OfflineResultSync />
      <Outlet />
    </div>
  );
}
