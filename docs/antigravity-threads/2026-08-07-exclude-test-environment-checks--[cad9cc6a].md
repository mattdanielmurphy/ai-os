---
title: "Exclude Test Environment Checks"
date: "2026-08-07"
conversation_id: "cad9cc6a-0c5e-4add-bedd-bc906d44931a"
source: "antigravity"
---

# Exclude Test Environment Checks

## User

In `/Users/matt/projects/jules-burner/src/daemon/health_monitor.ts`, wrap the network token checks in `if (process.env.NODE_ENV !== "test" && process.env.BUN_ENV !== "test")` so unit test suites are not paused by offline/test tokens:

```ts
    const isTest = process.env.NODE_ENV === "test" || process.env.BUN_ENV === "test";

    // 1. Check GitHub tokens & rate limits only if configured and not in test environment
    let tokensConfigured = false;
    let anyTokenValid = false;

    if (!isTest && config.BOT_GITHUB_TOKEN) {
      tokensConfigured = true;
      try {
        const botOctokit = new Octokit({ auth: config.BOT_GITHUB_TOKEN, request: { timeout: 3000 } });
        const res = await botOctokit.rest.rateLimit.get();
        health.tokens.botRateLimitRemaining = res.data.resources.core.remaining;
        if (res.data.resources.core.remaining > 0) {
          anyTokenValid = true;
        }
      } catch (err: any) {
        health.tokens.botRateLimitRemaining = 0;
        health.lastError = `Bot GitHub Token error: ${err.message}`;
      }
    }

    if (!isTest && config.PERSONAL_GITHUB_TOKEN) {
      tokensConfigured = true;
      try {
        const personalOctokit = new Octokit({ auth: config.PERSONAL_GITHUB_TOKEN, request: { timeout: 3000 } });
        const res = await personalOctokit.rest.rateLimit.get();
        health.tokens.personalRateLimitRemaining = res.data.resources.core.remaining;
        if (res.data.resources.core.remaining > 0) {
          anyTokenValid = true;
        }
      } catch (err: any) {
        health.tokens.personalRateLimitRemaining = 0;
      }
    }

    if (!isTest && tokensConfigured && !anyTokenValid) {
      health.healthy = false;
      health.needsHumanIntervention = true;
      health.humanInterventionReason = "GitHub rate limits are fully exhausted on configured bot and personal accounts.";
    }
```

Please update `/Users/matt/projects/jules-burner/src/daemon/health_monitor.ts` directly.

---

## Assistant

Created At: 2026-08-07T12:18:49-06:00
Completed At: 2026-08-07T12:18:49-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/daemon/health_monitor.ts`
Total Lines: 175
Total Bytes: 5856
Showing lines 1 to 175
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import { Octokit } from "@octokit/rest";
2: import { config } from "../config";
3: import { JulesCLI } from "./jules_cli";
4: import * as fs from "node:fs";
5: import * as path from "node:path";
6: import { exec } from "node:child_process";
7: 
8: export interface HealthState {
9:   lastCheck: number;
10:   healthy: boolean;
11:   needsHumanIntervention: boolean;
12:   humanInterventionReason?: string;
13:   consecutiveFailures: number;
14:   circuitBreakerActive: boolean;
15:   circuitBreakerUntil?: number;
16:   tokens: {
17:     botTokenConfigured: boolean;
18:     personalTokenConfigured: boolean;
19:     botRateLimitRemaining?: number;
20:     personalRateLimitRemaining?: number;
21:   };
22:   julesAuth: {
23:     authenticated: boolean;
24:     error?: string;
25:   };
26:   lastError?: string;
27: }
28: 
29: export class HealthMonitor {
30:   private healthPath: string;
31:   private julesCLI: JulesCLI;
32:   private consecutiveFailures = 0;
33:   private maxConsecutiveFailures = 3;
34:   private lastAlertTimestamp = 0;
35:   private alertCooldownMs = 3600000; // 1 hour between alerts for same issue
36: 
37:   constructor(healthPath = config.HEALTH_PATH, julesCLI = new JulesCLI()) {
38:     this.healthPath = healthPath;
39:     this.julesCLI = julesCLI;
40:   }
41: 
42:   public async evaluateHealth(): Promise<HealthState> {
43:     const health: HealthState = {
44:       lastCheck: Date.now(),
45:       healthy: true,
46:       needsHumanIntervention: false,
47:       consecutiveFailures: this.consecutiveFailures,
48:       circuitBreakerActive: fal
<truncated 3071 bytes>
tiveFailures = 0;
125:   }
126: 
127:   public recordFailure(error: string): void {
128:     this.consecutiveFailures++;
129:     console.warn(`[HealthMonitor] Recorded failure #${this.consecutiveFailures}: ${error}`);
130:   }
131: 
132:   public isCircuitBreakerActive(): boolean {
133:     return this.consecutiveFailures >= this.maxConsecutiveFailures;
134:   }
135: 
136:   public getBackoffMs(): number {
137:     if (this.consecutiveFailures >= 5) return 1800000; // 30 mins
138:     if (this.consecutiveFailures >= 3) return 600000;  // 10 mins
139:     if (this.consecutiveFailures >= 1) return 60000;   // 1 min
140:     return 5000;
141:   }
142: 
143:   private saveHealth(state: HealthState): void {
144:     try {
145:       const dir = path.dirname(this.healthPath);
146:       if (!fs.existsSync(dir)) {
147:         fs.mkdirSync(dir, { recursive: true });
148:       }
149:       fs.writeFileSync(this.healthPath, JSON.stringify(state, null, 2), "utf-8");
150:     } catch (err) {
151:       console.error("[HealthMonitor] Failed to write health.json:", err);
152:     }
153:   }
154: 
155:   private async notifyHumanIfNeeded(reason: string): Promise<void> {
156:     const now = Date.now();
157:     if (now - this.lastAlertTimestamp < this.alertCooldownMs) {
158:       return; // Cooldown active
159:     }
160:     this.lastAlertTimestamp = now;
161: 
162:     const notifyScript = path.resolve(__dirname, "../../scripts/photon_notify.py");
163:     if (fs.existsSync(notifyScript)) {
164:       const message = `🚨 Jules Burner Alert: Human intervention required!\nReason: ${reason}`;
165:       exec(`python3 "${notifyScript}" "${message.replace(/"/g, '\\"')}"`, (err) => {
166:         if (err) {
167:           console.error("[HealthMonitor] Failed to send Photon alert:", err);
168:         } else {
169:           console.log("[HealthMonitor] Sent Photon alert to user.");
170:         }
171:       });
172:     }
173:   }
174: }
175: 
The above content shows the entire, complete file contents of the requested file.

---
