---
title: "Update GitHub Bounty Filtering"
date: "2026-08-09"
conversation_id: "7f6cc664-5922-4e0f-967e-6b01e2c02961"
source: "antigravity"
---

# Update GitHub Bounty Filtering

## User

Enforce assignee, pull request, and human review / claimed comment checks on GitHub issue searches in `/Volumes/127.0.0.1/projects/jules-burner/src/discovery/pipelines/micro_bounties.ts`:

1. Update search query `q` in `src/discovery/pipelines/micro_bounties.ts` from:
   `is:issue is:open label:bounty sort:updated-desc`
   to:
   `is:issue is:open no:assignee label:bounty sort:updated-desc`

2. Inside `res.data.items.map` (or filter step):
   Filter out any issue where `issue.assignee` or `issue.assignees` is present, OR `issue.comments > 0` (or check if `issue.pull_request` is defined).

Use `replace_file_content` to apply these edits cleanly.

---

## Assistant

Created At: 2026-08-08T20:45:01-06:00
Completed At: 2026-08-08T20:45:01-06:00
File Path: `file:///Volumes/127.0.0.1/projects/jules-burner/src/discovery/pipelines/micro_bounties.ts`
Total Lines: 57
Total Bytes: 1952
Showing lines 1 to 57
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import type { TaskCandidate } from "../types";
2: import { Octokit } from "@octokit/rest";
3: import { logger } from "../../telemetry/logger";
4: import { rateLimitManager } from "../../telemetry/rate_limiter";
5: 
6: export class MicroBountiesPipeline {
7:   async fetch(): Promise<TaskCandidate[]> {
8:     const backoff = rateLimitManager.shouldBackoff("search");
9:     if (backoff.backoff) {
10:       logger.warn("DISCOVERY", `Search rate limit safe cooldown active (${Math.round(backoff.waitMs / 1000)}s). Using fallback tasks.`);
11:       return this.getFallbacks();
12:     }
13: 
14:     const { token, account } = rateLimitManager.getOptimalToken("search");
15:     const octokit = new Octokit({ auth: token });
16: 
17:     try {
18:       const res = await octokit.rest.search.issuesAndPullRequests({
19:         q: "is:issue is:open label:bounty sort:updated-desc",
20:         per_page: 10,
21:         request: { signal: AbortSignal.timeout(4000) },
22:       });
23: 
24:       if (res.headers) {
25:         rateLimitManager.recordResponseHeaders(account === "personal" ? "personal" : "bot", "search", res.headers as any);
26:       }
27: 
28:       return res.data.items.map((issue) => ({
29:         id: issue.node_id,
30:         source: "micro_bounties",
31:         title: issue.title,
32:         description: `${issue.title}\n\n${issue.body || ""}`,
33:         url: issue.html_url,
34:         bountyAmount: 0.50,
35:         complexity: "low",
36:       }));
37:     } catch (error: any) {
38:       logger.warn("DISCOVERY", `GitHub issue search failed: ${logger.sanitizeError(error)}. Using fallback tasks.`);
39:       return this.getFallbacks();
40:     }
41:   }
42: 
43:   private getFallbacks(): TaskCandidate[] {
44:     return [
45:       {
46:         id: "fallback-1",
47:         source: "micro_bounties",
48:         title: "Fallback: Setup Development Environment",
49:         description: "Ensure your local development environment is configured correctly.",
50:         url: "https://github.com/example/repo/issues/1",
51:         bountyAmount: 0.50,
52:         complexity: "low",
53:       },
54:     ];
55:   }
56: }
57: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-08T20:45:03-06:00
Completed At: 2026-08-08T20:45:03-06:00
The following changes were made by the replace_file_content tool to: /Volumes/127.0.0.1/projects/jules-burner/src/discovery/pipelines/micro_bounties.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -16,7 +16,7 @@
 
     try {
       const res = await octokit.rest.search.issuesAndPullRequests({
-        q: "is:issue is:open label:bounty sort:updated-desc",
+        q: "is:issue is:open no:assignee label:bounty sort:updated-desc",
         per_page: 10,
         request: { signal: AbortSignal.timeout(4000) },
       });
@@ -24,15 +24,17 @@
         rateLimitManager.recordResponseHeaders(account === "personal" ? "personal" : "bot", "search", res.headers as any);
       }
 
-      return res.data.items.map((issue) => ({
-        id: issue.node_id,
-        source: "micro_bounties",
-        title: issue.title,
-        description: `${issue.title}\n\n${issue.body || ""}`,
-        url: issue.html_url,
-        bountyAmount: 0.50,
-        complexity: "low",
-      }));
+      return res.data.items
+        .filter((issue) => !issue.assignee && !issue.assignees?.length && !issue.pull_request && issue.comments === 0)
+        .map((issue) => ({
+          id: issue.node_id,
+          source: "micro_bounties",
+          title: issue.title,
+          description: `${issue.title}\n\n${issue.body || ""}`,
+          url: issue.html_url,
+          bountyAmount: 0.50,
+          complexity: "low",
+        }));
     } catch (error: any) {
       logger.warn("DISCOVERY", `GitHub issue search failed: ${logger.sanitizeError(error)}. Using fallback tasks.`);
       return this.getFallbacks();
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T20:45:04-06:00
Completed At: 2026-08-08T20:45:04-06:00
Message sent to "c1a99726-cbe8-4216-b6f3-f5bd05ba57fe".

---
