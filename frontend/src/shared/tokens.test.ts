import { describe, expect, it } from 'vitest';
import tokens from './tokens';

function luminance(color: string): number {
  const channels = color.match(/[A-Fa-f0-9]{2}/g);
  if (!channels || channels.length !== 3) {
    throw new Error(`Expected a six-digit hex color, received ${color}`);
  }

  const [red, green, blue] = channels.map((channel) => {
    const value = parseInt(channel, 16) / 255;
    return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
  });

  return 0.2126 * red + 0.7152 * green + 0.0722 * blue;
}

function contrastRatio(foreground: string, background: string): number {
  const values = [luminance(foreground), luminance(background)].sort((a, b) => b - a);
  return (values[0] + 0.05) / (values[1] + 0.05);
}

describe('accessible color tokens', () => {
  it.each([
    ['primary', tokens.color.primary],
    ['primary hover', tokens.color.primaryHover],
    ['primary active', tokens.color.primaryActive],
  ])('%s supports AA contrast with primary button text', (_name, background) => {
    expect(contrastRatio(tokens.color.textOnPrimary, background)).toBeGreaterThanOrEqual(4.5);
  });

  it('keeps focus indicators distinguishable from light surfaces', () => {
    expect(contrastRatio(tokens.color.focus, tokens.color.surface)).toBeGreaterThanOrEqual(3);
    expect(contrastRatio(tokens.color.focus, tokens.color.background)).toBeGreaterThanOrEqual(3);
  });

  it('keeps control borders distinguishable from their surface', () => {
    expect(contrastRatio(tokens.color.border, tokens.color.surface)).toBeGreaterThanOrEqual(3);
  });
});
