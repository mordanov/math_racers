import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getChampionship } from '../engine/race/championshipApi';
import { Button } from '../shared/components/Button';
import { useAudioManager } from '../shared/hooks/useAudioManager';
import tokens from '../shared/tokens';

export default function HomePage() {
  const navigate = useNavigate();
  const [activeChampionshipId, setActiveChampionshipId] = useState<string | null>(null);
  const { playMusic, stopMusic } = useAudioManager();

  useEffect(() => {
    playMusic('menu');
    return () => stopMusic();
  }, []); // playMusic/stopMusic are stable useCallback refs

  useEffect(() => {
    const savedId = localStorage.getItem('activeChampionshipId');
    if (!savedId) return;
    getChampionship(savedId)
      .then((c) => {
        if (c.status === 'active') setActiveChampionshipId(savedId);
        else localStorage.removeItem('activeChampionshipId');
      })
      .catch(() => localStorage.removeItem('activeChampionshipId'));
  }, []);

  return (
    <div
      data-testid="page-home"
      style={{ maxWidth: 480, margin: '0 auto', padding: tokens.spacing.xl, textAlign: 'center' }}
    >
      <h1
        style={{
          fontSize: 40,
          fontWeight: 900,
          color: tokens.color.textPrimary,
          marginBottom: tokens.spacing.xl,
        }}
      >
        Math Racers
      </h1>

      {activeChampionshipId && (
        <div
          style={{
            marginBottom: tokens.spacing.lg,
            padding: tokens.spacing.md,
            background: `${tokens.color.warning}22`,
            borderRadius: tokens.radius.md,
            border: `1px solid ${tokens.color.warning}`,
          }}
        >
          <p style={{ margin: `0 0 ${tokens.spacing.sm}px`, color: tokens.color.textPrimary }}>
            You have an active championship!
          </p>
          <Button
            variant="primary"
            onClick={() => void navigate(`/championship/${activeChampionshipId}`)}
          >
            Continue Championship
          </Button>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: tokens.spacing.md }}>
        <Button variant="primary" onClick={() => void navigate('/race/setup')}>
          Start Racing
        </Button>
        <Button variant="secondary" onClick={() => void navigate('/avatars')}>
          My Avatars
        </Button>
        <Button variant="secondary" onClick={() => void navigate('/statistics')}>
          Statistics
        </Button>
      </div>
    </div>
  );
}
