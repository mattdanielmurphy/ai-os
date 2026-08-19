---
title: "Implement Bounty Price Cap"
date: "2026-08-09"
conversation_id: "04492ee8-5241-4f2e-ab7c-d0b04cf18a92"
source: "antigravity"
---

# Implement Bounty Price Cap

## User

Modify `/Volumes/127.0.0.1/projects/jules-burner/src/discovery/pipeline.ts` and `/Volumes/127.0.0.1/projects/jules-burner/src/discovery/miner.ts` to strictly cap bounties at $1.00 USD (or equivalent):

1. In `/Volumes/127.0.0.1/projects/jules-burner/src/discovery/pipeline.ts`:
   - Filter `candidates` in `aggregateAll()`: keep ONLY candidates where `c.bountyAmount === undefined || c.bountyAmount <= 1.00` and `c.estimatedPayoutUsd === undefined || c.estimatedPayoutUsd <= 1.00`.
   - Explicitly reject any tasks with dollar values higher than $1.00 USD.

2. In `/Volumes/127.0.0.1/projects/jules-burner/src/discovery/miner.ts`:
   - Filter candidates in `main()` so any candidate with `bountyAmount > 1` or `estimatedPayoutUsd > 1` is removed.

Use `replace_file_content` to make these edits cleanly.

---

## Assistant

Created At: 2026-08-08T20:43:45-06:00
Completed At: 2026-08-08T20:43:46-06:00
File Path: `file:///Volumes/127.0.0.1/projects/jules-burner/src/discovery/pipeline.ts`
Total Lines: 51
Total Bytes: 1710
Showing lines 1 to 51
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import type { TaskCandidate } from "./types";
2: import { MicroBountiesPipeline } from "./micro_bounties";
3: import { TaskMarketClient } from "./taskmarket";
4: import { AlgoraPolarClient } from "./algora_polar";
5: import { OpireClient } from "./opire";
6: import { YieldRiskRanker } from "./ranker";
7: 
8: export class DiscoveryPipeline {
9:   private ghPipeline: MicroBountiesPipeline;
10:   private taskMarketClient: TaskMarketClient;
11:   private algoraPolarClient: AlgoraPolarClient;
12:   private opireClient: OpireClient;
13:   private ranker: YieldRiskRanker;
14: 
15:   constructor() {
16:     this.ghPipeline = new MicroBountiesPipeline();
17:     this.taskMarketClient = new TaskMarketClient();
18:     this.algoraPolarClient = new AlgoraPolarClient();
19:     this.opireClient = new OpireClient();
20:     this.ranker = new YieldRiskRanker();
21:   }
22: 
23:   public async discover(): Promise<TaskCandidate[]> {
24:     return this.aggregateAll();
25:   }
26: 
27:   public async aggregateAll(): Promise<TaskCandidate[]> {
28:     const results = await Promise.allSettled([
29:       this.taskMarketClient.fetchOpenTasks(),
30:       this.algoraPolarClient.fetchAlgoraBounties(),
31:       this.algoraPolarClient.fetchPolarBounties(),
32:       this.opireClient.fetchRewards(),
33:       this.ghPipeline.fetchBounties(),
34:     ]);
35: 
36:     const candidates: TaskCandidate[] = [];
37:     for (const r of results) {
38:       if (r.status === "fulfilled" && Array.isArray(r.value)) {
39:         candidates.push(...r.value);
40:       }
41:     }
42: 
43:     return candidates.map(c => this.ranker.score(c)).sort((a, b) => (b.score || 0) - (a.score || 0));
44:   }
45: 
46:   public async getNextBestCandidate(): Promise<TaskCandidate | null> {
47:     const candidates = await this.aggregateAll();
48:     return candidates.length > 0 ? candidates[0] : null;
49:   }
50: }
51: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-08T20:43:47-06:00
Completed At: 2026-08-08T20:43:47-06:00
File Path: `file:///Volumes/127.0.0.1/projects/jules-burner/src/discovery/miner.ts`
Total Lines: 41
Total Bytes: 1401
Showing lines 1 to 41
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import { MicroBountiesPipeline } from './pipelines/micro_bounties';
2: import { AssetSpecsPipeline } from './pipelines/asset_specs';
3: import { SelfTasksPipeline } from './pipelines/self_tasks';
4: import { NostrPipeline } from './pipelines/nostr_pipeline';
5: import { YieldRiskRanker } from './ranker';
6: import type { TaskCandidate } from './types';
7: 
8: export async function fetchNextBountyCandidate(): Promise<TaskCandidate | null> {
9:   const pipeline = new MicroBountiesPipeline();
10:   const ranker = new YieldRiskRanker();
11:   const candidates = await pipeline.fetch();
12:   if (!candidates || candidates.length === 0) return null;
13:   const scored = candidates.map(c => ranker.score(c));
14:   scored.sort((a, b) => b.score - a.score);
15:   return scored[0] ?? null;
16: }
17: 
18: export async function main() {
19:   const isDryRun = process.argv.includes('--dry-run');
20:   const pipelines = [new MicroBountiesPipeline(), new AssetSpecsPipeline(), new SelfTasksPipeline(), new NostrPipeline()];
21:   const ranker = new YieldRiskRanker();
22: 
23:   let candidates = [];
24:   for (const pipeline of pipelines) {
25:     candidates.push(...(await pipeline.fetch()));
26:   }
27: 
28:   const scored = candidates.map(c => ranker.score(c));
29:   scored.sort((a, b) => b.score - a.score);
30: 
31:   if (isDryRun) {
32:     console.log('Dry run: Candidates found', scored);
33:   } else {
34:     console.log('Mining complete');
35:   }
36: }
37: 
38: if (require.main === module) {
39:   main().catch(console.error);
40: }
41: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-08T20:43:48-06:00
Completed At: 2026-08-08T20:43:48-06:00
The following changes were made by the replace_file_content tool to: /Volumes/127.0.0.1/projects/jules-burner/src/discovery/pipeline.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -40,7 +40,10 @@
       }
     }
 
