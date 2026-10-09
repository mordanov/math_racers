import { render, screen, act, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import RaceScreenPage from './RaceScreenPage';
import * as useRaceEngineModule from '../engine/race/hooks/useRaceEngine';
import * as reduceMotionModule from '../shared/hooks/useReducedMotion';
import * as sfxModule from '../shared/hooks/useSfxPlayer';
import * as ambienceModule from '../shared/hooks/useAmbienceManager';
import * as voiceModule from '../shared/hooks/useVoicePlayer';
import type { RaceEngineState } from '../engine/race/types';

vi.mock('../shared/hooks/useReducedMotion');
vi.mock('../shared/hooks/useSfxPlayer');
vi.mock('../shared/hooks/useAmbienceManager');
vi.mock('../shared/hooks/useVoicePlayer');

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
  avatarSpecies: 'bear',
  opponentCount: 1,
  raceIndex: 0,
};

// Default sfx/ambience/voice mocks — override per test as needed
beforeEach(() => {
  vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx: vi.fn() });
  vi.mocked(ambienceModule.useAmbienceManager).mockReturnValue({ triggerAmbience: vi.fn() });
  vi.mocked(voiceModule.useVoicePlayer).mockReturnValue({ playVoice: vi.fn() });
});

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
    vi.mocked(reduceMotionModule.useReducedMotion).mockReturnValue(false);
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
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({ startCountdown }),
    );
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
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(screen.getByRole('status')).toHaveTextContent('2');
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(screen.getByRole('status')).toHaveTextContent('1');
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(screen.getByRole('status')).toHaveTextContent('GO!');
  });

  it('calls startRacing after GO! delay', () => {
    const startRacing = vi.fn();
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({ state: 'COUNTDOWN', startRacing }),
    );
    renderPage();
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    act(() => {
      vi.advanceTimersByTime(800);
    });
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
        problemSet: {
          seed: 1,
          tier: 1 as const,
          count: 8,
          problems: Array.from({ length: 8 }, () => problem),
        },
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
        problemSet: {
          seed: 1,
          tier: 1 as const,
          count: 8,
          problems: Array.from({ length: 8 }, () => problem),
        },
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

describe('RaceScreenPage — reduced motion', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
  });
  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  const racingState = makeEngineReturn({
    state: 'RACING',
    currentObstacle: 0,
    obstacleClockMs: 5000,
    runners: [
      {
        runnerId: 'player',
        isHuman: true,
        totalDistanceMetres: 42,
        obstaclesCompleted: 0,
        obstacleResults: [],
        finishTime: null,
      },
      {
        runnerId: 'ai-1',
        isHuman: false,
        totalDistanceMetres: 30,
        obstaclesCompleted: 0,
        obstacleResults: [],
        finishTime: null,
      },
    ],
    problemSet: {
      seed: 1,
      tier: 1 as const,
      count: 8,
      problems: Array.from({ length: 8 }, () => problem),
    },
  });

  it('runner row has accessible aria-label combining identity and distance', () => {
    vi.mocked(reduceMotionModule.useReducedMotion).mockReturnValue(false);
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(racingState);
    renderPage();
    expect(screen.getByRole('listitem', { name: 'You: 42m' })).toBeInTheDocument();
    expect(screen.getByRole('listitem', { name: 'CPU 1: 30m' })).toBeInTheDocument();
  });

  it('runner dot has no transition when useReducedMotion is true', () => {
    vi.mocked(reduceMotionModule.useReducedMotion).mockReturnValue(true);
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(racingState);
    const { container } = renderPage();
    const track = container.querySelector('[aria-label="Race track"]');
    const absoluteDots =
      track?.querySelectorAll<HTMLElement>('[style*="position: absolute"]') ?? [];
    expect(absoluteDots.length).toBeGreaterThan(0);
    absoluteDots.forEach((dot) => {
      expect(dot.style.transition).toBe('');
    });
  });

  it('runner dot has transition when useReducedMotion is false', () => {
    vi.mocked(reduceMotionModule.useReducedMotion).mockReturnValue(false);
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(racingState);
    const { container } = renderPage();
    const track = container.querySelector('[aria-label="Race track"]');
    const absoluteDots =
      track?.querySelectorAll<HTMLElement>('[style*="position: absolute"]') ?? [];
    expect(absoluteDots.length).toBeGreaterThan(0);
    const hasTransition = Array.from(absoluteDots).some((dot) => dot.style.transition !== '');
    expect(hasTransition).toBe(true);
  });

  it('timer bar has no transition when useReducedMotion is true', () => {
    vi.mocked(reduceMotionModule.useReducedMotion).mockReturnValue(true);
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(racingState);
    const { container } = renderPage();
    // The timer bar inner div has height:'100%' and a width percentage — it's the only div with height:'100%'
    const timerFill = container.querySelector<HTMLElement>('[style*="height: 100%"]');
    expect(timerFill).not.toBeNull();
    expect(timerFill!.style.transition).toBe('');
  });

  it('timer bar has transition when useReducedMotion is false', () => {
    vi.mocked(reduceMotionModule.useReducedMotion).mockReturnValue(false);
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(racingState);
    const { container } = renderPage();
    const timerFill = container.querySelector<HTMLElement>('[style*="height: 100%"]');
    expect(timerFill).not.toBeNull();
    expect(timerFill!.style.transition).toBe('width 0.1s linear');
  });
});

