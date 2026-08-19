---
title: "Refactor Miner Execution Logic"
date: "2026-08-07"
conversation_id: "fc062cc9-f5f3-4636-9f97-afc3dbcf9fc5"
source: "antigravity"
---

# Refactor Miner Execution Logic

## User

Please update /Users/matt/projects/jules-burner/src/discovery/miner.ts so that `main()` handles `--dry-run` properly:

```ts
export async function main() {
  const isDryRun = process.argv.includes('--dry-run');
  const pipelines = [new MicroBountiesPipeline(), new AssetSpecsPipeline(), new SelfTasksPipeline()];
  const ranker = new YieldRiskRanker();

  let candidates = [];
  for (const pipeline of pipelines) {
    candidates.push(...(await pipeline.fetch()));
  }

  const scored = candidates.map(c => ranker.score(c));
  scored.sort((a, b) => b.score - a.score);

  if (isDryRun) {
    console.log('Dry run: Candidates found', scored);
  } else {
    console.log('Mining complete');
  }
}
```
And also export `fetchNextBountyCandidate`:
```ts
export async function fetchNextBountyCandidate(): Promise<TaskCandidate | null> {
  const pipeline = new MicroBountiesPipeline();
  const ranker = new YieldRiskRanker();
  const candidates = await pipeline.fetch();
  if (!candidates || candidates.length === 0) return null;
  const scored = candidates.map(c => ranker.score(c));
  scored.sort((a, b) => b.score - a.score);
  return scored[0] ?? null;
}
```

Ensure all imports (`MicroBountiesPipeline`, `AssetSpecsPipeline`, `SelfTasksPipeline`, `YieldRiskRanker`, `TaskCandidate`) are cleanly included.

---

## Assistant

Created At: 2026-08-06T19:52:56-06:00
Completed At: 2026-08-06T19:52:56-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/discovery/miner.ts`
Total Lines: 36
Total Bytes: 997
Showing lines 1 to 36
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import { MicroBountiesPipeline } from './pipelines/micro_bounties';
2: import { YieldRiskRanker } from './ranker';
3: import type { TaskCandidate } from './types';
4: 
5: export async function fetchNextBountyCandidate(): Promise<TaskCandidate | null> {
6:   const pipelines = [new MicroBountiesPipeline()];
7:   const ranker = new YieldRiskRanker();
8: 
9:   let candidates: TaskCandidate[] = [];
10:   for (const pipeline of pipelines) {
11:     try {
12:       candidates.push(...(await pipeline.fetch()));
13:     } catch (e) {
14:       console.error('Failed to fetch from pipeline', e);
15:     }
16:   }
17: 
18:   const scored = candidates.map(c => ranker.score(c));
19:   scored.sort((a, b) => b.score - a.score);
20: 
21:   return scored.length > 0 ? scored[0] : null;
22: }
23: 
24: export async function main(): Promise<void> {
25:   const candidate = await fetchNextBountyCandidate();
26:   if (candidate) {
27:     console.log('Best candidate:', candidate);
28:   } else {
29:     console.log('No candidates found');
30:   }
31: }
32: 
33: if (require.main === module) {
34:   main().catch(console.error);
35: }
36: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-06T19:52:57-06:00
Completed At: 2026-08-06T19:52:57-06:00
{"name":"miner.ts","sizeBytes":"997"}
{"name":"pipelines","isDir":true}
{"name":"ranker.ts","sizeBytes":"377"}
{"name":"types.ts","sizeBytes":"390"}

Summary: This directory contains 1 subdirectories and 3 files.

Created At: 2026-08-06T19:52:58-06:00
Completed At: 2026-08-06T19:52:58-06:00
{"name":"asset_specs.ts","sizeBytes":"408"}
{"name":"micro_bounties.ts","sizeBytes":"1218"}
{"name":"self_tasks.ts","sizeBytes":"407"}

Summary: This directory contains 0 subdirectories and 3 files.

Created At: 2026-08-06T19:53:00-06:00
Completed At: 2026-08-06T19:53:00-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/jules-burner/src/discovery/miner.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -1,4 +1,6 @@
 import { MicroBountiesPipeline } from './pipelines/micro_bounties';
+import { AssetSpecsPipeline } from './pipelines/asset_specs';
+import { SelfTasksPipeline } from './pipelines/self_tasks';
 import { YieldRiskRanker } from './ranker';
 import type { TaskCandidate } from './types';
 
@@ -5,27 +5,29 @@
-  const pipelines = [new MicroBountiesPipeline()];
-  const ranker = new YieldRiskRanker();
-
-  let candidates: TaskCandidate[] = [];
+  const pipeline = new MicroBountiesPipeline();
+  const ranker = new YieldRiskRanker();
+  const candidates = await pipeline.fetch();
+  if (!candidates || candidates.length === 0) return null;
+  const scored = candidates.map(c => ranker.score(c));
+  scored.sort((a, b) => b.score - a.score);
+  return scored[0] ?? null;
+}
+
+export async function main() {
+  const isDryRun = process.argv.includes('--dry-run');
+  const pipelines = [new MicroBountiesPipeline(), new AssetSpecsPipeline(), new SelfTasksPipeline()];
+  const ranker = new YieldRiskRanker();
+
+  let candidates = [];
   for (const pipeline of pipelines) {
-    try {
-      candidates.push(...(await pipeline.fetch()));
-    } catch (e) {
-      console.error('Failed to fetch from pipeline', e);
-    }
-  }
-
-  const scored = candidates.map(c => ranker.score(c));
-  scored.sort((a, b) => b.score - a.score);
-
-  return scored.length > 0 ? scored[0] : null;
-}
-
-export async function main(): Promise<void> {
-  const candidate = await fetchNextBountyCandidate();
-  if (candidate) {
-    console.log('Best candidate:', candidate);
+    candidates.push(...(await pipeline.fetch()));
+  }
+
+  const scored = candidates.map(c => ranker.score(c));
+  scored.sort((a, b) => b.score - a.score);
+
+  if (isDryRun) {
+    console.log('Dry run: Candidates found', scored);
   } else {
-    console.log('No candidates found');
+    console.log('Mining complete');
   }
 }
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-06T19:53:01-06:00
Completed At: 2026-08-06T19:53:01-06:00
Message sent to "a50c7f96-5f08-4c4e-82e3-d475dc73889b".

The file `/Users/matt/projects/jules-burner/src/discovery/miner.ts` has been updated to handle `--dry-run` in `main()` and export the `fetchNextBountyCandidate` function as requested. All required imports have been added.

---
