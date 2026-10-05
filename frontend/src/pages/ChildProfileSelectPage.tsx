import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../infrastructure/auth/AuthContext';
import { createChildProfile, fetchChildProfiles } from '../infrastructure/auth/childProfilesApi';
import type { ChildProfile } from '../infrastructure/auth/types';
import { Button } from '../shared/components/Button';
import { LoadingSpinner } from '../shared/components/LoadingSpinner';

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
    <main>
      <h1>Who's Playing?</h1>
      {profiles.length === 0 ? (
        <p>No profiles yet — add one below.</p>
      ) : (
        <ul data-testid="profile-list">
          {profiles.map((p) => (
            <li key={p.id}>
              <button type="button" onClick={() => handleSelect(p)}>
                {p.display_name}
              </button>
            </li>
          ))}
        </ul>
      )}
      {profiles.length < 5 && (
        <form
          onSubmit={(e) => {
            void handleCreate(e);
          }}
        >
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Profile name"
            maxLength={50}
            aria-label="New profile name"
          />
          <Button type="submit" variant="primary" disabled={creating || !newName.trim()}>
            Add
          </Button>
        </form>
      )}
    </main>
  );
}
