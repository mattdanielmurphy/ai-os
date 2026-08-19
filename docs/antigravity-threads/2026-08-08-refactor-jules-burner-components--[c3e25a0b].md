---
title: "Refactor Jules Burner Components"
date: "2026-08-08"
conversation_id: "c3e25a0b-6621-4ade-b20b-6c99efcb4bef"
source: "antigravity"
---

# Refactor Jules Burner Components

## User

Fix the following files in `/Users/matt/projects/jules-burner`:

1. In `/Users/matt/projects/jules-burner/src/audit/db.ts`:
Fix the end of the class closing brace and export:
Make sure the class `AuditDatabase` has its closing brace `}` and then:
```typescript
export { AuditDatabase, AuditDatabase as AuditDB };
```

2. In `/Users/matt/projects/jules-burner/src/staging/fork_manager.ts`:
```typescript
import { config } from "../config";

export interface ForkResult {
  success: boolean;
  forkRepo: string;
  error?: string;
}

export class ForkManager {
  private userOrg: string;

  constructor(userOrg: string = config.STAGING_ORG_OR_USER) {
    this.userOrg = userOrg;
  }

  public getStagingRepoName(upstreamRepo: string): string {
    const parts = upstreamRepo.split("/");
    const repoName = parts[parts.length - 1];
    return `${this.userOrg}/staging-${repoName}`;
  }

  public async createStagingBranch(stagingRepo: string, title: string): Promise<string> {
    const safeTitle = title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
    return `jules/feat-${safeTitle}-${Date.now()}`;
  }

  public async ensureStagingFork(upstreamRepo: string): Promise<{ stagingRepo: string; forkRepo: string; created: boolean }> {
    const forkRepo = this.getStagingRepoName(upstreamRepo);
    return { stagingRepo: forkRepo, forkRepo, created: true };
  }

  public async forkRepository(upstreamRepo: string): Promise<ForkResult> {
    try {
      const parts = upstreamRepo.split("/");
      const repoName = parts[parts.length - 1];
      const targetFork = `${this.userOrg}/${repoName}`;

      const proc = Bun.spawn(["gh", "repo", "fork", upstreamRepo, "--clone=false", "--org", this.userOrg], {
        stdout: "pipe",
        stderr: "pipe",
        env: { ...process.env },
      });

      const exitCode = await proc.exited;
      const stderr = await new Response(proc.stderr).text();

      if (exitCode === 0 || stderr.includes("already exists")) {
        return { success: true, forkRepo: targ
<truncated 11539 bytes>
thy: false,
      errorCode: code,
      message: errorMsg,
      actionRequired: action,
    };
  }

  public classifyFriction(): Record<string, number> {
    const logs = this.db.getAllFrictionLogs();
    const result: Record<string, number> = {};
    for (const log of logs) {
      result[log.failureCategory] = (result[log.failureCategory] || 0) + 1;
    }
    return result;
  }

  public runTuningCycle(dayIndex: number) {
    const quota = this.allocator.getQuotaAllocation(dayIndex);
    const logs = this.db.getAllFrictionLogs();
    const directives = this.patcher.analyzeFrictionAndPatch(logs);
    const injectedPromptSuffix = this.patcher.getInjectedPromptDirectives();

    const repairTasks: Array<{ type: string; priority: string; targetArea: string }> = [];
    for (const log of logs) {
      if (log.failureCategory === "AUTH_403" || log.failureCategory === "BUILD_FAIL") {
        repairTasks.push({
          type: "AUTO_HEAL",
          priority: "CRITICAL",
          targetArea: log.failureCategory === "AUTH_403" ? "auth" : "dependencies",
        });
      } else {
        repairTasks.push({
          type: "ROUTINE_PATCH",
          priority: "MEDIUM",
          targetArea: "test_suite",
        });
      }
    }

    return {
      quota,
      directives,
      repairTasks,
      injectedPromptSuffix,
    };
  }

  public runDailyTuning(taskHistoryCount: number): {
    quotaProfile: string;
    appliedPromptPatches: number;
    infraStatus: InfrastructureStatus;
  } {
    const profile = this.allocator.getProfile ? this.allocator.getProfile(taskHistoryCount) : { mode: "MATURE" };
    const patchedCount = this.patcher.autoTune ? this.patcher.autoTune() : 0;

    return {
      quotaProfile: profile.mode,
      appliedPromptPatches: patchedCount,
      infraStatus: { healthy: true },
    };
  }
}
```

