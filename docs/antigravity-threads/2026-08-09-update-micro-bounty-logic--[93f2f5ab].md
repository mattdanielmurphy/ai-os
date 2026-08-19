---
title: "Update Micro Bounty Logic"
date: "2026-08-09"
conversation_id: "93f2f5ab-1c44-4cd4-acb1-4be3448f3d05"
source: "antigravity"
---

# Update Micro Bounty Logic

## User

Fix `/Volumes/127.0.0.1/projects/jules-burner/src/discovery/pipeline.ts` and `/Volumes/127.0.0.1/projects/jules-burner/src/discovery/micro_bounties.ts`:

1. In `src/discovery/micro_bounties.ts`:
   - Change line 56 `estimatedPayoutUsd: 20` to `estimatedPayoutUsd: 0.50` (or `bountyAmount: 0.50`).

2. In `src/discovery/pipeline.ts`:
   - Inside `aggregateAll()`: Add a strict filter on the aggregated candidate array:
     ```ts
     const microOnly = candidates.filter(c => {
       const amount = c.bountyAmount ?? c.estimatedPayoutUsd ?? 0;
       return amount <= 1.00;
     });
     return microOnly.map(c => this.ranker.score(c)).sort((a, b) => (b.score || 0) - (a.score || 0));
     ```

Use `replace_file_content` to apply these edits.

---

## Assistant

Created At: 2026-08-08T20:44:35-06:00
Completed At: 2026-08-08T20:44:35-06:00
File Path: `file:///Volumes/127.0.0.1/projects/jules-burner/src/discovery/micro_bounties.ts`
Total Lines: 67
Total Bytes: 2061
Showing lines 1 to 67
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import { config } from "../config";
2: import type { TaskCandidate } from "./types";
3: 
4: export interface GitHubIssueSearchResult {
5:   id: number;
6:   number: number;
7:   title: string;
8:   body: string | null;
9:   html_url: string;
10:   repository_url: string;
11:   state: string;
12:   labels: Array<{ name: string } | string>;
13: }
14: 
15: export class MicroBountiesPipeline {
16:   private githubToken?: string;
17: 
18:   constructor(token?: string) {
19:     this.githubToken = token || process.env.GITHUB_TOKEN || process.env.GH_TOKEN || config.GITHUB_TOKEN;
20:   }
21: 
22:   public async fetchBounties(customQuery?: string): Promise<TaskCandidate[]> {
23:     const query = customQuery || "is:issue is:open label:bounty,algora,polar sort:updated-desc";
24:     const url = `https://api.github.com/search/issues?q=${encodeURIComponent(query)}&per_page=15`;
25: 
26:     const headers: Record<string, string> = {
27:       "User-Agent": "Jules-Quota-Burner",
28:       "Accept": "application/vnd.github.v3+json",
29:     };
30: 
31:     if (this.githubToken) {
32:       headers["Authorization"] = `Bearer ${this.githubToken}`;
33:     }
34: 
35:     try {
36:       const res = await fetch(url, { headers });
37:       if (!res.ok) {
38:         const errorText = await res.text();
39:         console.warn(`[MicroBountiesPipeline] GitHub search error ${res.status}: ${errorText}`);
40:         return [];
41:       }
42: 
43:       const data = await res.json() as any;
44:       const items: GitHubIssueSearchResult[] = data.items || [];
45: 
46:       return items.map(item => {
47:         const repoPath = item.repository_url.replace("https://api.github.com/repos/", "");
48:         return {
49:           id: `gh_${item.id}`,
50:           type: "MICRO_BOUNTY" as const,
51:           title: item.title,
52:           description: item.body || item.title,
53:           targetRepo: repoPath,
54:           sourceUrl: item.html_url,
55:           source: "github_bounty",
56:           estimatedPayoutUsd: 20,
57:           status: "OPEN" as const,
58:           difficulty: "MEDIUM" as const,
59:         };
60:       });
61:     } catch (err: any) {
62:       console.warn(`[MicroBountiesPipeline] Fetch failed: ${err?.message || err}`);
63:       return [];
64:     }
65:   }
66: }
67: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-08T20:44:36-06:00
Completed At: 2026-08-08T20:44:36-06:00
File Path: `file:///Volumes/127.0.0.1/projects/jules-burner/src/discovery/pipeline.ts`
Total Lines: 54
Total Bytes: 1873
Showing lines 1 to 54
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
43:     return candidates
44:       .filter(c => (c.bountyAmount === undefined || c.bountyAmount <= 1.00) && (c.estimatedPayoutUsd === undefined || c.estimatedPayoutUsd <= 1.00))
45:       .map(c => this.ranker.score(c))
46:       .sort((a, b) => (b.score || 0) - (a.score || 0));
47:   }
48: 
49:   public async getNextBestCandidate(): Promise<TaskCandidate | null> {
50:     const candidates = await this.aggregateAll();
51:     return candidates.length > 0 ? candidates[0] : null;
52:   }
53: }
54: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-08T20:44:37-06:00
Completed At: 2026-08-08T20:44:37-06:00
The following changes were made by the replace_file_content tool to: /Volumes/127.0.0.1/projects/jules-burner/src/discovery/micro_bounties.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -53,7 +53,7 @@
           targetRepo: repoPath,
           sourceUrl: item.html_url,
           source: "github_bounty",
-          estimatedPayoutUsd: 20,
+          estimatedPayoutUsd: 0.50,
           status: "OPEN" as const,
           difficulty: "MEDIUM" as const,
         };
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T20:44:39-06:00
Completed At: 2026-08-08T20:44:39-06:00
The following changes were made by the replace_file_content tool to: /Volumes/127.0.0.1/projects/jules-burner/src/discovery/pipeline.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -40,10 +40,11 @@
       }
     }
 
-    return candidates
-      .filter(c => (c.bountyAmount === undefined || c.bountyAmount <= 1.00) && (c.estimatedPayoutUsd === undefined || c.estimatedPayoutUsd <= 1.00))
-      .map(c => this.ranker.score(c))
-      .sort((a, b) => (b.score || 0) - (a.score || 0));
+    const microOnly = candidates.filter(c => {
+      const amount = c.bountyAmount ?? c.estimatedPayoutUsd ?? 0;
+      return amount <= 1.00;
+    });
+    return microOnly.map(c => this.ranker.score(c)).sort((a, b) => (b.score || 0) - (a.score || 0));
   }
 
   public async getNextBestCandidate(): Promise<TaskCandidate | null> {
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T20:44:40-06:00
Completed At: 2026-08-08T20:44:40-06:00
Message sent to "c1a99726-cbe8-4216-b6f3-f5bd05ba57fe".

---