describe('RaceScreenPage — audio', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(makeEngineReturn());
    vi.mocked(reduceMotionModule.useReducedMotion).mockReturnValue(false);
  });
  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  it('plays countdown sfx on each countdown tick', () => {
    const playSfx = vi.fn();
    vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({ state: 'COUNTDOWN' }),
    );
    renderPage();
    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(playSfx).toHaveBeenCalledWith('countdown');
  });

  it('plays correct sfx on correct answer', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime.bind(vi) });
    const playSfx = vi.fn();
    vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({
        state: 'RACING',
        currentObstacle: 0,
        obstacleClockMs: 5000,
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
        problemSet: {
          seed: 1,
          tier: 1 as const,
          count: 8,
          problems: Array.from({ length: 8 }, () => problem),
        },
      }),
    );
    renderPage();
    await user.type(screen.getByRole('spinbutton'), '7');
    await user.keyboard('{Enter}');
    expect(playSfx).toHaveBeenCalledWith('correct');
  });

  it('plays incorrect sfx on wrong answer', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime.bind(vi) });
    const playSfx = vi.fn();
    vi.mocked(sfxModule.useSfxPlayer).mockReturnValue({ playSfx });
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({
        state: 'RACING',
        currentObstacle: 0,
        obstacleClockMs: 5000,
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
        problemSet: {
          seed: 1,
          tier: 1 as const,
          count: 8,
          problems: Array.from({ length: 8 }, () => problem),
        },
      }),
    );
    renderPage();
    await user.type(screen.getByRole('spinbutton'), '5');
    await user.keyboard('{Enter}');
    expect(playSfx).toHaveBeenCalledWith('incorrect');
  });

  it('triggers cheer ambience on correct answer', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime.bind(vi) });
    const triggerAmbience = vi.fn();
    vi.mocked(ambienceModule.useAmbienceManager).mockReturnValue({ triggerAmbience });
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({
        state: 'RACING',
        currentObstacle: 0,
        obstacleClockMs: 5000,
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
        problemSet: {
          seed: 1,
          tier: 1 as const,
          count: 8,
          problems: Array.from({ length: 8 }, () => problem),
        },
      }),
    );
    renderPage();
    await user.type(screen.getByRole('spinbutton'), '7');
    await user.keyboard('{Enter}');
    expect(triggerAmbience).toHaveBeenCalledWith('cheer');
  });

  it('triggers applause ambience when engine transitions to RESULTS', async () => {
    const triggerAmbience = vi.fn();
    vi.mocked(ambienceModule.useAmbienceManager).mockReturnValue({ triggerAmbience });
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
    await waitFor(() => expect(triggerAmbience).toHaveBeenCalledWith('applause'));
  });

  it('plays thinking voice when new obstacle appears while RACING', () => {
    const playVoice = vi.fn();
    vi.mocked(voiceModule.useVoicePlayer).mockReturnValue({ playVoice });
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({
        state: 'RACING',
        currentObstacle: 0,
        obstacleClockMs: 5000,
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
        problemSet: {
          seed: 1,
          tier: 1 as const,
          count: 8,
          problems: Array.from({ length: 8 }, () => problem),
        },
      }),
    );
    renderPage();
    expect(playVoice).toHaveBeenCalledWith('thinking');
  });

  it('plays happy voice on correct answer', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime.bind(vi) });
    const playVoice = vi.fn();
    vi.mocked(voiceModule.useVoicePlayer).mockReturnValue({ playVoice });
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({
        state: 'RACING',
        currentObstacle: 0,
        obstacleClockMs: 5000,
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
        problemSet: {
          seed: 1,
          tier: 1 as const,
          count: 8,
          problems: Array.from({ length: 8 }, () => problem),
        },
      }),
    );
    renderPage();
    await user.type(screen.getByRole('spinbutton'), '7');
    await user.keyboard('{Enter}');
    expect(playVoice).toHaveBeenCalledWith('happy');
  });

  it('plays surprised voice on wrong answer', async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime.bind(vi) });
    const playVoice = vi.fn();
    vi.mocked(voiceModule.useVoicePlayer).mockReturnValue({ playVoice });
    vi.mocked(useRaceEngineModule.useRaceEngine).mockReturnValue(
      makeEngineReturn({
        state: 'RACING',
        currentObstacle: 0,
        obstacleClockMs: 5000,
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
        problemSet: {
          seed: 1,
          tier: 1 as const,
          count: 8,
          problems: Array.from({ length: 8 }, () => problem),
        },
      }),
    );
    renderPage();
    await user.type(screen.getByRole('spinbutton'), '5');
    await user.keyboard('{Enter}');
    expect(playVoice).toHaveBeenCalledWith('surprised');
  });
});
