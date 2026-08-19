---
title: "Refactor Staging Fork Logic"
date: "2026-08-08"
conversation_id: "8925a696-6116-4701-8a57-a50ec5de799d"
source: "antigravity"
---

# Refactor Staging Fork Logic

## User

Update `/Users/matt/projects/jules-burner/src/daemon/dispatcher.ts` to ensure `prepareStagingFork` properly creates a staging repo name that satisfies firewall staging isolation:

```typescript
  public prepareStagingFork(candidate: TaskCandidate): string {
    const safeRepoName = candidate.targetRepo
      ? candidate.targetRepo.split("/").pop() || candidate.id
      : candidate.id.replace(/[^a-zA-Z0-9_\-]/g, "_");
    if (safeRepoName.startsWith("staging-")) {
      return `${this.stagingOrg}/${safeRepoName}`;
    }
    return `${this.stagingOrg}/staging-${safeRepoName}`;
  }
```

Use replace_file_content or write_to_file directly. Ensure cleanly formatted code.

---

## Assistant

Created At: 2026-08-08T13:49:01-06:00
Completed At: 2026-08-08T13:49:01-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/daemon/dispatcher.ts`
Total Lines: 187
Total Bytes: 5699
Showing lines 1 to 187
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import { Throttler } from "./throttler";
2: import { JulesCLI } from "./jules_cli";
3: import { PromptPackager } from "./prompter";
4: import { Firewall } from "../safety/firewall";
5: import { SystemTuner } from "../self_improve/tuner";
6: import type { TaskCandidate } from "../discovery/types";
7: import type { Task } from "../types";
8: import { config } from "../config";
9: 
10: export interface DispatcherOptions {
11:   throttler?: Throttler;
12:   julesCLI?: JulesCLI;
13:   prompter?: PromptPackager;
14:   firewall?: Firewall;
15:   tuner?: SystemTuner;
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
34:   private tuner: SystemTuner;
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
45:     this.tuner = options.tuner 
<truncated 2970 bytes>
ason: `Jules CLI invocation failed: ${cliResult.stderr}`,
129:       };
130:     }
131: 
132:     const sessionId = cliResult.sessionId ?? `sess_${Date.now()}_${candidate.id}`;
133: 
134:     // 7. Record dispatch in Throttler & Firewall
135:     this.throttler.recordDispatch(sessionId, candidate.id);
136:     this.firewall.incrementTaskCount();
137: 
138:     // 8. Calculate Jitter Delay
139:     const jitterMs = this.throttler.calculateJitterMs();
140: 
141:     return {
142:       success: true,
143:       taskId: candidate.id,
144:       sessionId,
145:       jitterMs,
146:     };
147:   }
148: 
149:   public async runBatch(count: number, candidateFactory?: (index: number) => TaskCandidate): Promise<DispatchResult[]> {
150:     const results: DispatchResult[] = [];
151:     for (let i = 0; i < count; i++) {
152:       const candidate = candidateFactory ? candidateFactory(i) : undefined;
153:       const res = await this.runSingleTask(candidate);
154:       results.push(res);
155: 
156:       if (!res.success) {
157:         break;
158:       }
159: 
160:       if (this.enableSleep && res.jitterMs && i < count - 1) {
161:         await new Promise(r => setTimeout(r, res.jitterMs));
162:       }
163:     }
164:     return results;
165:   }
166: 
167:   public async startLoop(intervalCheckMs = 10000): Promise<void> {
168:     this.isRunning = true;
169:     while (this.isRunning) {
170:       if (this.throttler.canDispatch()) {
171:         const res = await this.runSingleTask();
172:         if (res.success && this.enableSleep && res.jitterMs) {
173:           await new Promise(r => setTimeout(r, res.jitterMs));
174:         } else {
175:           await new Promise(r => setTimeout(r, intervalCheckMs));
176:         }
177:       } else {
178:         await new Promise(r => setTimeout(r, intervalCheckMs));
179:       }
180:     }
181:   }
182: 
183:   public stopLoop(): void {
184:     this.isRunning = false;
185:   }
186: }
187: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-08T13:49:03-06:00
Completed At: 2026-08-08T13:49:03-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/jules-burner/src/daemon/dispatcher.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -61,13 +61,13 @@
   }
 
   public prepareStagingFork(candidate: TaskCandidate): string {
-    // If targetRepo is an external repo, use user's fork
-    if (candidate.targetRepo && !candidate.targetRepo.startsWith(`${this.stagingOrg}/`)) {
-      const parts = candidate.targetRepo.split("/");
-      const repoName = parts[parts.length - 1];
-      return `${this.stagingOrg}/${repoName}`;
-    }
-    return candidate.targetRepo || `${this.stagingOrg}/jules-burner`;
+    const safeRepoName = candidate.targetRepo
+      ? candidate.targetRepo.split("/").pop() || candidate.id
+      : candidate.id.replace(/[^a-zA-Z0-9_\-]/g, "_");
+    if (safeRepoName.startsWith("staging-")) {
+      return `${this.stagingOrg}/${safeRepoName}`;
+    }
+    return `${this.stagingOrg}/staging-${safeRepoName}`;
   }
 
   public async runSingleTask(taskCandidate?: TaskCandidate): Promise<DispatchResult> {
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T13:49:04-06:00
Completed At: 2026-08-08T13:49:04-06:00
Message sent to "bef3c6ef-d5d2-4d21-b2f6-a0ce12a497ac".

I have updated `/Users/matt/projects/jules-burner/src/daemon/dispatcher.ts` with the requested `prepareStagingFork` implementation to ensure staging repository names satisfy firewall staging isolation requirements.

---
