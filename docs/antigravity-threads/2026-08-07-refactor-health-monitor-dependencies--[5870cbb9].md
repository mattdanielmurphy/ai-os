---
title: "Refactor Health Monitor Dependencies"
date: "2026-08-07"
conversation_id: "5870cbb9-bf90-4bef-aa07-4bdb9cc10272"
source: "antigravity"
---

# Refactor Health Monitor Dependencies

## User

Please update `/Users/matt/projects/jules-burner/src/daemon/health_monitor.ts` and `/Users/matt/projects/jules-burner/src/daemon/dispatcher.ts` to ensure clean dependency injection for testing and prevent false positive health errors when running unit tests:

1. In `/Users/matt/projects/jules-burner/src/daemon/health_monitor.ts`:
Ensure `evaluateHealth()` gracefully handles test environments where GitHub tokens might not be set in process.env:
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

  constructor(healthPath = config.HEALTH_PATH, julesCLI = new JulesCLI()) {
    this.healthPath = healthPath;
    this.julesCLI = julesCLI;
  }

  public async evaluateHealth(): Promise<HealthState> {
    const health: HealthState = {
      lastCheck: Date.now(),
      healthy: true,
      needsHumanIntervention: false,
      consecutiveFailures: this.consecutiveFailures,
      circuitBreakerActive: false,
      tokens: {
        botTokenConfigured: Boolean(config.BOT_GITHUB_TOKEN),
        personalTokenConfigured: Boolean(config.PERSONAL_GITHUB_TOKEN),
      },
      julesA
<truncated 2721 bytes>
ublic recordFailure(error: string): void {
    this.consecutiveFailures++;
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
      return; // Cooldown active
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

2. In `/Users/matt/projects/jules-burner/src/daemon/dispatcher.ts`:
Ensure `this.healthMonitor = options.healthMonitor ?? new HealthMonitor(config.HEALTH_PATH, this.julesCLI);` so the injected `julesCLI` is used.

Please edit the files cleanly.

---

## Assistant

Created At: 2026-08-07T12:15:16-06:00
Completed At: 2026-08-07T12:15:16-06:00
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

Created At: 2026-08-07T12:15:17-06:00
Completed At: 2026-08-07T12:15:17-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/daemon/dispatcher.ts`
Total Lines: 205
Total Bytes: 6469
Showing lines 1 to 205
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import { Throttler } from "./throttler";
2: import { JulesCLI } from "./jules_cli";
3: import { PromptPackager } from "./prompter";
4: import { Firewall } from "../safety/firewall";
5: import { HealthMonitor } from "./health_monitor";
6: import type { TaskCandidate } from "../discovery/types";
7: import type { Task } from "../types";
8: import { config } from "../config";
9: 
10: export interface DispatcherOptions {
11:   throttler?: Throttler;
12:   julesCLI?: JulesCLI;
13:   prompter?: PromptPackager;
14:   firewall?: Firewall;
15:   healthMonitor?: HealthMonitor;
16:   taskProvider?: () => Promise<TaskCandidate | null>;
17:   stagingOrg?: string;
18:   enableSleep?: boolean;
19: }
20: 
21: export interface DispatchResult {
22:   success: boolean;
23:   taskId: string;
24:   sessionId?: string;
25:   reason?: string;
26:   jitterMs?: number;
27: }
28: 
29: export class Dispatcher {
30:   private throttler: Throttler;
31:   private julesCLI: JulesCLI;
32:   private prompter: PromptPackager;
33:   private firewall: Firewall;
34:   private healthMonitor: HealthMonitor;
35:   private taskProvider?: () => Promise<TaskCandidate | null>;
36:   private stagingOrg: string;
37:   private enableSleep: boolean;
38:   private isRunning: boolean = false;
39: 
40:   constructor(options: DispatcherOptions = {}) {
41:     this.throttler = options.throttler ?? new Throttler();
42:     this.julesCLI = options.julesCLI ?? new JulesCLI();
43:     this.prompter = options.prompter ?? new PromptPackager();
44:     this.firewall = options.firewall ?? new Firewall();
45:     this.healt
<truncated 3830 bytes>
52:       return {
153:         success: false,
154:         taskId: candidate.id,
155:         reason: `Jules CLI invocation failed: ${cliResult.stderr}`,
156:       };
157:     }
158: 
159:     const sessionId = cliResult.sessionId ?? `sess_${Date.now()}_${candidate.id}`;
160: 
161:     // 8. Record dispatch in Throttler, Firewall & Health
162:     this.throttler.recordDispatch(sessionId, candidate.id);
163:     this.firewall.incrementTaskCount();
164:     this.healthMonitor.recordSuccess();
165: 
166:     // 9. Calculate Jitter Delay
167:     const jitterMs = this.throttler.calculateJitterMs();
168: 
169:     return {
170:       success: true,
171:       taskId: candidate.id,
172:       sessionId,
173:       jitterMs,
174:     };
175:   }
176: 
177:   public async startLoop(intervalCheckMs = 5000): Promise<void> {
178:     this.isRunning = true;
179:     while (this.isRunning) {
180:       try {
181:         if (this.throttler.canDispatch() && !this.healthMonitor.isCircuitBreakerActive()) {
182:           const res = await this.runSingleTask();
183:           if (res.success && this.enableSleep && res.jitterMs) {
184:             await new Promise((r) => setTimeout(r, res.jitterMs));
185:           } else {
186:             const backoff = this.healthMonitor.getBackoffMs();
187:             await new Promise((r) => setTimeout(r, Math.max(intervalCheckMs, backoff)));
188:           }
189:         } else {
190:           const backoff = this.healthMonitor.getBackoffMs();
191:           await new Promise((r) => setTimeout(r, Math.max(intervalCheckMs, backoff)));
192:         }
193:       } catch (err: any) {
194:         this.healthMonitor.recordFailure(err?.message || String(err));
195:         const backoff = this.healthMonitor.getBackoffMs();
196:         await new Promise((r) => setTimeout(r, backoff));
197:       }
198:     }
199:   }
200: 
201:   public stopLoop(): void {
202:     this.isRunning = false;
203:   }
204: }
205: 
The above content shows the entire, complete file contents of the requested file.

---
