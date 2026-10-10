import { useEffect, useState } from 'react';
import {
  fetchHistory,
  fetchPlayerStats,
  type HistoryResponse,
  type PlayerStats,
} from '../features/statistics/statisticsApi';
import tokens from '../shared/tokens';

function fmtPct(value: number | null): string {
  if (value === null) return '—';
  return `${Math.round(value * 100)}%`;
}

export default function StatisticsPage() {
  const [stats, setStats] = useState<PlayerStats | null>(null);
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    setLoading(true);
    setError(false);
    void Promise.all([fetchPlayerStats(), fetchHistory(page)])
      .then(([s, h]) => {
        setStats(s);
        setHistory(h);
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, [page]);

  return (
    <div
      data-testid="page-statistics"
      style={{ maxWidth: 700, margin: '0 auto', padding: tokens.spacing.xl }}
    >
      <h1 style={{ fontSize: 28, fontWeight: 900, marginBottom: tokens.spacing.lg }}>Statistics</h1>

      {loading && <p>Loading…</p>}
      {error && <p>Failed to load statistics. Please try again.</p>}

      {stats && (
        <section aria-label="Player statistics" style={{ marginBottom: tokens.spacing.xl }}>
          <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: tokens.spacing.md }}>
            All-Time
          </h2>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: tokens.spacing.md,
            }}
          >
            {[
              { label: 'Races', value: String(stats.total_races) },
              { label: 'Accuracy', value: fmtPct(stats.accuracy_all_time) },
              {
                label: 'Favourite operation',
                value: stats.favourite_operation ?? '—',
              },
              {
                label: 'Avg response (ms)',
                value: stats.avg_response_ms !== null ? String(stats.avg_response_ms) : '—',
              },
              { label: 'Best streak', value: String(stats.best_streak) },
            ].map(({ label, value }) => (
              <div
                key={label}
                style={{
                  background: tokens.color.surface,
                  borderRadius: tokens.radius.lg,
                  padding: tokens.spacing.md,
                  boxShadow: tokens.shadow.card,
                  textAlign: 'center',
                }}
              >
                <p style={{ fontSize: 32, fontWeight: 900, color: tokens.color.primary }}>
                  {value}
                </p>
                <p style={{ fontSize: 12, color: tokens.color.textSecondary, marginTop: 4 }}>
                  {label}
                </p>
              </div>
            ))}
          </div>
        </section>
      )}

      {history && (
        <section aria-label="Race history">
          <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: tokens.spacing.md }}>
            Recent Races
          </h2>
          {history.results.length === 0 ? (
            <p style={{ color: tokens.color.textSecondary }}>No races yet.</p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
              <thead>
                <tr>
                  {['Mode', 'Position', 'Score', 'Streak', 'XP'].map((h) => (
                    <th
                      key={h}
                      scope="col"
                      style={{
                        textAlign: 'left',
                        padding: `${tokens.spacing.xs}px ${tokens.spacing.sm}px`,
                        borderBottom: `1px solid ${tokens.color.border}`,
                        color: tokens.color.textSecondary,
                        fontWeight: 600,
                      }}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {history.results.map((r) => (
                  <tr key={r.id}>
                    <td style={{ padding: `${tokens.spacing.xs}px ${tokens.spacing.sm}px` }}>
                      {r.mode}
                    </td>
                    <td style={{ padding: `${tokens.spacing.xs}px ${tokens.spacing.sm}px` }}>
                      {r.finishing_position ?? '—'}
                    </td>
                    <td style={{ padding: `${tokens.spacing.xs}px ${tokens.spacing.sm}px` }}>
                      {r.correct_answers} / {r.problems_solved}
                    </td>
                    <td style={{ padding: `${tokens.spacing.xs}px ${tokens.spacing.sm}px` }}>
                      {r.longest_streak}
                    </td>
                    <td style={{ padding: `${tokens.spacing.xs}px ${tokens.spacing.sm}px` }}>
                      {r.xp_earned}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {history.total_pages > 1 && (
            <div style={{ marginTop: tokens.spacing.md, display: 'flex', gap: tokens.spacing.sm }}>
              <button
                type="button"
                disabled={page === 1}
                onClick={() => setPage((p) => p - 1)}
                style={{ padding: `${tokens.spacing.xs}px ${tokens.spacing.sm}px` }}
              >
                Previous
              </button>
              <span style={{ color: tokens.color.textSecondary, alignSelf: 'center' }}>
                Page {history.page} of {history.total_pages}
              </span>
              <button
                type="button"
                disabled={page === history.total_pages}
                onClick={() => setPage((p) => p + 1)}
                style={{ padding: `${tokens.spacing.xs}px ${tokens.spacing.sm}px` }}
              >
                Next
              </button>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
