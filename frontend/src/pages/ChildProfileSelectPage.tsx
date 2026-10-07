import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../infrastructure/auth/AuthContext';
import { createChildProfile, fetchChildProfiles } from '../infrastructure/auth/childProfilesApi';
import type { ChildProfile } from '../infrastructure/auth/types';
import { Button } from '../shared/components/Button';
import { LoadingSpinner } from '../shared/components/LoadingSpinner';
import tokens from '../shared/tokens';

const pageStyle: React.CSSProperties = {
  minHeight: '100vh',
  background: tokens.color.background,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: tokens.spacing.lg,
};

const cardStyle: React.CSSProperties = {
  background: tokens.color.surface,
  borderRadius: tokens.radius.lg,
  padding: tokens.spacing.xl,
  boxShadow: tokens.shadow.card,
  width: '100%',
  maxWidth: 560,
};

const profileButtonStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: tokens.spacing.sm,
  padding: tokens.spacing.md,
  background: tokens.color.surface,
  border: `1px solid ${tokens.color.border}`,
  borderRadius: tokens.radius.md,
  cursor: 'pointer',
  width: '100%',
};

const avatarCircleStyle: React.CSSProperties = {
  width: 48,
  height: 48,
  borderRadius: '50%',
  background: tokens.color.border,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: 20,
};

const inputStyle: React.CSSProperties = {
  flex: 1,
  padding: tokens.spacing.sm,
  border: `1px solid ${tokens.color.border}`,
  borderRadius: tokens.radius.sm,
  fontSize: 16,
  color: tokens.color.textPrimary,
  background: tokens.color.surface,
};

export default function ChildProfileSelectPage() {
  const { selectChild } = useAuth();
  const navigate = useNavigate();
  const [profiles, setProfiles] = useState<ChildProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newName, setNewName] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchChildProfiles()
      .then(setProfiles)
      .catch(() => setError('Could not load profiles.'))
      .finally(() => setLoading(false));
  }, []);

  const handleSelect = (profile: ChildProfile) => {
    selectChild(profile.id);
    void navigate('/', { replace: true });
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    setCreating(true);
    try {
      const created = await createChildProfile(newName.trim());
      setProfiles((prev) => [...prev, created]);
      setNewName('');
    } catch {
      setError('Could not create profile.');
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading profiles…" />;
  if (error) return <p role="alert">{error}</p>;

  return (
    <div style={pageStyle}>
      <div style={cardStyle}>
        <h1
          style={{
            margin: `0 0 ${tokens.spacing.xl}px`,
            color: tokens.color.textPrimary,
            textAlign: 'center',
            fontSize: 28,
            fontWeight: 700,
          }}
        >
          Who&apos;s Playing?
        </h1>

        {profiles.length === 0 ? (
          <p
            style={{
              color: tokens.color.textSecondary,
              textAlign: 'center',
              margin: `0 0 ${tokens.spacing.xl}px`,
            }}
          >
            No profiles yet — add one below.
          </p>
        ) : (
          <div
            data-testid="profile-list"
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))',
              gap: tokens.spacing.md,
              marginBottom: tokens.spacing.xl,
            }}
          >
            {profiles.map((p) => (
              <button
                key={p.id}
                type="button"
                style={profileButtonStyle}
                onClick={() => handleSelect(p)}
              >
                <div style={avatarCircleStyle} aria-hidden="true">
                  {p.display_name.charAt(0).toUpperCase()}
                </div>
                <span style={{ fontWeight: 600, color: tokens.color.textPrimary, fontSize: 14 }}>
                  {p.display_name}
                </span>
              </button>
            ))}
          </div>
        )}

        {profiles.length < 5 && (
          <div
            style={{
              borderTop: `1px solid ${tokens.color.border}`,
              paddingTop: tokens.spacing.lg,
            }}
          >
            <p
              style={{
                color: tokens.color.textSecondary,
                fontSize: 14,
                marginBottom: tokens.spacing.sm,
              }}
            >
              Add a profile
            </p>
            <form
              onSubmit={(e) => {
                void handleCreate(e);
              }}
              style={{ display: 'flex', gap: tokens.spacing.sm, alignItems: 'center' }}
            >
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Profile name"
                maxLength={50}
                aria-label="New profile name"
                style={inputStyle}
              />
              <Button type="submit" variant="primary" disabled={creating || !newName.trim()}>
                Add
              </Button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
