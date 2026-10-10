import tokens from '../tokens';
import { useReducedMotion } from '../hooks/useReducedMotion';
import { useLocale } from '../../infrastructure/localization/LocaleContext';

interface XPBarProps {
  current: number;
  max: number;
  level: number;
}

export function XPBar({ current, max, level }: XPBarProps) {
  const reduced = useReducedMotion();
  const { t } = useLocale();
  const pct = `${Math.min(100, Math.round((current / max) * 100))}%`;

  return (
    <div
      role="progressbar"
      aria-valuenow={current}
      aria-valuemin={0}
      aria-valuemax={max}
      aria-label={t('Level {{level}} — {{current}} of {{max}} XP', { level, current, max })}
      style={{
        height: 12,
        borderRadius: 9999,
        background: tokens.color.background,
        overflow: 'hidden',
        border: `1px solid ${tokens.color.border}`,
      }}
    >
      <div
        data-testid="xpbar-fill"
        style={{
          height: '100%',
          width: pct,
          background: tokens.color.primary,
          borderRadius: 9999,
          transition: reduced ? 'none' : `width ${tokens.animation.standard} ease-out`,
        }}
      />
    </div>
  );
}
