import { render, screen, act, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import RaceScreenPage from './RaceScreenPage';
import * as useRaceEngineModule from '../engine/race/hooks/useRaceEngine';
import type { RaceEngineState } from '../engine/race/types';

vi.mock('../engine/race/hooks/useRaceEngine');

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return {
    ...actual,
    useBlocker: vi.fn().mockReturnValue({ state: 'unblocked', proceed: vi.fn(), reset: vi.fn() }),
  };
});

type EngineReturn = ReturnType<typeof useRaceEngineModule.useRaceEngine>;

const problem = {
  id: 'p1',
  operation: 'addition' as const,
  operand_a: 3,
  operand_b: 4,
  answer: 7,
  tier: 1 as const,
  seed: 1,
};

const baseState: RaceEngineState = {
  state: 'IDLE',
  config: null,
  clockMs: 0,
  obstacleClockMs: 0,
  currentObstacle: -1,
  runners: [],
  problemSet: null,
};

function makeEngineReturn(overrides: Partial<EngineReturn> = {}): EngineReturn {
  return {
    ...baseState,
    startCountdown: vi.fn(),
    startRacing: vi.fn(),
    submitAnswer: vi.fn(),
    forceComplete: vi.fn(),
    getSummary: vi.fn(),
    ...overrides,
  } as EngineReturn;
}

const routeState = {
  mode: 'quick' as const,
  tier: 1 as const,
  seed: 42,
  avatarId: 'av1',
  opponentCount: 1,
  raceIndex: 0,
};

function renderPage(state: unknown = routeState) {
  return render(
    <MemoryRouter initialEntries={[{ pathname: '/race/r1', state }]}>
      <Routes>
        <Route path="/race/:id" element={<RaceScreenPage />} />
        <Route path="/race/:id/results" element={<div>Results</div>} />
        <Route path="/race/setup" element={<div>Setup</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('RaceScreenPage', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(makeEngineReturn());
  });
  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  it('renders empty page when no route state', () => {
    render(
      <MemoryRouter initialEntries={['/race/r1']}>
        <Routes>
          <Route path="/race/:id" element={<RaceScreenPage />} />
        </Routes>
      </MemoryRouter>,
    );
    expect(screen.getByTestId('page-race-screen')).toBeInTheDocument();
  });

  it('calls startCountdown on mount', () => {
    const startCountdown = vi.fn();
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(makeEngineReturn({ startCountdown }));
    renderPage();
    expect(startCountdown).toHaveBeenCalledTimes(1);
  });

  it('shows countdown 3 in aria-live region when COUNTDOWN starts', () => {
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({ state: 'COUNTDOWN' }),
    );
    renderPage();
    expect(screen.getByRole('status')).toHaveTextContent('3');
  });

  it('counts down 3→2→1→GO! with timers', () => {
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({ state: 'COUNTDOWN' }),
    );
    renderPage();
    expect(screen.getByRole('status')).toHaveTextContent('3');
    act(() => { vi.advanceTimersByTime(1000); });
    expect(screen.getByRole('status')).toHaveTextContent('2');
    act(() => { vi.advanceTimersByTime(1000); });
    expect(screen.getByRole('status')).toHaveTextContent('1');
    act(() => { vi.advanceTimersByTime(1000); });
    expect(screen.getByRole('status')).toHaveTextContent('GO!');
  });

  it('calls startRacing after GO! delay', () => {
    const startRacing = vi.fn();
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({ state: 'COUNTDOWN', startRacing }),
    );
    renderPage();
    act(() => { vi.advanceTimersByTime(1000); });
    act(() => { vi.advanceTimersByTime(1000); });
    act(() => { vi.advanceTimersByTime(1000); });
    act(() => { vi.advanceTimersByTime(800); });
    expect(startRacing).toHaveBeenCalledTimes(1);
  });

  it('renders problem card with aria-labeled input when RACING', () => {
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({
        state: 'RACING',
        currentObstacle: 0,
        obstacleClockMs: 1000,
        runners: [
          {
            runnerId: 'player',
            isHuman: true,
            totalDistanceMetres: 0,
            obstaclesCompleted: 0,
            obstacleResults: [],
            finishTime: null,
          },
        ],
        problemSet: { seed: 1, tier: 1 as const, count: 8, problems: Array(8).fill(problem) },
      }),
    );
    renderPage();
    expect(screen.getByText('3 + 4 = ?')).toBeInTheDocument();
    expect(screen.getByRole('spinbutton')).toBeInTheDocument();
  });

  it('calls submitAnswer with isCorrect: true when correct answer submitted', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime.bind(vi) });
    const submitAnswer = vi.fn();
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({
        state: 'RACING',
        currentObstacle: 0,
        obstacleClockMs: 500,
        runners: [
          {
            runnerId: 'player',
            isHuman: true,
            totalDistanceMetres: 0,
            obstaclesCompleted: 0,
            obstacleResults: [],
            finishTime: null,
          },
        ],
        problemSet: { seed: 1, tier: 1 as const, count: 8, problems: Array(8).fill(problem) },
        submitAnswer,
      }),
    );
    renderPage();
    await user.type(screen.getByRole('spinbutton'), '7');
    await user.keyboard('{Enter}');
    expect(submitAnswer).toHaveBeenCalledWith({ isCorrect: true });
  });

  it('navigates to /race/:id/results when engine reaches RESULTS', async () => {
    const summary = {
      race_id: 'r1',
      seed: '42',
      difficulty_tier: 1 as const,
      mode: 'quick' as const,
      started_at: '',
      completed_at: '',
      participants: [],
    };
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({ state: 'RESULTS', getSummary: vi.fn().mockReturnValue(summary) }),
    );
    renderPage();
    await waitFor(() => expect(screen.getByText('Results')).toBeInTheDocument());
  });
});
