import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getChampionship, type ChampionshipState } from '../engine/race/championshipApi';
import { Button } from '../shared/components/Button';
import { LoadingSpinner } from '../shared/components/LoadingSpinner';
import tokens from '../shared/tokens';

export default function ChampionshipPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [championship, setChampionship] = useState<ChampionshipState | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    getChampionship(id)
      .then(setChampionship)
      .catch(() => {
        /* championship stays null → shows "not found" */
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div data-testid="page-championship">
        <LoadingSpinner message="Loading standings…" />
      </div>
    );
  }

  if (!championship) {
    return (
      <div data-testid="page-championship" style={{ padding: tokens.spacing.xl }}>
        Championship not found.
      </div>
    );
  }

  const isCompleted = championship.status === 'completed';

  function handleStartNext() {
    void navigate('/race/setup', {
      state: {
        continueChampionshipId: championship!.championship_id,
        continueRaceIndex: championship!.races_completed,
      },
    });
  }

  return (
    <div
      data-testid="page-championship"
      style={{ maxWidth: 640, margin: '0 auto', padding: tokens.spacing.xl }}
    >
      <h1 style={{ color: tokens.color.textPrimary, marginBottom: tokens.spacing.xs }}>
        Championship
      </h1>
      <p style={{ color: tokens.color.textSecondary, marginBottom: tokens.spacing.lg }}>
        Race {championship.races_completed} of {championship.total_races} complete
      </p>

      <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: tokens.spacing.lg }}>
        <thead>
          <tr>
            {['Position', 'Runner', 'Points', 'Podiums'].map((h) => (
              <th
                key={h}
                scope="col"
                style={{
                  padding: tokens.spacing.sm,
                  borderBottom: `2px solid ${tokens.color.border}`,
                  color: tokens.color.textSecondary,
                  fontSize: 14,
                  fontWeight: 600,
                  textAlign: h === 'Position' || h === 'Runner' ? 'left' : 'right',
                }}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {championship.standings.map((entry) => (
            <tr
              key={entry.avatar_id}
              style={{ background: entry.is_player ? `${tokens.color.primary}18` : 'transparent' }}
            >
              <th scope="row" style={{ padding: tokens.spacing.sm, fontWeight: 400 }}>
                {entry.position}
              </th>
              <td style={{ padding: tokens.spacing.sm, fontWeight: entry.is_player ? 700 : 400 }}>
                {entry.is_player ? 'You' : 'Opponent'}
              </td>
              <td style={{ padding: tokens.spacing.sm, textAlign: 'right' }}>{entry.points}</td>
              <td style={{ padding: tokens.spacing.sm, textAlign: 'right' }}>{entry.podiums}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {isCompleted ? (
        <div>
          <h2 style={{ color: tokens.color.success }}>Championship Complete!</h2>
          <Button variant="primary" onClick={() => void navigate('/race/setup')}>
            Play Again
          </Button>
        </div>
      ) : (
        <Button variant="primary" onClick={handleStartNext}>
          Start Next Race
        </Button>
      )}
    </div>
  );
}
