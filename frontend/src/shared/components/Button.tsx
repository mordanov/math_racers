import tokens from '../tokens';

interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  type?: 'button' | 'submit' | 'reset';
  'aria-label'?: string;
}

const variantStyles: Record<ButtonProps['variant'], React.CSSProperties> = {
  primary: {
    background: tokens.color.primary,
    color: tokens.color.textOnPrimary,
    border: 'none',
  },
  secondary: {
    background: 'transparent',
    color: tokens.color.primary,
    border: `2px solid ${tokens.color.primary}`,
  },
  ghost: {
    background: 'transparent',
    color: tokens.color.textPrimary,
    border: 'none',
  },
};

export function Button({
  variant,
  children,
  onClick,
  disabled = false,
  loading = false,
  type = 'button',
  'aria-label': ariaLabel,
}: ButtonProps) {
  const isInert = disabled || loading;

  const style: React.CSSProperties = {
    ...variantStyles[variant],
    borderRadius: tokens.radius.md,
    padding: `${tokens.spacing.sm}px ${tokens.spacing.lg}px`,
    minHeight: tokens.touchTarget,
    minWidth: tokens.touchTarget,
    fontSize: 16,
    fontWeight: 600,
    cursor: isInert ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.4 : 1,
    transition: `opacity ${tokens.animation.micro}, transform ${tokens.animation.micro}`,
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: tokens.spacing.xs,
    outline: 'none',
    position: 'relative',
  };

  return (
    <button
      type={type}
      style={style}
      disabled={isInert}
      onClick={isInert ? undefined : onClick}
      aria-label={ariaLabel}
      aria-busy={loading}
      onFocus={(e) => {
        (e.target as HTMLElement).style.outline = `2px solid ${tokens.color.focus}`;
        (e.target as HTMLElement).style.outlineOffset = '2px';
      }}
      onBlur={(e) => {
        (e.target as HTMLElement).style.outline = 'none';
      }}
    >
      {loading ? '…' : children}
    </button>
  );
}
