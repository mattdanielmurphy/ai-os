---
title: "Update the following files:"
date: "2026-08-08"
conversation_id: "4ffa8129-7e73-47eb-9f28-b5536762d77d"
source: "antigravity"
---

# Update the following files:

## User

Update the following files:

1. TargetFile: `/Users/matt/projects/jules-burner/src/daemon/dispatcher.ts`
Overwrite: true
CodeContent:
```ts
import { Throttler } from "./throttler";
import { JulesCLI } from "./jules_cli";
import { PromptPackager } from "./prompter";
import { Firewall } from "../safety/firewall";
import { HealthMonitor } from "./health_monitor";
import { config } from "../config";
import type { TaskCandidate } from "../discovery/types";
import type { Task } from "../types";

export interface DispatchResult {
  success: boolean;
  taskId: string;
  sessionId?: string;
  reason?: string;
  jitterMs?: number;
}

export interface DispatcherOptions {
  throttler?: Throttler;
  julesCLI?: JulesCLI;
  prompter?: PromptPackager;
  firewall?: Firewall;
  healthMonitor?: HealthMonitor;
  stagingOrg?: string;
  taskProvider?: () => Promise<TaskCandidate | null>;
  enableSleep?: boolean;
}

export class Dispatcher {
  private throttler: Throttler;
  private julesCLI: JulesCLI;
  private prompter: PromptPackager;
  private firewall: Firewall;
  private healthMonitor: HealthMonitor;
  private stagingOrg: string;
  private taskProvider?: () => Promise<TaskCandidate | null>;
  private enableSleep: boolean;
  private isRunning = false;

  constructor(options: DispatcherOptions = {}) {
    this.throttler = options.throttler ?? new Throttler();
    this.julesCLI = options.julesCLI ?? new JulesCLI();
    this.prompter = options.prompter ?? new PromptPackager();
    this.firewall = options.firewall ?? new Firewall(this.throttler.getDispatchedCount());
    this.healthMonitor = options.healthMonitor ?? new HealthMonitor(config.HEALTH_PATH, this.julesCLI);
    this.stagingOrg = options.stagingOrg ?? config.STAGING_ORG_OR_USER;
    this.taskProvider = options.taskProvider;
    this.enableSleep = options.enableSleep ?? true;
  }

  public getFirewall(): Firewall {
    return this.firewall;
  }

  public prepareStagingFork(candidate: TaskCandidate): string {
    if (candidate.targetRepo) {
      return candida
<truncated 4853 bytes>
!task.targetRepository.includes("jules-burner")) {
      return { safe: false, reason: "Fork Isolation Guard violation: target repository is not an allowed repo." };
    }

    return { safe: true };
  }

  public incrementTaskCount(): void {
    this.dailyTaskCount++;
  }
}
```

3. TargetFile: `/Users/matt/projects/jules-burner/src/discovery/pipelines/self_tasks.ts`
Overwrite: true
CodeContent:
```ts
import type { TaskCandidate } from "../types";

export class SelfTasksPipeline {
  private tasks: TaskCandidate[] = [
    {
      id: "st-health-tests",
      source: "self_tasks",
      title: "Add unit tests for health monitor rate limit parsing",
      description: "Implement comprehensive unit tests for HealthMonitor rate limit parsing and cooldown timers.",
      url: "internal://health-monitor-tests",
      complexity: "low",
    },
    {
      id: "st-openapi-docs",
      source: "self_tasks",
      title: "Document OpenAPI telemetry schema",
      description: "Add detailed field descriptions and example payloads to OpenAPI audit telemetry spec.",
      url: "internal://openapi-docs",
      complexity: "low",
    },
    {
      id: "st-friction-pattern-detector",
      source: "self_tasks",
      title: "Add automated friction pattern detector",
      description: "Build pattern matching to group repeated build errors and log them into friction tables.",
      url: "internal://friction-patterns",
      complexity: "low",
    },
    {
      id: "st-status-badge",
      source: "self_tasks",
      title: "Add status badge to README",
      description: "Add a clean markdown status badge for Jules Burner CI and operational health.",
      url: "internal://status-badge",
      complexity: "low",
    },
  ];

  private currentIndex = 0;

  async fetch(): Promise<TaskCandidate[]> {
    const task = this.tasks[this.currentIndex % this.tasks.length];
    this.currentIndex++;
    return [task];
  }
}
```

---
