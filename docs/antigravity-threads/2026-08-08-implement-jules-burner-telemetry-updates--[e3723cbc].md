---
title: "Implement Jules Burner Telemetry Updates"
date: "2026-08-08"
conversation_id: "e3723cbc-767d-49af-8c49-f8d0c04f0f17"
source: "antigravity"
---

# Implement Jules Burner Telemetry Updates

## User

You are a file editor subagent.
Perform the following file updates in /Users/matt/projects/jules-burner:

1. UPDATE `/Users/matt/projects/jules-burner/src/telemetry/rate_limiter.ts`:
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
  lastError?: string;
}

export interface RateLimitStatus {
  bot: AccountRateLimits;
  personal: AccountRateLimits;
  activeAccount: "bot" | "personal" | "none";
  searchBackoffActive: boolean;
  searchBackoffUntil?: number;
  coreBackoffActive: boolean;
  coreBackoffUntil?: number;
  lastError?: string;
}

export class RateLimitManager {
  private botToken?: string;
  private personalToken?: string;
  private state: RateLimitStatus;
  private minSafeSearchRemaining = 3;
  private minSafeCoreRemaining = 25;

  constructor(botToken?: string, personalToken?: string) {
    this.botToken = botToken ?? config.BOT_GITHUB_TOKEN;
    this.personalToken = personalToken ?? config.PERSONAL_GITHUB_TOKEN;

    this.state = {
      bot: {
        configured: Boolean(this.botToken),
        core: { limit: 5000, remaining: this.botToken ? 5000 : 0, reset: 0, used: 0 },
        search: { limit: 30, remaining: this.botToken ? 30 : 0, reset: 0, used: 0 },
        lastChecked: 0,
      },
      personal: {
        configured: Boolean(this.personalToken),
        core: { limit: 5000, remaining: this.personalToken ? 5000 : 0, reset: 0, used: 0 },
        search: { limit: 30, remaining: this.personalToken ? 30 : 0, reset: 0, used: 0 },
        lastChecked: 0,
      },
      activeAccount: this.botToken ? "bot" : this.personalToken ? "personal" : "none",
      searchBackoffActive: false,
      coreBackoffActive: false,

<truncated 58335 bytes>
, () => {
    const manager = new RateLimitManager("ghp_bot_token", "ghp_personal_token");
    manager.recordResponseHeaders("bot", "search", {
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

---

## Assistant

Created At: 2026-08-08T15:16:04-06:00
Completed At: 2026-08-08T15:16:04-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-08T15:16:09-06:00
Completed At: 2026-08-08T15:16:09-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-08T15:16:39-06:00
Completed At: 2026-08-08T15:16:39-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-08T15:16:42-06:00
Completed At: 2026-08-08T15:16:42-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-08T15:16:44-06:00
Completed At: 2026-08-08T15:16:44-06:00
Message sent to "380a0d9b-233e-4e47-8904-7dbed9335103".

The requested file updates for `/Users/matt/projects/jules-burner` have been completed successfully.

The following files were updated or created:
*   [rate_limiter.ts](file:///Users/matt/projects/jules-burner/src/telemetry/rate_limiter.ts)
*   [health_monitor.ts](file:///Users/matt/projects/jules-burner/src/daemon/health_monitor.ts)
*   [index.html](file:///Users/matt/projects/jules-burner/src/dashboard/public/index.html)
*   [rate_limiter.test.ts](file:///Users/matt/projects/jules-burner/tests/telemetry/rate_limiter.test.ts)

I have reported these changes to the parent agent.

---
