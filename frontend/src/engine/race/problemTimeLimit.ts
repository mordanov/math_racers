export const DEFAULT_PROBLEM_TIME_LIMIT_SECONDS = 30;
export const MIN_PROBLEM_TIME_LIMIT_SECONDS = 10;
export const MAX_PROBLEM_TIME_LIMIT_SECONDS = 60;
export const PROBLEM_TIME_LIMIT_STEP_SECONDS = 5;

export function isValidProblemTimeLimitSeconds(value: number): boolean {
  return (
    Number.isInteger(value) &&
    value >= MIN_PROBLEM_TIME_LIMIT_SECONDS &&
    value <= MAX_PROBLEM_TIME_LIMIT_SECONDS &&
    value % PROBLEM_TIME_LIMIT_STEP_SECONDS === 0
  );
}

export function readProblemTimeLimitSeconds(): number {
  try {
    const stored = localStorage.getItem('settings.problemTimeLimitSeconds');
    if (stored === null) return DEFAULT_PROBLEM_TIME_LIMIT_SECONDS;
    const value = Number(stored);
    return isValidProblemTimeLimitSeconds(value) ? value : DEFAULT_PROBLEM_TIME_LIMIT_SECONDS;
  } catch {
    return DEFAULT_PROBLEM_TIME_LIMIT_SECONDS;
  }
}
