import { Outlet } from 'react-router-dom';
import OfflineResultSync from './infrastructure/offline/OfflineResultSync';
import { LanguageSwitcher } from './shared/components/LanguageSwitcher';
import tokens from './shared/tokens';

export default function App() {
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
        <LanguageSwitcher />
      </header>
      <OfflineResultSync />
      <Outlet />
    </div>
  );
}
