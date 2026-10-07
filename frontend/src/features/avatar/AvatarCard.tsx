import { useEffect, useRef, useState } from 'react';
import type { AvatarListItem } from '../../engine/avatar/types';
import { ConfirmDialog } from '../../shared/components/ConfirmDialog';
import tokens from '../../shared/tokens';

interface AvatarCardProps {
  avatar: AvatarListItem;
  selected?: boolean;
  onSelect?: (avatarId: string) => void;
  onFavourite?: (avatarId: string, isFavourite: boolean) => void;
  onRename?: (avatarId: string, name: string) => void;
  onRegenerate?: (avatarId: string) => void;
  onDelete?: (avatarId: string) => void;
}

const starBtnStyle: React.CSSProperties = {
  position: 'absolute',
  top: tokens.spacing.sm,
  right: tokens.spacing.sm,
  background: 'none',
  border: 'none',
  cursor: 'pointer',
  fontSize: 18,
  padding: 2,
  lineHeight: 1,
};

const manageBtnStyle: React.CSSProperties = {
  position: 'absolute',
  bottom: tokens.spacing.sm,
  right: tokens.spacing.sm,
  background: 'none',
  border: 'none',
  cursor: 'pointer',
  fontSize: 18,
  padding: 2,
  lineHeight: 1,
};

const menuStyle: React.CSSProperties = {
  position: 'absolute',
  bottom: tokens.spacing.xl,
  right: tokens.spacing.sm,
  background: tokens.color.surface,
  boxShadow: tokens.shadow.overlay,
  borderRadius: tokens.radius.md,
  display: 'flex',
  flexDirection: 'column',
  zIndex: 10,
  minWidth: 120,
};

const menuItemStyle: React.CSSProperties = {
  background: 'none',
  border: 'none',
  cursor: 'pointer',
  padding: `${tokens.spacing.sm}px ${tokens.spacing.md}px`,
  textAlign: 'left',
  width: '100%',
  fontSize: 14,
  color: tokens.color.textPrimary,
};

export function AvatarCard({
  avatar,
  selected = false,
  onSelect,
  onFavourite,
  onRename,
  onRegenerate,
  onDelete,
}: AvatarCardProps) {
  const isPending = avatar.status === 'pending';
  const isFailed = avatar.status === 'failed';
  const rawName = avatar.name ?? avatar.species;
  const displayName = rawName.length > 24 ? rawName.slice(0, 24) + '…' : rawName;

  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [showManage, setShowManage] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (showManage && menuRef.current) {
      menuRef.current.querySelector<HTMLElement>('[role="menuitem"]')?.focus();
    }
  }, [showManage]);

  const hasManage = !!(onRename || onRegenerate || onDelete);

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
    position: 'relative',
  };

  const handleSave = () => {
    const trimmed = editName.trim();
    if (!trimmed) return;
    onRename?.(avatar.avatar_id, trimmed);
    setIsEditing(false);
    setEditName('');
  };

  const content = (
    <>
      {onFavourite && (
        <button
          type="button"
          aria-label={avatar.is_favourite ? 'Remove from favourites' : 'Add to favourites'}
          style={starBtnStyle}
          onClick={() => onFavourite(avatar.avatar_id, !avatar.is_favourite)}
        >
          {avatar.is_favourite ? '★' : '☆'}
        </button>
      )}

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
          alt={rawName}
          style={{
            width: 80,
            height: 80,
            borderRadius: '50%',
            objectFit: 'cover',
            marginBottom: tokens.spacing.sm,
          }}
        />
      )}

      {isEditing ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: tokens.spacing.xs }}>
          <input
            type="text"
            aria-label="Rename avatar"
            value={editName}
            onChange={(e) => setEditName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Escape') {
                setIsEditing(false);
                setEditName('');
              } else if (e.key === 'Enter' && editName.trim()) {
                handleSave();
              }
            }}
            autoFocus
          />
          <button type="button" disabled={!editName.trim()} onClick={handleSave}>
            Save
          </button>
        </div>
      ) : (
        <>
          <div
            title={rawName}
            style={{
              fontWeight: 600,
              color: tokens.color.textPrimary,
              overflow: 'hidden',
              whiteSpace: 'nowrap',
            }}
          >
            {displayName}
          </div>
          <div
            style={{
              fontSize: 14,
              color: tokens.color.textSecondary,
              textTransform: 'capitalize',
            }}
          >
            {avatar.species}
          </div>
        </>
      )}

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

      {hasManage && (
        <>
          <button
            type="button"
            aria-label="Manage avatar"
            style={manageBtnStyle}
            onClick={() => setShowManage((v) => !v)}
          >
            ⋯
          </button>

          {showManage && (
            <div
              role="menu"
              ref={menuRef}
              style={menuStyle}
              onKeyDown={(e) => {
                if (e.key === 'Escape') {
                  setShowManage(false);
                  return;
                }
                if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;
                e.preventDefault();
                const items = Array.from(
                  menuRef.current?.querySelectorAll<HTMLElement>('[role="menuitem"]') ?? [],
                );
                const idx = items.indexOf(document.activeElement as HTMLElement);
                const next =
                  e.key === 'ArrowDown'
                    ? (idx + 1) % items.length
                    : (idx - 1 + items.length) % items.length;
                items[next]?.focus();
              }}
            >
              {onRename && (
                <button
                  type="button"
                  role="menuitem"
                  tabIndex={-1}
                  style={menuItemStyle}
                  onClick={() => {
                    setEditName(rawName);
                    setIsEditing(true);
                    setShowManage(false);
                  }}
                >
                  Rename
                </button>
              )}
              {onRegenerate && (
                <button
                  type="button"
                  role="menuitem"
                  tabIndex={-1}
                  style={menuItemStyle}
                  onClick={() => {
                    onRegenerate(avatar.avatar_id);
                    setShowManage(false);
                  }}
                >
                  Regenerate
                </button>
              )}
              {onDelete && (
                <button
                  type="button"
                  role="menuitem"
                  tabIndex={-1}
                  style={menuItemStyle}
                  onClick={() => {
                    setShowDeleteConfirm(true);
                    setShowManage(false);
                  }}
                >
                  Delete
                </button>
              )}
            </div>
          )}
        </>
      )}

      <ConfirmDialog
        open={showDeleteConfirm}
        title="Delete avatar?"
        message="This cannot be undone."
        confirmLabel="Delete"
        onConfirm={() => {
          onDelete?.(avatar.avatar_id);
          setShowDeleteConfirm(false);
        }}
        onClose={() => setShowDeleteConfirm(false)}
      />
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
