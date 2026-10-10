import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  assignLegacyData,
  deleteChildProfile,
  exportChildData,
  listLegacyData,
  type LegacyRecord,
} from '../engine/childProfiles/childProfilesApi';
import { fetchPersonalRecords, type PersonalRecords } from '../features/statistics/parentApi';
import {
  fetchWeeklySummary,
  type PlayerStats,
  type WeeklySummary,
} from '../features/statistics/statisticsApi';
import { useAuth } from '../infrastructure/auth/AuthContext';
import { deleteCachedChildData, getCachedChildData } from '../infrastructure/offline/offlineStore';
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
  const { activeChildId, selectChild } = useAuth();
  const [summary, setSummary] = useState<WeeklySummary | null>(null);
  const [records, setRecords] = useState<PersonalRecords | null>(null);
  const [cachedStats, setCachedStats] = useState<PlayerStats | null>(null);
  const [legacyRecords, setLegacyRecords] = useState<LegacyRecord[]>([]);
  const [selectedLegacyKeys, setSelectedLegacyKeys] = useState<string[]>([]);
  const [childActionMessage, setChildActionMessage] = useState<string | null>(null);
  const [childActionError, setChildActionError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!isOffline || !activeChildId) return;
    let cancelled = false;
    getCachedChildData(activeChildId)
      .then((data) => {
        if (!cancelled) setCachedStats(data?.statistics ?? null);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });
    return () => {
      cancelled = true;
    };
  }, [activeChildId, isOffline]);

  useEffect(() => {
    if (isOffline) return;
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
  }, [isOffline]);

  useEffect(() => {
    if (isOffline || !activeChildId) return;
    let cancelled = false;
    listLegacyData(activeChildId)
      .then((items) => {
        if (!cancelled) setLegacyRecords(items);
      })
      .catch(() => {
        if (!cancelled) setChildActionError('Could not load unassigned child data.');
      });
    return () => {
      cancelled = true;
    };
  }, [activeChildId, isOffline]);

  function toggleLegacyRecord(key: string, selected: boolean): void {
    setSelectedLegacyKeys((current) =>
      selected ? [...current, key] : current.filter((item) => item !== key),
    );
  }

  async function assignSelectedRecords(): Promise<void> {
    if (!activeChildId) return;
    const selected = new Set(selectedLegacyKeys);
    const assignments = legacyRecords
      .filter((item) => selected.has(`${item.record_type}:${item.record_id}`))
      .map(({ record_type, record_id }) => ({ record_type, record_id }));
    if (assignments.length === 0) return;

    try {
      const response = await assignLegacyData(activeChildId, assignments);
      setSelectedLegacyKeys([]);
      setLegacyRecords(await listLegacyData(activeChildId));
      setChildActionMessage(`${response.assigned} records assigned to this child.`);
      setChildActionError(null);
    } catch {
      setChildActionError('Could not assign the selected records. Refresh and try again.');
    }
  }

  async function downloadChildData(): Promise<void> {
    if (!activeChildId) return;
    try {
      const data = await exportChildData(activeChildId);
      const url = URL.createObjectURL(
        new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }),
      );
      const link = document.createElement('a');
      link.href = url;
      link.download = `child-data-${activeChildId}.json`;
      link.click();
      URL.revokeObjectURL(url);
      setChildActionError(null);
    } catch {
      setChildActionError('Could not export this child data.');
    }
  }

  async function deleteSelectedChild(): Promise<void> {
    if (!activeChildId || !window.confirm('Delete this child profile and all its data?')) return;
    const childProfileId = activeChildId;
    try {
      await deleteChildProfile(childProfileId);
    } catch {
      setChildActionError('Could not delete this child profile.');
      return;
    }
    selectChild(null);
    try {
      await deleteCachedChildData(childProfileId);
    } catch {
      setChildActionError(
        'The profile was deleted, but saved offline data could not be removed from this device.',
      );
      return;
    }
    await navigate('/child-profiles');
  }

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
        <p style={{ fontSize: 20, color: tokens.color.textPrimary }}>You are offline.</p>
        {cachedStats ? (
          <section aria-label="Saved progress">
            <h2>Last saved progress</h2>
            <p>{cachedStats.total_races} races completed</p>
            <p>{cachedStats.total_problems_solved} problems answered</p>
            <p>Accuracy: {fmtPct(cachedStats.accuracy_all_time)}</p>
            <p>Favourite operation: {cachedStats.favourite_operation ?? '—'}</p>
          </section>
        ) : (
          <p role="status">No saved progress is available for this child.</p>
        )}
        {error && <p role="alert">Could not load saved progress.</p>}
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
            <p>Strongest operation: {summary.strongest_operation ?? '—'}</p>
            <p>Weakest operation: {summary.weakest_operation ?? '—'}</p>
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

      <section aria-label="Child data management" style={{ marginBottom: tokens.spacing.xl }}>
        <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: tokens.spacing.md }}>
          Child Data
        </h2>
        {activeChildId ? (
          <>
            <p>Unassigned records are not visible to this child until you assign them.</p>
            {legacyRecords.length > 0 ? (
              <fieldset>
                <legend>Unassigned records</legend>
                {legacyRecords.map((item) => {
                  const key = `${item.record_type}:${item.record_id}`;
                  return (
                    <label key={key} style={{ display: 'block', marginBottom: tokens.spacing.xs }}>
                      <input
                        type="checkbox"
                        checked={selectedLegacyKeys.includes(key)}
                        onChange={(event) => toggleLegacyRecord(key, event.target.checked)}
                      />{' '}
                      {item.record_type}: {item.label}
                    </label>
                  );
                })}
                <Button
                  variant="secondary"
                  disabled={selectedLegacyKeys.length === 0}
                  onClick={() => void assignSelectedRecords()}
                >
                  Assign selected data
                </Button>
              </fieldset>
            ) : (
              <p>No unassigned records.</p>
            )}
            <div style={{ display: 'flex', gap: tokens.spacing.md, flexWrap: 'wrap' }}>
              <Button variant="secondary" onClick={() => void downloadChildData()}>
                Export child data
              </Button>
              <Button variant="secondary" onClick={() => void deleteSelectedChild()}>
                Delete child profile and data
              </Button>
            </div>
          </>
        ) : (
          <p>Select a child profile to manage child data.</p>
        )}
        {childActionMessage && <p role="status">{childActionMessage}</p>}
        {childActionError && <p role="alert">{childActionError}</p>}
      </section>

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
