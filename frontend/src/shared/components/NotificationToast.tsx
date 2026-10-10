import { useEffect } from 'react';
import tokens from '../tokens';
import { useReducedMotion } from '../hooks/useReducedMotion';
import { useLocale } from '../../infrastructure/localization/LocaleContext';

interface NotificationToastProps {
  message: string;
  type?: 'success' | 'error' | 'info';
  onClose: () => void;
}

const typeColor: Record<NonNullable<NotificationToastProps['type']>, string> = {
  success: tokens.color.success,
  error: tokens.color.error,
  info: tokens.color.primary,
};

export function NotificationToast({ message, type = 'info', onClose }: NotificationToastProps) {
  const reduced = useReducedMotion();
  const { t } = useLocale();

  useEffect(() => {
    const id = setTimeout(onClose, 3000);
    return () => clearTimeout(id);
  }, [onClose]);

  return (
    <div
      role="status"
      aria-live="polite"
      className={reduced ? undefined : 'slideIn'}
      style={{
        position: 'fixed',
        top: tokens.spacing.lg,
        right: tokens.spacing.lg,
        background: tokens.color.surface,
        borderLeft: `4px solid ${typeColor[type]}`,
        borderRadius: tokens.radius.md,
        padding: `${tokens.spacing.sm}px ${tokens.spacing.md}px`,
        boxShadow: tokens.shadow.overlay,
        display: 'flex',
        alignItems: 'center',
        gap: tokens.spacing.sm,
        zIndex: 1100,
        animation: reduced ? 'none' : `slideIn ${tokens.animation.standard} ease-out`,
        minWidth: 240,
        maxWidth: 360,
      }}
    >
      <span style={{ flex: 1, color: tokens.color.textPrimary }}>{message}</span>
      <button
        type="button"
        aria-label={t('Dismiss notification')}
        onClick={onClose}
        style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          color: tokens.color.textSecondary,
          fontSize: 18,
          padding: tokens.spacing.xs,
          minHeight: tokens.touchTarget,
          minWidth: tokens.touchTarget,
        }}
      >
        ✕
      </button>
    </div>
  );
}
