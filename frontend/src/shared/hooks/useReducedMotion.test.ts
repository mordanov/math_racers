import { act, renderHook } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { useReducedMotion } from './useReducedMotion';

const mkMq = (matches: boolean) => ({
  matches,
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
});

describe('useReducedMotion', () => {
  let matchMediaMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    matchMediaMock = vi.fn().mockReturnValue(mkMq(false));
    Object.defineProperty(window, 'matchMedia', { writable: true, value: matchMediaMock });
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('returns false when media query is false and localStorage is not set', () => {
    const { result } = renderHook(() => useReducedMotion());
    expect(result.current).toBe(false);
  });

  it('returns true when media query matches', () => {
    matchMediaMock.mockReturnValue(mkMq(true));
    const { result } = renderHook(() => useReducedMotion());
    expect(result.current).toBe(true);
  });

  it('returns true when localStorage settings.reducedMotion is "true"', () => {
    localStorage.setItem('settings.reducedMotion', 'true');
    const { result } = renderHook(() => useReducedMotion());
    expect(result.current).toBe(true);
  });

  it('returns false when localStorage settings.reducedMotion is "false"', () => {
    localStorage.setItem('settings.reducedMotion', 'false');
    const { result } = renderHook(() => useReducedMotion());
    expect(result.current).toBe(false);
  });

  it('updates when a storage event fires with the settings key', () => {
    const { result } = renderHook(() => useReducedMotion());
    expect(result.current).toBe(false);

    act(() => {
      localStorage.setItem('settings.reducedMotion', 'true');
      window.dispatchEvent(
        new StorageEvent('storage', {
          key: 'settings.reducedMotion',
          newValue: 'true',
        }),
      );
    });

    expect(result.current).toBe(true);
  });

  it('does not update when an unrelated storage event fires', () => {
    const { result } = renderHook(() => useReducedMotion());

    act(() => {
      window.dispatchEvent(
        new StorageEvent('storage', { key: 'some.other.key', newValue: 'true' }),
      );
    });

    expect(result.current).toBe(false);
  });
});
