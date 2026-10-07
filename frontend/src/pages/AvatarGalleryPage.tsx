import { Link } from 'react-router-dom';
import { AvatarCard } from '../features/avatar/AvatarCard';
import { useAvatarGallery } from '../features/avatar/useAvatarGallery';
import { LoadingSpinner } from '../shared/components/LoadingSpinner';
import tokens from '../shared/tokens';

export default function AvatarGalleryPage() {
  const {
    avatars,
    loading,
    error,
    mutationError,
    clearMutationError,
    toggleFavourite,
    renameAvatar,
    startRegenerate,
    removeAvatar,
  } = useAvatarGallery();

  if (loading)
    return (
      <div data-testid="page-avatar-gallery">
        <LoadingSpinner />
      </div>
    );

  if (error) {
    return (
      <div
        role="alert"
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: tokens.spacing.md,
          padding: tokens.spacing.xl,
          textAlign: 'center',
          color: tokens.color.textPrimary,
        }}
      >
        <span style={{ fontSize: 32 }} aria-hidden="true">
          😕
        </span>
        <p style={{ margin: 0 }}>{error}</p>
      </div>
    );
  }

  if (avatars.length === 0) {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: tokens.spacing.lg,
          padding: tokens.spacing.xl,
        }}
      >
        <h1 style={{ color: tokens.color.textPrimary }}>Your Avatars</h1>
        <p style={{ color: tokens.color.textSecondary }}>
          You don&apos;t have any avatars yet. Create your first one!
        </p>
        <Link
          to="/avatars/new"
          style={{
            padding: `${tokens.spacing.sm}px ${tokens.spacing.lg}px`,
            background: tokens.color.primary,
            color: '#fff',
            borderRadius: tokens.radius.md,
            textDecoration: 'none',
            fontWeight: 600,
          }}
        >
          Create Your First Avatar
        </Link>
      </div>
    );
  }

  return (
    <div style={{ padding: tokens.spacing.xl }}>
      {mutationError && (
        <div
          role="alert"
          aria-label="mutation error"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: tokens.spacing.md,
            padding: `${tokens.spacing.sm}px ${tokens.spacing.md}px`,
            background: '#FEF2F2',
            border: `1px solid ${tokens.color.error}`,
            borderRadius: tokens.radius.md,
            color: tokens.color.error,
            marginBottom: tokens.spacing.md,
            fontSize: 14,
          }}
        >
          <span>{mutationError}</span>
          <button
            type="button"
            aria-label="Dismiss"
            onClick={clearMutationError}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: tokens.color.error,
              fontSize: 18,
              lineHeight: 1,
              padding: tokens.spacing.xs,
            }}
          >
            ×
          </button>
        </div>
      )}

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: tokens.spacing.lg,
        }}
      >
        <h1 style={{ color: tokens.color.textPrimary }}>Your Avatars</h1>
        <Link
          to="/avatars/new"
          style={{
            padding: `${tokens.spacing.sm}px ${tokens.spacing.lg}px`,
            background: tokens.color.primary,
            color: '#fff',
            borderRadius: tokens.radius.md,
            textDecoration: 'none',
            fontWeight: 600,
          }}
        >
          + New Avatar
        </Link>
      </div>
      <div
        role="list"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
          gap: tokens.spacing.md,
        }}
      >
        {avatars.map((avatar) => (
          <div key={avatar.avatar_id} role="listitem">
            <AvatarCard
              avatar={avatar}
              onFavourite={(id, val) => void toggleFavourite(id, val)}
              onRename={(id, name) => void renameAvatar(id, name)}
              onRegenerate={(id) => void startRegenerate(id)}
              onDelete={(id) => void removeAvatar(id)}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
