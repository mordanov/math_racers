import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchPersonalRecords, type PersonalRecords } from '../features/statistics/parentApi';
import { fetchWeeklySummary, type WeeklySummary } from '../features/statistics/statisticsApi';
import { Button } from '../shared/components/Button';
import { useOffline } from '../shared/hooks/useOffline';
import tokens from '../shared/tokens';

function fmtPct(value: number | null): string {
  if (value === null) return '—';
  return `${Math.round(value * 100)}%`;
}

export default function ParentDashboardPage() {
  const navigate = useNavigate();
  const isOffline = useOffline();
  const [summary, setSummary] = useState<WeeklySummary | null>(null);
  const [records, setRecords] = useState<PersonalRecords | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    void Promise.all([fetchWeeklySummary(), fetchPersonalRecords()])
      .then(([s, r]) => {
        setSummary(s);
        setRecords(r);
        setLoading(false);
      })
      .catch(() => {
        setError(true);
        setLoading(false);
      });
  }, []);

  if (isOffline) {
    return (
      <div
        data-testid="page-parent-dashboard"
        role="alert"
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: tokens.spacing.lg,
          padding: tokens.spacing.xl,
          textAlign: 'center',
        }}
      >
        <p style={{ fontSize: 20, color: tokens.color.textPrimary }}>
          Internet required to view parent dashboard.
        </p>
        <Button variant="secondary" onClick={() => void navigate(-1)}>
          Go Back
        </Button>
      </div>
    );
  }

  return (
    <div
      data-testid="page-parent-dashboard"
      style={{ maxWidth: 700, margin: '0 auto', padding: tokens.spacing.xl }}
    >
      <h1 style={{ fontSize: 28, fontWeight: 900, marginBottom: tokens.spacing.lg }}>
        Parent Dashboard
      </h1>

      {loading && <p>Loading…</p>}
      {error && <p>Failed to load data. Please try again.</p>}

      {summary && (
        <section aria-label="This week" style={{ marginBottom: tokens.spacing.xl }}>
          <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: tokens.spacing.md }}>
            This Week
          </h2>
          <div
            style={{
              background: tokens.color.surface,
              borderRadius: tokens.radius.lg,
              padding: tokens.spacing.lg,
              boxShadow: tokens.shadow.card,
            }}
          >
            <p>
              <strong>{summary.races_completed} races</strong> completed
            </p>
            <p>
              {summary.problems_solved} problems solved ({summary.correct_answers} correct)
            </p>
            <p>Accuracy: {fmtPct(summary.accuracy)}</p>
            <p>
              Avg response:{' '}
              {summary.avg_response_ms !== null ? `${summary.avg_response_ms} ms` : '—'}
            </p>
            <p>XP earned: {summary.xp_earned}</p>
          </div>
        </section>
      )}

      {records && (
        <section aria-label="All-time records" style={{ marginBottom: tokens.spacing.xl }}>
          <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: tokens.spacing.md }}>
            All-Time Records
          </h2>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: tokens.spacing.md,
            }}
          >
            {[
              { label: 'Total Races', value: String(records.total_races) },
              { label: 'Best Streak', value: String(records.best_streak) },
              { label: 'Best Accuracy', value: fmtPct(records.best_race_accuracy) },
              {
                label: 'Fastest Avg (ms)',
                value:
                  records.fastest_avg_response_ms !== null
                    ? String(records.fastest_avg_response_ms)
                    : '—',
              },
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
                <p style={{ fontSize: 28, fontWeight: 900, color: tokens.color.primary }}>
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

      <section aria-label="Data export">
        <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: tokens.spacing.md }}>Export</h2>
        <a
          href="/api/v1/players/me/export"
          download="statistics.csv"
          style={{
            display: 'inline-block',
            padding: `${tokens.spacing.sm}px ${tokens.spacing.lg}px`,
            background: tokens.color.primary,
            color: tokens.color.textOnPrimary,
            borderRadius: tokens.radius.md,
            textDecoration: 'none',
            fontWeight: 700,
            minHeight: tokens.touchTarget,
            lineHeight: `${tokens.touchTarget}px`,
          }}
        >
          Export race history (CSV)
        </a>
      </section>
    </div>
  );
}
