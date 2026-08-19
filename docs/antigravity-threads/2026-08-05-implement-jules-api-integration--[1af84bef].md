---
title: "Implement Jules API Integration"
date: "2026-08-05"
conversation_id: "1af84bef-6b35-4f8d-9add-8dd677b29d08"
source: "antigravity"
---

# Implement Jules API Integration

## User

You are a leaf file-editing agent. Create and modify all the following files EXACTLY as specified. Do not skip any file. Do not delegate.

---

## FILE 1: MODIFY /Users/matt/projects/jules-burner/src/config.ts

Overwrite the entire file with:

```typescript
import { z } from "zod";

const envSchema = z.object({
  GITHUB_TOKEN: z.string().optional(),
  JULES_CLI_PATH: z.string().default("jules"),
  JULES_API_KEY: z.string().optional(),
  JULES_API_BASE_URL: z.string().default("https://jules.googleapis.com/v1alpha"),
  JULES_REPO_SOURCE: z.string().default("sources/github/mattdanielmurphy/jules-burner"),
  DATABASE_PATH: z.string().default("data/audit.db"),
  USE_JULES_API: z.string().default("true"),
});

const env = envSchema.parse(process.env);

export const config = {
  DAILY_TASK_LIMIT: 100,
  MIN_JITTER_SECONDS: 180,
  MAX_JITTER_SECONDS: 420,
  STAGING_ORG_OR_USER: "staging-org",
  GITHUB_TOKEN: env.GITHUB_TOKEN,
  JULES_CLI_PATH: env.JULES_CLI_PATH,
  JULES_API_KEY: env.JULES_API_KEY,
  JULES_API_BASE_URL: env.JULES_API_BASE_URL,
  JULES_REPO_SOURCE: env.JULES_REPO_SOURCE,
  DATABASE_PATH: env.DATABASE_PATH,
  USE_JULES_API: env.USE_JULES_API !== "false",
};
```

---

## FILE 2: CREATE /Users/matt/projects/jules-burner/src/daemon/jules_api.ts

Create this new file:

```typescript
import { config } from "../config";

export interface JulesSession {
  name: string;           // e.g. "sessions/abc123"
  state: string;          // e.g. "PENDING", "RUNNING", "SUCCEEDED", "FAILED"
  prompt?: string;
  title?: string;
  createTime?: string;
  updateTime?: string;
}

export interface CreateSessionOptions {
  prompt: string;
  title?: string;
  sourceRepo?: string;       // e.g. "sources/github/mattdanielmurphy/jules-burner"
  startingBranch?: string;
  automationMode?: "AUTO_CREATE_PR" | "UNSET";
  requirePlanApproval?: boolean;
}

export class JulesAPI {
  private apiKey: string;
  private baseUrl: string;

  constructor(apiKey?: string, baseUrl?: string) {
    this.apiKey = apiKey ?? config.JULES_A
<truncated 18199 bytes>
newSession.name,
      });
    } catch (err: any) {
      console.error(`   ❌ Failed: ${err.message}`);
      results.push({
        original: session.name,
        title: session.title,
        error: err.message,
      });
    }

    // Brief delay to avoid rate-limiting
    await new Promise(r => setTimeout(r, 1200));
  }

  // Persist results
  const outDir = "./tmp";
  if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
  const outPath = path.join(outDir, "backfill_results.json");
  fs.writeFileSync(outPath, JSON.stringify(results, null, 2));

  const succeeded = results.filter(r => r.newSession).length;
  const failed = results.filter(r => r.error).length;
  console.log(`\n📊 Backfill complete: ${succeeded} succeeded, ${failed} failed.`);
  console.log(`Results written to ${outPath}`);
}

main().catch(err => {
  console.error("Fatal:", err);
  process.exit(1);
});
```

---

## FILE 7: MODIFY /Users/matt/projects/jules-burner/AG_CONTEXT.md

Append the following lines to the end of the existing file (do NOT overwrite, just append):

```
- **Never interrupt a running Jules session**: Let any active session complete fully before re-queuing or modifying its target repository. This is a project-level invariant.
- **Jules API Mode**: All new sessions are dispatched via the Jules REST API (`jules.googleapis.com/v1alpha`) with `automationMode: AUTO_CREATE_PR` and `requirePlanApproval: false`. The CLI path (`jules remote new`) is kept as a fallback only (`USE_JULES_API=false`).
- **Backfill script**: `bun run src/scripts/backfill_pending_prs.ts` re-submits any sessions stuck at manual plan approval in the web UI.
```

---

All 7 files must be created/modified. Use write_to_file with Overwrite=true for files 1, 3, 4. Use write_to_file (no overwrite needed) for files 2, 5, 6. For file 7, read the existing content first then use replace_file_content to append the new lines at the end.

---

## Assistant