-    return candidates.map(c => this.ranker.score(c)).sort((a, b) => (b.score || 0) - (a.score || 0));
+    return candidates
+      .filter(c => (c.bountyAmount === undefined || c.bountyAmount <= 1.00) && (c.estimatedPayoutUsd === undefined || c.estimatedPayoutUsd <= 1.00))
+      .map(c => this.ranker.score(c))
+      .sort((a, b) => (b.score || 0) - (a.score || 0));
   }
 
   public async getNextBestCandidate(): Promise<TaskCandidate | null> {
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T20:43:49-06:00
Completed At: 2026-08-08T20:43:49-06:00
The following changes were made by the replace_file_content tool to: /Volumes/127.0.0.1/projects/jules-burner/src/discovery/miner.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -25,7 +25,9 @@
     candidates.push(...(await pipeline.fetch()));
   }
 
-  const scored = candidates.map(c => ranker.score(c));
+  const scored = candidates
+    .filter(c => (c.bountyAmount === undefined || c.bountyAmount <= 1.00) && (c.estimatedPayoutUsd === undefined || c.estimatedPayoutUsd <= 1.00))
+    .map(c => ranker.score(c));
   scored.sort((a, b) => b.score - a.score);
 
   if (isDryRun) {
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T20:43:50-06:00
Completed At: 2026-08-08T20:43:50-06:00
Message sent to "c1a99726-cbe8-4216-b6f3-f5bd05ba57fe".

The bounty cap modifications have been applied to both files:

*   **[`pipeline.ts`](file:///Volumes/127.0.0.1/projects/jules-burner/src/discovery/pipeline.ts)**: The `aggregateAll()` method now filters `candidates` to include only those where `bountyAmount` and `estimatedPayoutUsd` are undefined or less than or equal to $1.00 USD.
*   **[`miner.ts`](file:///Volumes/127.0.0.1/projects/jules-burner/src/discovery/miner.ts)**: The `main()` function now filters the `candidates` array using the same criteria before scoring and sorting.

---
