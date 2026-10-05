import tokens from '../tokens';
import { useReducedMotion } from '../hooks/useReducedMotion';

interface LoadingSpinnerProps {
  message?: string;
  size?: number;
}

export function LoadingSpinner({ message, size = 40 }: LoadingSpinnerProps) {
  const reduced = useReducedMotion();

  return (
    <div
      role="status"
      aria-label={message ?? 'Loading…'}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: tokens.spacing.sm,
      }}
    >
      <div
        className={reduced ? 'pulse' : 'spin'}
        style={{
          width: size,
          height: size,
          borderRadius: '50%',
          border: `4px solid ${tokens.color.border}`,
          borderTopColor: tokens.color.primary,
          animation: reduced ? `pulse 1s ease-in-out infinite` : `spin 0.8s linear infinite`,
        }}
        aria-hidden="true"
      />
      {message && (
        <span style={{ color: tokens.color.textSecondary, fontSize: 14 }}>{message}</span>
      )}
    </div>
  );
}
