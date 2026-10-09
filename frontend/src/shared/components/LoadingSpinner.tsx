import tokens from '../tokens';

interface LoadingSpinnerProps {
  message?: string;
}

export function LoadingSpinner({ message }: LoadingSpinnerProps) {
  return (
    <div
      role="status"
      aria-label={message ?? 'Loading…'}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: tokens.spacing.md,
        padding: tokens.spacing.xl,
      }}
    >
      <img src="/artwork/loading.png" alt="" aria-hidden="true" style={{ width: 120, height: 'auto' }} />
      {message && <p style={{ color: tokens.color.textSecondary, margin: 0 }}>{message}</p>}
    </div>
  );
}
