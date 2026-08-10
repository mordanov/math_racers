import { FRAME_DELTA_CAP_MS } from './constants';

export class GameClock {
  private totalMs = 0;
  private obstacleMs = 0;
  private paused = false;
  private lastTimestamp: number | null = null;

  tick(timestamp: number): void {
    if (this.paused) {
      this.lastTimestamp = timestamp;
      return;
    }
    if (this.lastTimestamp !== null) {
      const delta = Math.min(timestamp - this.lastTimestamp, FRAME_DELTA_CAP_MS);
      this.totalMs += delta;
      this.obstacleMs += delta;
    }
    this.lastTimestamp = timestamp;
  }

  startObstacleClock(): void {
    this.obstacleMs = 0;
  }

  getMs(): number {
    return this.totalMs;
  }

  getObstacleMs(): number {
    return this.obstacleMs;
  }

  pause(): void {
    this.paused = true;
  }

  resume(): void {
    this.paused = false;
    this.lastTimestamp = null;
  }

  reset(): void {
    this.totalMs = 0;
    this.obstacleMs = 0;
    this.paused = false;
    this.lastTimestamp = null;
  }
}
