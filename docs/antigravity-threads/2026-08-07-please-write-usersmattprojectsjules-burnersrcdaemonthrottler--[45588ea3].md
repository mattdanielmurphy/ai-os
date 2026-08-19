---
title: "Please write `/Users/matt/projects/jules-burner/src/daemon/throttler.ts` using `write_to_file` with Overwrite: true."
date: "2026-08-07"
conversation_id: "45588ea3-17e0-4dfc-b292-3098d2c63283"
source: "antigravity"
---

# Please write `/Users/matt/projects/jules-burner/src/daemon/throttler.ts` using `write_to_file` with Overwrite: true.

## User

Please write `/Users/matt/projects/jules-burner/src/daemon/throttler.ts` using `write_to_file` with Overwrite: true.

Here is the exact TypeScript code:

```ts
import { config } from "../config";
import * as fs from "node:fs";
import * as path from "node:path";

export interface DispatchRecord {
  timestamp: number;
  sessionId?: string;
  taskId?: string;
}

export interface ThrottlerState {
  dispatches: DispatchRecord[];
}

export interface ThrottlerOptions {
  stateFilePath?: string;
  dailyLimit?: number;
  minJitterSeconds?: number;
  maxJitterSeconds?: number;
}

export class Throttler {
  private stateFilePath: string;
  private dailyLimit: number;
  private minJitterSeconds: number;
  private maxJitterSeconds: number;
  private state: ThrottlerState;

  constructor(options: ThrottlerOptions = {}) {
    this.stateFilePath = options.stateFilePath ?? "data/state.json";
    this.dailyLimit = options.dailyLimit ?? config.DAILY_TASK_LIMIT;
    this.minJitterSeconds = options.minJitterSeconds ?? config.MIN_JITTER_SECONDS;
    this.maxJitterSeconds = options.maxJitterSeconds ?? config.MAX_JITTER_SECONDS;
    this.state = this.loadState();
  }

  private loadState(): ThrottlerState {
    try {
      if (fs.existsSync(this.stateFilePath)) {
        const content = fs.readFileSync(this.stateFilePath, "utf-8");
        const parsed = JSON.parse(content);
        if (parsed && Array.isArray(parsed.dispatches)) {
          return parsed;
        }
      }
    } catch {
      // Fallback on read failure
    }
    return { dispatches: [] };
  }

  private saveState(): void {
    try {
      const dir = path.dirname(this.stateFilePath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(this.stateFilePath, JSON.stringify(this.state, null, 2), "utf-8");
    } catch (err) {
      console.error(`Failed to save throttler state to ${this.stateFilePath}:`, err);
    }
  }

  private getRecentDispatches(): DispatchRecord[] {
    const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000;
    return this.state.dispatches.filter((d) => d.timestamp >= oneDayAgo);
  }

  public canDispatch(): boolean {
    const recent = this.getRecentDispatches();
    return recent.length < this.dailyLimit;
  }

  public getDispatchedCount(): number {
    return this.getRecentDispatches().length;
  }

  public getRemainingQuota(): number {
    const count = this.getDispatchedCount();
    return Math.max(0, this.dailyLimit - count);
  }

  public recordDispatch(sessionId?: string, taskId?: string): void {
    const record: DispatchRecord = {
      timestamp: Date.now(),
      sessionId,
      taskId,
    };
    this.state.dispatches.push(record);
    this.saveState();
  }

  public calculateJitterMs(): number {
    const minMs = this.minJitterSeconds * 1000;
    const maxMs = this.maxJitterSeconds * 1000;
    return Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs;
  }
}
```

---
