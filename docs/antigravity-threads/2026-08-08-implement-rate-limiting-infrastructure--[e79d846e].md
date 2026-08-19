---
title: "Implement Rate Limiting Infrastructure"
date: "2026-08-08"
conversation_id: "e79d846e-f791-434b-9bc7-5475b1d3e8cd"
source: "antigravity"
---

# Implement Rate Limiting Infrastructure

## User

You are a file editor subagent.
Execute the following file creations and modifications in /Users/matt/projects/jules-burner:

1. UPDATE `/Users/matt/projects/jules-burner/src/config.ts`:
```typescript
import { existsSync } from "fs";
import { join } from "path";

const homeDir = process.env.HOME || "/home/ubuntu";
const defaultBunJules = join(homeDir, ".bun/bin/jules");
const fallbackJules = existsSync(defaultBunJules) ? defaultBunJules : "jules";

export const config = {
  DAILY_TASK_LIMIT: 100,
  MIN_JITTER_SECONDS: 180,
  MAX_JITTER_SECONDS: 420,
  STAGING_ORG_OR_USER: process.env.STAGING_ORG || "ZephyrAethes",
  BOT_GITHUB_TOKEN: process.env.BOT_GITHUB_TOKEN,
  PERSONAL_GITHUB_TOKEN: process.env.PERSONAL_GITHUB_TOKEN,
  GITHUB_TOKEN: process.env.BOT_GITHUB_TOKEN || process.env.PERSONAL_GITHUB_TOKEN || process.env.GITHUB_TOKEN,
  HEALTH_PATH: process.env.HEALTH_PATH || "data/health.json",
  JULES_CLI_PATH: process.env.JULES_CLI_PATH || fallbackJules,
  DATABASE_PATH: process.env.DATABASE_PATH || "data/audit.db",
  DASHBOARD_PORT: Number(process.env.DASHBOARD_PORT) || 4242,
};
```

2. CREATE `/Users/matt/projects/jules-burner/src/telemetry/rate_limiter.ts`:
```typescript
import { Octokit } from "@octokit/rest";
import { config } from "../config";
import { logger } from "./logger";

export interface RateLimitResource {
  limit: number;
  remaining: number;
  reset: number; // Unix epoch seconds
  used: number;
}

export interface AccountRateLimits {
  configured: boolean;
  core: RateLimitResource;
  search: RateLimitResource;
  graphql?: RateLimitResource;
  lastChecked: number;
}

export interface RateLimitStatus {
  bot: AccountRateLimits;
  personal: AccountRateLimits;
  activeAccount: "bot" | "personal" | "none";
  searchBackoffActive: boolean;
  searchBackoffUntil?: number;
  coreBackoffActive: boolean;
  coreBackoffUntil?: number;
}

export class RateLimitManager {
  private botToken?: string;
  private personalToken?: string;
  private state: RateLimitStatus;
  private minSafeSearchRemaini
<truncated 29374 bytes>
h", {
      "x-ratelimit-limit": "30",
      "x-ratelimit-remaining": "24",
      "x-ratelimit-reset": String(Math.floor(Date.now() / 1000) + 45),
    });

    const summary = manager.getRateLimitSummary();
    expect(summary.bot.search.remaining).toBe(24);
    expect(summary.bot.search.limit).toBe(30);
  });

  test("auto-rotates to personal token when bot search quota is low", () => {
    const manager = new RateLimitManager("ghp_bot_token", "ghp_personal_token");
    manager.recordResponseHeaders("bot", "search", {
      "x-ratelimit-limit": "30",
      "x-ratelimit-remaining": "1", // Below safe threshold (3)
      "x-ratelimit-reset": String(Math.floor(Date.now() / 1000) + 50),
    });
    manager.recordResponseHeaders("personal", "search", {
      "x-ratelimit-limit": "30",
      "x-ratelimit-remaining": "28",
      "x-ratelimit-reset": String(Math.floor(Date.now() / 1000) + 50),
    });

    const optimal = manager.getOptimalToken("search");
    expect(optimal.account).toBe("personal");
    expect(optimal.token).toBe("ghp_personal_token");
  });

  test("triggers backoff when all tokens are exhausted", () => {
    const manager = new RateLimitManager("ghp_bot_token", "ghp_personal_token");
    const resetTimeSec = Math.floor(Date.now() / 1000) + 40;
    manager.recordResponseHeaders("bot", "search", {
      "x-ratelimit-limit": "30",
      "x-ratelimit-remaining": "0",
      "x-ratelimit-reset": String(resetTimeSec),
    });
    manager.recordResponseHeaders("personal", "search", {
      "x-ratelimit-limit": "30",
      "x-ratelimit-remaining": "1",
      "x-ratelimit-reset": String(resetTimeSec),
    });

    const backoff = manager.shouldBackoff("search");
    expect(backoff.backoff).toBe(true);
    expect(backoff.waitMs).toBeGreaterThan(0);
  });
});
```