Use write_to_file / replace_file_content directly. Ensure all code is cleanly formatted.

---

## Assistant

Created At: 2026-08-08T13:48:10-06:00
Completed At: 2026-08-08T13:48:10-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/audit/db.ts`
Total Lines: 429
Total Bytes: 12471
Showing lines 1 to 429
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import { Database } from "bun:sqlite";
2: import { config } from "../config";
3: import { SessionRecord, FrictionLogRecord, DailyMetricsRecord, DispatchedTaskRecord } from "./types";
4: import { mkdirSync, existsSync } from "fs";
5: import { dirname } from "path";
6: 
7: export const auditOpenApiSchema = {
8:   openapi: "3.0.0",
9:   info: {
10:     title: "Audit Telemetry API",
11:     version: "1.0.0",
12:     description: "API for audit telemetry and friction logs.",
13:   },
14:   paths: {
15:     "/sessions": {
16:       get: {
17:         summary: "Get all sessions",
18:         responses: {
19:           "200": {
20:             description: "A list of sessions",
21:             content: {
22:               "application/json": {
23:                 schema: {
24:                   type: "array",
25:                   items: {
26:                     $ref: "#/components/schemas/Session",
27:                   },
28:                 },
29:               },
30:             },
31:           },
32:         },
33:       },
34:       post: {
35:         summary: "Create a session",
36:         requestBody: {
37:           required: true,
38:           content: {
39:             "application/json": {
40:               schema: {
41:                 $ref: "#/components/schemas/Session",
42:               },
43:             },
44:           },
45:         },
46:         responses: {
47:           "201": {
48:             description: "Session created",
49:           },
50:           "400": {
51:             description: "Invalid input",
52:           },
53:         },
54:   
<truncated 10944 bytes>
   }
383: 
384:         if (req.method === "GET" && url.pathname === "/sessions") {
385:           const sessions = this.getAllSessions();
386:           return new Response(JSON.stringify(sessions), {
387:             headers: { "Content-Type": "application/json" },
388:           });
389:         }
390: 
391:         if (req.method === "POST" && url.pathname === "/sessions") {
392:           try {
393:             const body = (await req.json()) as SessionRecord;
394:             if (!body.sessionId || !body.taskId || !body.status) {
395:               return new Response("Invalid session data", { status: 400 });
396:             }
397:             this.insertSession(body);
398:             return new Response("Session created", { status: 201 });
399:           } catch (e) {
400:             return new Response("Invalid JSON", { status: 400 });
401:           }
402:         }
403: 
404:         if (req.method === "GET" && url.pathname === "/friction-logs") {
405:           const logs = this.getAllFrictionLogs();
406:           return new Response(JSON.stringify(logs), {
407:             headers: { "Content-Type": "application/json" },
408:           });
409:         }
410: 
411:         if (req.method === "POST" && url.pathname === "/friction-logs") {
412:           try {
413:             const body = (await req.json()) as FrictionLogRecord;
414:             if (!body.sessionId || !body.failureCategory || !body.rawError) {
415:               return new Response("Invalid friction log data", { status: 400 });
416:             }
417:             this.insertFrictionLog(body);
418:             return new Response("Friction log created", { status: 201 });
419:           } catch (e) {
420:             return new Response("Invalid JSON", { status: 400 });
421:           }
422:         }
423: 
424:         return new Response("Not Found", { status: 404 });
425:       },
426:     });
427:   }
428: export { AuditDatabase as AuditDB };
429: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-08T13:48:11-06:00
Completed At: 2026-08-08T13:48:11-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/jules-burner/src/audit/db.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -425,5 +425,7 @@
       },
     });
   }
-export { AuditDatabase as AuditDB };
+}
+
+export { AuditDatabase, AuditDatabase as AuditDB };
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T13:48:15-06:00
Completed At: 2026-08-08T13:48:15-06:00
Created file file:///Users/matt/projects/jules-burner/src/staging/fork_manager.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-08T13:48:17-06:00
Completed At: 2026-08-08T13:48:17-06:00
Created file file:///Users/matt/projects/jules-burner/src/discovery/taskmarket.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-08T13:48:20-06:00
Completed At: 2026-08-08T13:48:20-06:00
Created file file:///Users/matt/projects/jules-burner/src/discovery/algora_polar.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-08T13:48:21-06:00
Completed At: 2026-08-08T13:48:21-06:00
Created file file:///Users/matt/projects/jules-burner/src/discovery/opire.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-08T13:48:23-06:00
Completed At: 2026-08-08T13:48:23-06:00
Created file file:///Users/matt/projects/jules-burner/src/discovery/pipeline.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-08T13:48:24-06:00
Completed At: 2026-08-08T13:48:24-06:00
File Path: `file:///Users/matt/projects/jules-burner/tests/discovery/discovery.test.ts`
Total Lines: 145
Total Bytes: 4343
Showing lines 1 to 145
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import { expect, test } from "bun:test";
2: import { YieldRiskRanker } from "../../src/discovery/ranker";
3: import { AssetSpecsPipeline } from "../../src/discovery/pipelines/asset_specs";
4: import { MicroBountiesPipeline } from "../../src/discovery/pipelines/micro_bounties";
5: import { SelfTasksPipeline } from "../../src/discovery/pipelines/self_tasks";
6: import { main } from "../../src/discovery/miner";
7: 
8: test("miner main should execute without throwing", async () => {
9:   // Capture console.log to avoid noise
10:   const originalLog = console.log;
11:   console.log = () => {};
12:   
13:   let error;
14:   try {
15:     await main();
16:   } catch (e) {
17:     error = e;
18:   }
19:   
20:   console.log = originalLog;
21:   expect(error).toBeUndefined();
22: });
23: 
24: test("miner main should handle --dry-run argument", async () => {
25:   const originalArgv = process.argv;
26:   process.argv = [...originalArgv, '--dry-run'];
27:   
28:   const originalLog = console.log;
29:   let loggedDryRun = false;
30:   console.log = (...args) => {
31:     if (args[0] && typeof args[0] === 'string' && args[0].includes('Dry run')) {
32:       loggedDryRun = true;
33:     }
34:   };
35:   
36:   await main();
37:   
38:   process.argv = originalArgv;
39:   console.log = originalLog;
40:   
41:   expect(loggedDryRun).toBe(true);
42: });
43: 
44: test("YieldRiskRanker should rank low complexity higher", () => {
45:   const ranker = new YieldRiskRanker();
46:   const task = {
47:     id: "test",
48:     source: "self_tasks" as any,
49:     title: "Test",

<truncated 1413 bytes>
 ranker.score(task);
99:   // 50 + 20 (low) + 30 (bounty) = 100
100:   expect(scored.score).toBe(100);
101: });
102: 
103: test("AssetSpecsPipeline should return task candidates", async () => {
104:   const pipeline = new AssetSpecsPipeline();
105:   const results = await pipeline.fetch();
106:   expect(results.length).toBeGreaterThan(0);
107:   expect(results[0].source).toBe("asset_specs");
108: });
109: 
110: test("MicroBountiesPipeline should return task candidates", async () => {
111:   const pipeline = new MicroBountiesPipeline();
112:   const results = await pipeline.fetch();
113:   expect(results.length).toBeGreaterThan(0);
114:   expect(results[0].source).toBe("micro_bounties");
115: });
116: 
117: 
118: test("TaskMarketClient should fetch data", async () => {
119:   const { TaskMarketClient } = await import("../../src/discovery/clients/task_market");
120:   const client = new TaskMarketClient();
121:   const results = await client.fetchTasks();
122:   expect(Array.isArray(results)).toBe(true);
123: });
124: 
125: test("AlgoraPolarClient should fetch data", async () => {
126:   const { AlgoraPolarClient } = await import("../../src/discovery/clients/algora_polar");
127:   const client = new AlgoraPolarClient();
128:   const results = await client.fetchTasks();
129:   expect(Array.isArray(results)).toBe(true);
130: });
131: 
132: test("OpireClient should fetch data", async () => {
133:   const { OpireClient } = await import("../../src/discovery/clients/opire");
134:   const client = new OpireClient();
135:   const results = await client.fetchTasks();
136:   expect(Array.isArray(results)).toBe(true);
137: });
138: 
139: test("DiscoveryPipeline should consolidate candidates", async () => {
140:   const { DiscoveryPipeline } = await import("../../src/discovery/pipeline");
141:   const pipeline = new DiscoveryPipeline();
142:   const tasks = await pipeline.discover();
143:   expect(Array.isArray(tasks)).toBe(true);
144: });
145: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-08T13:48:26-06:00
Completed At: 2026-08-08T13:48:26-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/jules-burner/tests/discovery/discovery.test.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -116,7 +116,7 @@
 
 
 test("TaskMarketClient should fetch data", async () => {
-  const { TaskMarketClient } = await import("../../src/discovery/clients/task_market");
+  const { TaskMarketClient } = await import("../../src/discovery/taskmarket");
   const client = new TaskMarketClient();
   const results = await client.fetchTasks();
   expect(Array.isArray(results)).toBe(true);
@@ -123,6 +123,6 @@
 
 test("AlgoraPolarClient should fetch data", async () => {
-  const { AlgoraPolarClient } = await import("../../src/discovery/clients/algora_polar");
+  const { AlgoraPolarClient } = await import("../../src/discovery/algora_polar");
   const client = new AlgoraPolarClient();
   const results = await client.fetchTasks();
   expect(Array.isArray(results)).toBe(true);
@@ -129,6 +129,6 @@
 
 test("OpireClient should fetch data", async () => {
-  const { OpireClient } = await import("../../src/discovery/clients/opire");
+  const { OpireClient } = await import("../../src/discovery/opire");
   const client = new OpireClient();
   const results = await client.fetchTasks();
   expect(Array.isArray(results)).toBe(true);
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T13:48:29-06:00
Completed At: 2026-08-08T13:48:29-06:00
Created file file:///Users/matt/projects/jules-burner/src/self_improve/tuner.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-08T13:48:30-06:00
Completed At: 2026-08-08T13:48:31-06:00
Message sent to "bef3c6ef-d5d2-4d21-b2f6-a0ce12a497ac".

The requested file updates have been completed:

*   **`src/audit/db.ts`**: Fixed the `AuditDatabase` closing brace and export.
*   **`src/staging/fork_manager.ts`**: Implemented `ForkManager`.
*   **`src/discovery/taskmarket.ts`**: Added `fetchTasks()` alias for `fetchOpenTasks()`.
*   **`src/discovery/algora_polar.ts`**: Added `fetchTasks()` alias for `fetchAlgoraBounties()`.
*   **`src/discovery/opire.ts`**: Added `fetchTasks()` alias for `fetchRewards()`.
*   **`src/discovery/pipeline.ts`**: Implemented the consolidated pipeline using the updated clients.
*   **`tests/discovery/discovery.test.ts`**: Updated imports to reflect the file structure changes.
*   **`src/self_improve/tuner.ts`**: Updated `SystemTuner` with new infrastructure self-healing methods.

I have notified the parent agent of these changes.

---
