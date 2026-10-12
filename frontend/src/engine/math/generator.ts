import { createRng } from './rng';
import { supportsDivisionRange, TIER_CONFIGS } from './tiers';
import type { Operation, Problem, ProblemSet, Tier, TierConfig } from './types';

const MAX_RETRIES = 10;

function randomInt(rng: () => number, min: number, max: number): number {
  return Math.floor(rng() * (max - min + 1)) + min;
}

function pickOperation(config: TierConfig, rng: () => number): Operation {
  const ops = config.operations;
  return ops[Math.floor(rng() * ops.length)];
}

function pickOperands(
  operation: Operation,
  config: TierConfig,
  rng: () => number,
): [number, number] {
  const { minOperand, maxOperand } = config;
  if (operation === 'division') {
    const minDivisor = Math.max(2, minOperand);
    const maxDivisor =
      config.tier === 4 || config.tier === 5
        ? Math.min(9, Math.floor(maxOperand / 2))
        : Math.floor(maxOperand / 2);
    const b = randomInt(rng, minDivisor, maxDivisor);
    const a = b * randomInt(rng, 2, Math.floor(maxOperand / b));
    return [a, b];
  }
  if (operation === 'subtraction') {
    const a = randomInt(rng, minOperand, maxOperand);
    const b = randomInt(rng, minOperand, a);
    return [a, b];
  }
  if (operation === 'addition' && config.tier === 5) {
    return [randomInt(rng, 10, 99), randomInt(rng, 10, 99)];
  }
  if (operation === 'multiplication' && (config.tier === 3 || config.tier === 5)) {
    return [randomInt(rng, 10, 99), randomInt(rng, 1, 9)];
  }
  return [randomInt(rng, minOperand, maxOperand), randomInt(rng, minOperand, maxOperand)];
}

function compute(operation: Operation, a: number, b: number): number {
  switch (operation) {
    case 'addition':
      return a + b;
    case 'subtraction':
      return a - b;
    case 'multiplication':
      return a * b;
    case 'division':
      return a / b;
  }
}

function isDuplicate(candidate: Problem, last: Problem | null): boolean {
  if (last === null) return false;
  return (
    candidate.operation === last.operation &&
    candidate.operand_a === last.operand_a &&
    candidate.operand_b === last.operand_b
  );
}

export function generateProblemSet(
  tier: Tier,
  seed: number,
  count: number,
  customTierConfig?: TierConfig,
): ProblemSet {
  let config: TierConfig;
  if (tier === 6) {
    if (customTierConfig === undefined) {
      throw new Error('Tier 6 requires parent-configured settings.');
    }
    config = customTierConfig;
  } else {
    config = TIER_CONFIGS[tier];
  }
  if (
    config.operations.includes('division') &&
    !supportsDivisionRange(config.minOperand, config.maxOperand)
  ) {
    throw new Error('The operand range cannot generate a division quotient above one.');
  }

  const rng = createRng(seed);
  const problems: Problem[] = [];
  let last: Problem | null = null;

  while (problems.length < count) {
    let problem: Problem | null = null;
    for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
      const operation = pickOperation(config, rng);
      const [a, b] = pickOperands(operation, config, rng);
      const answer = compute(operation, a, b);
      const candidate: Problem = {
        id: crypto.randomUUID(),
        operation,
        operand_a: a,
        operand_b: b,
        answer,
        tier,
        seed,
      };
      if (!isDuplicate(candidate, last) || attempt === MAX_RETRIES) {
        problem = candidate;
        break;
      }
    }
    problems.push(problem!);
    last = problem;
  }

  return { seed, tier, count, problems };
}