Created At: 2026-08-05T04:21:24-06:00
Completed At: 2026-08-05T04:21:24-06:00
Created file file:///Users/matt/projects/jules-burner/src/config.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T04:21:27-06:00
Completed At: 2026-08-05T04:21:27-06:00
Created file file:///Users/matt/projects/jules-burner/src/daemon/jules_api.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T04:21:31-06:00
Completed At: 2026-08-05T04:21:31-06:00
Created file file:///Users/matt/projects/jules-burner/src/daemon/jules_cli.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T04:21:35-06:00
Completed At: 2026-08-05T04:21:35-06:00
Created file file:///Users/matt/projects/jules-burner/src/daemon/dispatcher.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T04:21:38-06:00
Completed At: 2026-08-05T04:21:38-06:00
Created file file:///Users/matt/projects/jules-burner/.github/workflows/auto_merge_jules_prs.yml with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T04:21:40-06:00
Completed At: 2026-08-05T04:21:41-06:00
Created file file:///Users/matt/projects/jules-burner/src/scripts/backfill_pending_prs.ts with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T04:21:41-06:00
Completed At: 2026-08-05T04:21:41-06:00
File Path: `file:///Users/matt/projects/jules-burner/AG_CONTEXT.md`
Total Lines: 13
Total Bytes: 1162
Showing lines 1 to 13
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # AG_CONTEXT - Jules Quota Burner (JQB)
2: 
3: ## Architectural & System Context
4: - **Project Purpose**: Automated, local, ToS-compliant dispatch daemon designed to harvest compute value from Google Jules daily quota (100 tasks/day on a single Google AI Pro account).
5: - **Core Strategy**: High-density task discovery (Algora micro-bounties, open-source spec/doc generation, internal self-improvement), automated staging fork validation, strict 100% self-auditing telemetry, and iterative self-improvement loops.
6: - **Tech Stack**: Bun, TypeScript, `@google/jules` CLI wrapper, SQLite telemetry store, GitHub GraphQL / REST APIs.
7: - **Safety Firewall**: Staging fork isolation (`staging-*`), CI gate checks before upstream submission, rate limiting with jitter (3-7 min intervals), strict ToS compliance (no unauthorized scraping, mining, or public issue spam).
8: 
9: ## Operational Rules
10: - All file edits must be performed via `flash_lite` subagent delegation per system rules.
11: - Single account mode: Max 100 tasks/day cap strictly enforced in dispatch state.
12: - Every Jules session MUST emit structured telemetry to `data/audit.db` and trigger failure pattern classification.
13: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-05T04:21:44-06:00
Completed At: 2026-08-05T04:21:44-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/jules-burner/AG_CONTEXT.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -10,4 +10,7 @@
 - All file edits must be performed via `flash_lite` subagent delegation per system rules.
 - Single account mode: Max 100 tasks/day cap strictly enforced in dispatch state.
 - Every Jules session MUST emit structured telemetry to `data/audit.db` and trigger failure pattern classification.
+- **Never interrupt a running Jules session**: Let any active session complete fully before re-queuing or modifying its target repository. This is a project-level invariant.
+- **Jules API Mode**: All new sessions are dispatched via the Jules REST API (`jules.googleapis.com/v1alpha`) with `automationMode: AUTO_CREATE_PR` and `requirePlanApproval: false`. The CLI path (`jules remote new`) is kept as a fallback only (`USE_JULES_API=false`).
+- **Backfill script**: `bun run src/scripts/backfill_pending_prs.ts` re-submits any sessions stuck at manual plan approval in the web UI.
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-05T04:21:45-06:00
Completed At: 2026-08-05T04:21:45-06:00
Message sent to "8c249b41-cf3c-463a-85cf-65f2a79c56f6".

All tasks requested in the USER_REQUEST have been completed successfully.

*   **File 1**: Updated [`config.ts`](file:///Users/matt/projects/jules-burner/src/config.ts) with new configuration schema.
*   **File 2**: Created [`jules_api.ts`](file:///Users/matt/projects/jules-burner/src/daemon/jules_api.ts) for Jules API interaction.
*   **File 3**: Updated [`jules_cli.ts`](file:///Users/matt/projects/jules-burner/src/daemon/jules_cli.ts) with `remoteNewViaAPI`.
*   **File 4**: Updated [`dispatcher.ts`](file:///Users/matt/projects/jules-burner/src/daemon/dispatcher.ts) to support the new API workflow.
*   **File 5**: Created [`.github/workflows/auto_merge_jules_prs.yml`](file:///Users/matt/projects/jules-burner/.github/workflows/auto_merge_jules_prs.yml).
*   **File 6**: Created [`backfill_pending_prs.ts`](file:///Users/matt/projects/jules-burner/src/scripts/backfill_pending_prs.ts).
*   **File 7**: Updated [`AG_CONTEXT.md`](file:///Users/matt/projects/jules-burner/AG_CONTEXT.md) with relevant project invariants.

---
