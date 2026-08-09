import type { Problem, ValidationResult } from './types';

export function validateAnswer(problem: Problem, playerInput: string, renderTime: number): ValidationResult {
  const elapsedMs = Date.now() - renderTime;
  const parsed = parseInt(playerInput.trim(), 10);
  if (isNaN(parsed)) {
    return { correct: false, reason: 'not_a_number', elapsedMs };
  }
  return { correct: parsed === problem.answer, elapsedMs };
}
