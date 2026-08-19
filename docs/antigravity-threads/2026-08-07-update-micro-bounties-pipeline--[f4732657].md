---
title: "Update Micro Bounties Pipeline"
date: "2026-08-07"
conversation_id: "f4732657-64a1-4125-a0cb-379d1ef75ae0"
source: "antigravity"
---

# Update Micro Bounties Pipeline

## User

Please update /Users/matt/projects/jules-burner/src/discovery/pipelines/micro_bounties.ts:

1. Use GitHub search API `octokit.rest.search.issuesAndPullRequests({ q: 'is:issue is:open label:bounty sort:updated-desc', per_page: 10 })` instead of `issues.listForRepo`.
2. Wrap the API call in a try/catch block. If the API call fails or requires auth (401/403/network error), log a warning and return mock candidates or fallback candidates so unit tests pass without failing.
3. Ensure `MicroBountiesPipeline.prototype.fetch()` always returns a non-empty array of `TaskCandidate` items (either live search items if successful, or fallback candidates if unauthenticated/in test mode).

Check `src/config.ts` for `BOT_GITHUB_TOKEN` or `PERSONAL_GITHUB_TOKEN` or `process.env.GITHUB_TOKEN`.

---

## Assistant

Created At: 2026-08-06T19:52:44-06:00
Completed At: 2026-08-06T19:52:44-06:00
{"name":"asset_specs.ts","sizeBytes":"408"}
{"name":"micro_bounties.ts","sizeBytes":"783"}
{"name":"self_tasks.ts","sizeBytes":"407"}

Summary: This directory contains 0 subdirectories and 3 files.

Created At: 2026-08-06T19:52:45-06:00
Completed At: 2026-08-06T19:52:45-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/discovery/pipelines/micro_bounties.ts`
Total Lines: 27
Total Bytes: 783
Showing lines 1 to 27
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import type { TaskCandidate } from '../types';
2: import { Octokit } from '@octokit/rest';
3: 
4: export class MicroBountiesPipeline {
5:   private octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
6: 
7:   async fetch(): Promise<TaskCandidate[]> {
8:     const { data: issues } = await this.octokit.issues.list({
9:       owner: 'jules-burner', // Assuming organization or user
10:       repo: 'jules-burner', // Assuming repo
11:       labels: 'bounty,algora,good first issue',
12:       state: 'open',
13:     });
14: 
15:     return issues.map((issue) => ({
16:       id: issue.node_id,
17:       source: 'micro_bounties',
18:       title: issue.title,
19:       description: `${issue.title}\n\n${issue.body || ''}`,
20:       url: issue.html_url,
21:       bountyAmount: 50, // Default if not parsed
22:       complexity: 'low',
23:     }));
24:   }
25: }
26: 
27: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-06T19:52:46-06:00
Completed At: 2026-08-06T19:52:46-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/config.ts`
Total Lines: 20
Total Bytes: 495
Showing lines 1 to 20
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import { z } from "zod";
2: 
3: const envSchema = z.object({
4:   GITHUB_TOKEN: z.string().optional(),
5:   JULES_CLI_PATH: z.string().default("jules"),
6:   DATABASE_PATH: z.string().default("data/audit.db"),
7: });
8: 
9: const env = envSchema.parse(process.env);
10: 
11: export const config = {
12:   DAILY_TASK_LIMIT: 100,
13:   MIN_JITTER_SECONDS: 180,
14:   MAX_JITTER_SECONDS: 420,
15:   STAGING_ORG_OR_USER: "staging-org",
16:   GITHUB_TOKEN: env.GITHUB_TOKEN,
17:   JULES_CLI_PATH: env.JULES_CLI_PATH,
18:   DATABASE_PATH: env.DATABASE_PATH,
19: };
20: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-06T19:52:48-06:00
Completed At: 2026-08-06T19:52:48-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/jules-burner/src/discovery/pipelines/micro_bounties.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -5,22 +5,35 @@
   private octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
 
   async fetch(): Promise<TaskCandidate[]> {
-    const { data: issues } = await this.octokit.issues.list({
-      owner: 'jules-burner', // Assuming organization or user
-      repo: 'jules-burner', // Assuming repo
-      labels: 'bounty,algora,good first issue',
-      state: 'open',
-    });
-
-    return issues.map((issue) => ({
-      id: issue.node_id,
-      source: 'micro_bounties',
-      title: issue.title,
-      description: `${issue.title}\n\n${issue.body || ''}`,
-      url: issue.html_url,
-      bountyAmount: 50, // Default if not parsed
-      complexity: 'low',
-    }));
+    try {
+      const { data } = await this.octokit.rest.search.issuesAndPullRequests({
+        q: 'is:issue is:open label:bounty sort:updated-desc',
+        per_page: 10,
+      });
+
+      return data.items.map((issue) => ({
+        id: issue.node_id,
+        source: 'micro_bounties',
+        title: issue.title,
+        description: `${issue.title}\n\n${issue.body || ''}`,
+        url: issue.html_url,
+        bountyAmount: 50,
+        complexity: 'low',
+      }));
+    } catch (error) {
+      console.warn('MicroBountiesPipeline: Failed to fetch bounties, using fallbacks.', error);
+      return [
+        {
+          id: 'fallback-1',
+          source: 'micro_bounties',
+          title: 'Fallback: Setup Development Environment',
+          description: 'Ensure your local development environment is configured correctly.',
+          url: 'https://github.com/example/repo/issues/1',
+          bountyAmount: 50,
+          complexity: 'low',
+        },
+      ];
+    }
   }
 }
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-06T19:52:50-06:00
Completed At: 2026-08-06T19:52:50-06:00
Message sent to "a50c7f96-5f08-4c4e-82e3-d475dc73889b".

FINISHED

---
