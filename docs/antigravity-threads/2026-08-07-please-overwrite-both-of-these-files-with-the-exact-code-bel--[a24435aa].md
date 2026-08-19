---
title: "Please overwrite BOTH of these files with the exact code below using write_to_file (Overwrite: true):"
date: "2026-08-07"
conversation_id: "a24435aa-219d-4fef-9046-022f45cebda9"
source: "antigravity"
---

# Please overwrite BOTH of these files with the exact code below using write_to_file (Overwrite: true):

## User

Please overwrite BOTH of these files with the exact code below using write_to_file (Overwrite: true):
1. `/Users/matt/projects/jules-burner/src/daemon/health_monitor.ts`
2. `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/src/daemon/health_monitor.ts`

Here is the exact TypeScript code:

```ts
import { Octokit } from "@octokit/rest";
import { config } from "../config";
import { JulesCLI } from "./jules_cli";
import * as fs from "node:fs";
import * as path from "node:path";
import { exec } from "node:child_process";

export interface HealthState {
  lastCheck: number;
  healthy: boolean;
  needsHumanIntervention: boolean;
  humanInterventionReason?: string;
  consecutiveFailures: number;
  circuitBreakerActive: boolean;
  circuitBreakerUntil?: number;
  tokens: {
    botTokenConfigured: boolean;
    personalTokenConfigured: boolean;
    botRateLimitRemaining?: number;
    personalRateLimitRemaining?: number;
  };
  julesAuth: {
    authenticated: boolean;
    error?: string;
  };
  lastError?: string;
}

export class HealthMonitor {
  private healthPath: string;
  private julesCLI: JulesCLI;
  private consecutiveFailures = 0;
  private maxConsecutiveFailures = 3;
  private lastAlertTimestamp = 0;
  private alertCooldownMs = 3600000; // 1 hour between alerts for same issue
  private cachedHealth?: HealthState;
  private cacheTtlMs = 60000; // 60s cache

  constructor(healthPath = config.HEALTH_PATH, julesCLI = new JulesCLI()) {
    this.healthPath = healthPath;
    this.julesCLI = julesCLI;
  }

  public async evaluateHealth(force = false): Promise<HealthState> {
    const now = Date.now();
    if (!force && this.cachedHealth && now - this.cachedHealth.lastCheck < this.cacheTtlMs) {
      return this.cachedHealth;
    }

    const health: HealthState = {
      lastCheck: now,
      healthy: true,
      needsHumanIntervention: false,
      consecutiveFailures: this.consecutiveFailures,
      circuitBreakerActive: this.consecutiveFailures >= this.maxConsecutiveFailures,
  
<truncated 3350 bytes>
    this.consecutiveFailures++;
    if (this.cachedHealth) {
      this.cachedHealth.consecutiveFailures = this.consecutiveFailures;
      if (this.consecutiveFailures >= this.maxConsecutiveFailures) {
        this.cachedHealth.circuitBreakerActive = true;
        this.cachedHealth.healthy = false;
      }
    }
    console.warn(`[HealthMonitor] Recorded failure #${this.consecutiveFailures}: ${error}`);
  }

  public isCircuitBreakerActive(): boolean {
    return this.consecutiveFailures >= this.maxConsecutiveFailures;
  }

  public getBackoffMs(): number {
    if (this.consecutiveFailures >= 5) return 1800000; // 30 mins
    if (this.consecutiveFailures >= 3) return 600000;  // 10 mins
    if (this.consecutiveFailures >= 1) return 60000;   // 1 min
    return 5000;
  }

  private saveHealth(state: HealthState): void {
    try {
      const dir = path.dirname(this.healthPath);
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(this.healthPath, JSON.stringify(state, null, 2), "utf-8");
    } catch (err) {
      console.error("[HealthMonitor] Failed to write health.json:", err);
    }
  }

  private async notifyHumanIfNeeded(reason: string): Promise<void> {
    const now = Date.now();
    if (now - this.lastAlertTimestamp < this.alertCooldownMs) {
      return;
    }
    this.lastAlertTimestamp = now;

    const notifyScript = path.resolve(__dirname, "../../scripts/photon_notify.py");
    if (fs.existsSync(notifyScript)) {
      const message = `🚨 Jules Burner Alert: Human intervention required!\nReason: ${reason}`;
      exec(`python3 "${notifyScript}" "${message.replace(/"/g, '\\"')}"`, (err) => {
        if (err) {
          console.error("[HealthMonitor] Failed to send Photon alert:", err);
        } else {
          console.log("[HealthMonitor] Sent Photon alert to user.");
        }
      });
    }
  }
}
```

Write to both files now.

---
