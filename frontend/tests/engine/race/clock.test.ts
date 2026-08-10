// @vitest-environment node
import { describe, expect, it } from 'vitest';
import { FRAME_DELTA_CAP_MS } from '../../../src/engine/race/constants';
import { GameClock } from '../../../src/engine/race/clock';

// Ticks at ~60fps (16ms intervals) stay well under the 100ms cap.
// Tests that exercise the cap use a single large jump explicitly.

describe('GameClock — basic accumulation', () => {
  it('starts at 0', () => {
    const clock = new GameClock();
    expect(clock.getMs()).toBe(0);
    expect(clock.getObstacleMs()).toBe(0);
  });

  it('accumulates deltas correctly across multiple ticks', () => {
    const clock = new GameClock();
    clock.tick(0);
    clock.tick(16);   // +16
    clock.tick(32);   // +16
    clock.tick(80);   // +48
    expect(clock.getMs()).toBe(80);
  });

  it('caps a single large delta at FRAME_DELTA_CAP_MS', () => {
    const clock = new GameClock();
    clock.tick(0);
    clock.tick(5000); // huge jump — capped to 100
    expect(clock.getMs()).toBe(FRAME_DELTA_CAP_MS);
  });

  it('does not advance on first tick (no previous timestamp)', () => {
    const clock = new GameClock();
    clock.tick(9999);
    expect(clock.getMs()).toBe(0);
  });
});

describe('GameClock — pause / resume', () => {
  it('does not advance while paused', () => {
    const clock = new GameClock();
    clock.tick(0);
    clock.tick(32);   // +32 → total = 32
    clock.pause();
    clock.tick(48);   // paused — no delta
    clock.tick(64);   // paused — no delta
    expect(clock.getMs()).toBe(32);
  });

  it('resumes accumulating after resume(), excluding hidden duration', () => {
    const clock = new GameClock();
    clock.tick(0);
    clock.tick(50);    // +50 → total = 50
    clock.pause();
    clock.tick(5000);  // hidden duration — not counted
    clock.resume();
    clock.tick(6000);  // first tick after resume — lastTimestamp reset → no delta
    clock.tick(6016);  // +16 → total = 66
    expect(clock.getMs()).toBe(66);
  });
});

describe('GameClock — reset', () => {
  it('resets all state to zero', () => {
    const clock = new GameClock();
    clock.tick(0);
    clock.tick(16);
    clock.reset();
    expect(clock.getMs()).toBe(0);
    expect(clock.getObstacleMs()).toBe(0);
    // After reset, first tick sets lastTimestamp; second tick starts accumulating
    clock.tick(0);
    clock.tick(16);
    expect(clock.getMs()).toBe(16);
  });
});

describe('GameClock — obstacle clock', () => {
  it('advances in parallel with total clock', () => {
    const clock = new GameClock();
    clock.tick(0);
    clock.tick(16);
    clock.tick(48);
    expect(clock.getMs()).toBe(48);
    expect(clock.getObstacleMs()).toBe(48);
  });

  it('resets independently via startObstacleClock()', () => {
    const clock = new GameClock();
    clock.tick(0);
    clock.tick(50);               // total = 50, obstacle = 50
    clock.startObstacleClock();   // obstacle resets to 0
    clock.tick(70);               // total += 20, obstacle += 20
    expect(clock.getMs()).toBe(70);
    expect(clock.getObstacleMs()).toBe(20);
  });

  it('excludes hidden duration from obstacle clock too', () => {
    const clock = new GameClock();
    clock.tick(0);
    clock.tick(30);                // total=30, obstacle=30
    clock.startObstacleClock();    // obstacle resets
    clock.tick(60);                // +30 obstacle → obstacle=30
    clock.pause();
    clock.tick(5000);              // hidden
    clock.resume();
    clock.tick(6000);              // first after resume — no delta
    clock.tick(6020);              // +20 obstacle → obstacle=50
    expect(clock.getObstacleMs()).toBe(50);
  });
});
