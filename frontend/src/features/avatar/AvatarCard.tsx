import type { AvatarListItem } from '../../engine/avatar/types';
import tokens from '../../shared/tokens';

interface AvatarCardProps {
  avatar: AvatarListItem;
  selected?: boolean;
  onSelect?: (avatarId: string) => void;
}

export function AvatarCard({ avatar, selected = false, onSelect }: AvatarCardProps) {
  const isPending = avatar.status === 'pending';
  const isFailed = avatar.status === 'failed';
  const displayName = avatar.name ?? avatar.species;

  const cardStyle: React.CSSProperties = {
    background: tokens.color.surface,
    borderRadius: tokens.radius.lg,
    padding: tokens.spacing.md,
    boxShadow: selected ? `0 0 0 3px ${tokens.color.primary}` : tokens.shadow.card,
    cursor: onSelect ? 'pointer' : 'default',
    border: 'none',
    textAlign: 'left',
    width: '100%',
    transition: `box-shadow ${tokens.animation.quick}`,
  };

  const content = (
    <>
      {isPending ? (
        <div
          style={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            background: tokens.color.border,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: tokens.spacing.sm,
          }}
        >
          <span aria-hidden="true" style={{ fontSize: 24 }}>
            ⏳
          </span>
        </div>
      ) : (
        <img
          src={avatar.portrait?.small_url}
          alt={displayName}
          style={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            objectFit: 'cover',
            marginBottom: tokens.spacing.sm,
          }}
        />
      )}
      <div style={{ fontWeight: 600, color: tokens.color.textPrimary }}>{displayName}</div>
      <div
        style={{
          fontSize: 14,
          color: tokens.color.textSecondary,
          textTransform: 'capitalize',
        }}
      >
        {avatar.species}
      </div>
      {isPending && (
        <div style={{ fontSize: 12, color: tokens.color.primary, marginTop: tokens.spacing.xs }}>
          Generating…
        </div>
      )}
      {isFailed && (
        <div style={{ fontSize: 12, color: tokens.color.error, marginTop: tokens.spacing.xs }}>
          Hmm, something went wobbly.
        </div>
      )}
    </>
  );

  if (onSelect) {
    return (
      <button
        type="button"
        style={cardStyle}
        aria-pressed={selected}
        onClick={() => onSelect(avatar.avatar_id)}
        onFocus={(e) => {
          (e.currentTarget as HTMLElement).style.outline = `2px solid ${tokens.color.focus}`;
          (e.currentTarget as HTMLElement).style.outlineOffset = '2px';
        }}
        onBlur={(e) => {
          (e.currentTarget as HTMLElement).style.outline = 'none';
        }}
      >
        {content}
      </button>
    );
  }

  return <div style={cardStyle}>{content}</div>;
}
