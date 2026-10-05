import tokens from '../tokens';

interface CardProps {
  children: React.ReactNode;
  onClick?: () => void;
  'data-testid'?: string;
}

export function Card({ children, onClick, 'data-testid': testId }: CardProps) {
  const style: React.CSSProperties = {
    background: tokens.color.surface,
    borderRadius: tokens.radius.lg,
    padding: tokens.spacing.lg,
    boxShadow: tokens.shadow.card,
    transition: `box-shadow ${tokens.animation.quick}`,
  };

  if (onClick) {
    return (
      <button
        type="button"
        data-testid={testId}
        style={{ ...style, cursor: 'pointer', border: 'none', textAlign: 'left', width: '100%' }}
        onClick={onClick}
        onFocus={(e) => { (e.target as HTMLElement).style.outline = `2px solid ${tokens.color.focus}`; (e.target as HTMLElement).style.outlineOffset = '2px'; }}
        onBlur={(e) => { (e.target as HTMLElement).style.outline = 'none'; }}
        onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.boxShadow = tokens.shadow.cardHover; }}
        onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.boxShadow = tokens.shadow.card; }}
      >
        {children}
      </button>
    );
  }

  return (
    <div data-testid={testId} style={style}>
      {children}
    </div>
  );
}
