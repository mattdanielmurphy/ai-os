---
title: "Cap Miner Bounty Amounts"
date: "2026-08-09"
conversation_id: "b53eebe9-7201-4a7e-acc9-4ef839863936"
source: "antigravity"
---

# Cap Miner Bounty Amounts

## User

Update `/Volumes/127.0.0.1/projects/jules-burner/src/discovery/miner.ts` to strictly cap candidate bounty amounts:

In `fetchNextBountyCandidate()` and `main()`, filter out any candidate where:
- `candidate.bountyAmount !== undefined && candidate.bountyAmount > 1.00`
- OR `candidate.estimatedPayoutUsd !== undefined && candidate.estimatedPayoutUsd > 1.00`

Use `replace_file_content` to enforce this rule in `src/discovery/miner.ts`.

---

## Assistant

Created At: 2026-08-08T20:44:15-06:00
Completed At: 2026-08-08T20:44:15-06:00
File Path: `file:///Volumes/127.0.0.1/projects/jules-burner/src/discovery/miner.ts`
Total Lines: 43
Total Bytes: 1553
Showing lines 1 to 43
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
28:   const scored = candidates
29:     .filter(c => (c.bountyAmount === undefined || c.bountyAmount <= 1.00) && (c.estimatedPayoutUsd === undefined || c.estimatedPayoutUsd <= 1.00))
30:     .map(c => ranker.score(c));
31:   scored.sort((a, b) => b.score - a.score);
32: 
33:   if (isDryRun) {
34:     console.log('Dry run: Candidates found', scored);
35:   } else {
36:     console.log('Mining complete');
37:   }
38: }
39: 
40: if (require.main === module) {
41:   main().catch(console.error);
42: }
43: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-08T20:44:17-06:00
Completed At: 2026-08-08T20:44:17-06:00
The following changes were made by the multi_replace_file_content tool to: /Volumes/127.0.0.1/projects/jules-burner/src/discovery/miner.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -10,7 +10,9 @@
   const ranker = new YieldRiskRanker();
   const candidates = await pipeline.fetch();
   if (!candidates || candidates.length === 0) return null;
-  const scored = candidates.map(c => ranker.score(c));
+  const scored = candidates
+    .filter(c => (c.bountyAmount === undefined || c.bountyAmount <= 1.00) && (c.estimatedPayoutUsd === undefined || c.estimatedPayoutUsd <= 1.00))
+    .map(c => ranker.score(c));
   scored.sort((a, b) => b.score - a.score);
   return scored[0] ?? null;
 }
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

---