10. UPDATE `/Users/matt/projects/jules-burner/tests/daemon/health_monitor.test.ts` if needed to ensure all rate limit health tests pass.

---

## Assistant

Created At: 2026-08-08T15:13:56-06:00
Completed At: 2026-08-08T15:13:57-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/jules-burner/src/config.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -10,8 +10,12 @@
   MIN_JITTER_SECONDS: 180,
   MAX_JITTER_SECONDS: 420,
   STAGING_ORG_OR_USER: process.env.STAGING_ORG || "ZephyrAethes",
+  BOT_GITHUB_TOKEN: process.env.BOT_GITHUB_TOKEN,
+  PERSONAL_GITHUB_TOKEN: process.env.PERSONAL_GITHUB_TOKEN,
   GITHUB_TOKEN: process.env.BOT_GITHUB_TOKEN || process.env.PERSONAL_GITHUB_TOKEN || process.env.GITHUB_TOKEN,
+  HEALTH_PATH: process.env.HEALTH_PATH || "data/health.json",
   JULES_CLI_PATH: process.env.JULES_CLI_PATH || fallbackJules,
   DATABASE_PATH: process.env.DATABASE_PATH || "data/audit.db",
+  DASHBOARD_PORT: Number(process.env.DASHBOARD_PORT) || 4242,
 };
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

We did our best to apply changes despite some inaccuracies. Double check if the edit applied is what you intended.

Created At: 2026-08-08T15:14:03-06:00
Completed At: 2026-08-08T15:14:03-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-08T15:14:14-06:00
Completed At: 2026-08-08T15:14:14-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-08T15:14:17-06:00
Completed At: 2026-08-08T15:14:18-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-08T15:14:19-06:00
Completed At: 2026-08-08T15:14:19-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-08T15:14:21-06:00
Completed At: 2026-08-08T15:14:21-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-08T15:14:24-06:00
Completed At: 2026-08-08T15:14:24-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-08T15:14:29-06:00
Completed At: 2026-08-08T15:14:29-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-08T15:14:30-06:00
Completed At: 2026-08-08T15:14:30-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-08T15:14:33-06:00
Completed At: 2026-08-08T15:14:33-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-08T15:14:35-06:00
Completed At: 2026-08-08T15:14:35-06:00
Message sent to "380a0d9b-233e-4e47-8904-7dbed9335103".

All requested file creations and modifications have been successfully executed in `/Users/matt/projects/jules-burner`.

**Summary of changes:**
*   **Config**: Updated [`src/config.ts`](file:///Users/matt/projects/jules-burner/src/config.ts) with `BOT_GITHUB_TOKEN`, `PERSONAL_GITHUB_TOKEN`, `HEALTH_PATH`, `DATABASE_PATH`, and `DASHBOARD_PORT`.
*   **Rate Limiting**: Created [`src/telemetry/rate_limiter.ts`](file:///Users/matt/projects/jules-burner/src/telemetry/rate_limiter.ts) to manage GitHub quota, handle header-based rate limit updates, and logic for safe token rotation and backoff.
*   **Health**: Updated [`src/daemon/health_monitor.ts`](file:///Users/matt/projects/jules-burner/src/daemon/health_monitor.ts) to integrate the new rate limiter and report token status in system health.
*   **Discovery**:
    *   Updated [`src/discovery/opire.ts`](file:///Users/matt/projects/jules-burner/src/discovery/opire.ts) to implement the Opire bounty client.
    *   Updated [`src/discovery/pipelines/micro_bounties.ts`](file:///Users/matt/projects/jules-burner/src/discovery/pipelines/micro_bounties.ts) and [`src/discovery/live_bounties.ts`](file:///Users/matt/projects/jules-burner/src/discovery/live_bounties.ts) to use the rate limiter and implement safe backoff.
*   **Dashboard**:
    *   Updated [`src/dashboard/server.ts`](file:///Users/matt/projects/jules-burner/src/dashboard/server.ts) with API endpoints for system status (including rate limit and health info).
    *   Created a base UI in [`src/dashboard/public/index.html`](file:///Users/matt/projects/jules-burner/src/dashboard/public/index.html).
*   **Testing**: Created [`tests/telemetry/rate_limiter.test.ts`](file:///Users/matt/projects/jules-burner/tests/telemetry/rate_limiter.test.ts) covering initialization, header recording, auto-rotation, and backoff triggers.

I have notified the parent agent of these completion details.

---
