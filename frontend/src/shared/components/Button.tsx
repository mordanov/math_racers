import { useState } from 'react';
import { useSfxPlayer } from '../hooks/useSfxPlayer';
import tokens from '../tokens';

interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  type?: 'button' | 'submit' | 'reset';
  'aria-label'?: string;
  playSound?: boolean;
}

const baseStyle: React.CSSProperties = {
  borderRadius: tokens.radius.lg,
  padding: `${tokens.spacing.md}px ${tokens.spacing.xl}px`,
  minHeight: tokens.touchTarget,
  minWidth: tokens.touchTarget,
  fontSize: tokens.fontSize.base,
  fontWeight: 800,
  letterSpacing: '0.02em',
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: tokens.spacing.xs,
  outline: 'none',
  position: 'relative',
  transition: `opacity ${tokens.animation.micro}, transform ${tokens.animation.micro}, box-shadow ${tokens.animation.micro}`,
};

const variantBase: Record<ButtonProps['variant'], React.CSSProperties> = {
  primary: {
    background: tokens.color.primary,
    color: tokens.color.textOnPrimary,
    border: 'none',
    boxShadow: `0 6px 0 ${tokens.color.primaryActive}`,
  },
  secondary: {
    background: tokens.color.surface,
    color: tokens.color.primary,
    border: `3px solid ${tokens.color.primary}`,
    boxShadow: 'none',
  },
  ghost: {
    background: 'rgba(255,255,255,0.9)',
    color: tokens.color.textPrimary,
    border: 'none',
    boxShadow: 'none',
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
  playSound = false,
}: ButtonProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [isPressed, setIsPressed] = useState(false);
  const isInert = disabled || loading;
  const { playSfx } = useSfxPlayer();

  let interactionStyle: React.CSSProperties = {};
  if (!isInert && isPressed && variant === 'primary') {
    interactionStyle = {
      transform: 'translateY(4px)',
      boxShadow: `0 2px 0 ${tokens.color.primaryActive}`,
    };
  } else if (!isInert && isHovered) {
    if (variant === 'primary') {
      interactionStyle = {
        transform: 'translateY(-2px)',
        boxShadow: `0 8px 0 ${tokens.color.primaryActive}`,
      };
    } else if (variant === 'secondary') {
      interactionStyle = { transform: 'translateY(-2px)', background: '#FFF0EA' };
    } else if (variant === 'ghost') {
      interactionStyle = { background: tokens.color.surface };
    }
  }

  const style: React.CSSProperties = {
    ...baseStyle,
    ...variantBase[variant],
    ...interactionStyle,
    cursor: isInert ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.4 : 1,
  };

  return (
    <button
      type={type}
      style={style}
      disabled={isInert}
      onClick={
        isInert
          ? undefined
          : () => {
              if (playSound) playSfx('ui_click');
              onClick?.();
            }
      }
      onMouseEnter={
        isInert
          ? undefined
          : () => {
              setIsHovered(true);
              if (playSound) playSfx('ui_hover');
            }
      }
      onMouseLeave={
        isInert
          ? undefined
          : () => {
              setIsHovered(false);
              setIsPressed(false);
            }
      }
      onMouseDown={isInert ? undefined : () => setIsPressed(true)}
      onMouseUp={isInert ? undefined : () => setIsPressed(false)}
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
