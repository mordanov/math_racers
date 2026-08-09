export type Operation = 'addition' | 'subtraction' | 'multiplication' | 'division';

export type Tier = 1 | 2 | 3 | 4 | 5 | 6;

export interface TierConfig {
  tier: Tier;
  operations: Operation[];
  minOperand: number;
  maxOperand: number;
}

export interface Problem {
  id: string;
  operation: Operation;
  operand_a: number;
  operand_b: number;
  answer: number;
  tier: Tier;
  seed: number;
}

export interface ProblemSet {
  seed: number;
  tier: Tier;
  count: number;
  problems: Problem[];
}

export interface ValidationResult {
  correct: boolean;
  reason?: 'not_a_number';
  elapsedMs: number;
}

export interface TierSelectionInput {
  currentTier: Tier;
  skillScore: number;
  parentOverride?: number;
}
