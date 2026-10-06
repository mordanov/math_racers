import { Link } from 'react-router-dom';
import { AvatarCard } from '../features/avatar/AvatarCard';
import { useAvatarGallery } from '../features/avatar/useAvatarGallery';
import { LoadingSpinner } from '../shared/components/LoadingSpinner';
import tokens from '../shared/tokens';
export default function AvatarGalleryPage() {
  const { avatars, loading, error } = useAvatarGallery();

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
            padding: `${tokens.spacing.sm} ${tokens.spacing.lg}`,
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
            padding: `${tokens.spacing.sm} ${tokens.spacing.lg}`,
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
            <AvatarCard avatar={avatar} />
          </div>
        ))}
      </div>
    </div>
  );
}
