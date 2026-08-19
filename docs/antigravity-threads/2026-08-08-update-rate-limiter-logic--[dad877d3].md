---
title: "Update Rate Limiter Logic"
date: "2026-08-08"
conversation_id: "dad877d3-e36e-46db-a404-da276ae84dc7"
source: "antigravity"
---

# Update Rate Limiter Logic

## User

You are a file editor subagent.
In `/Users/matt/projects/jules-burner/src/telemetry/rate_limiter.ts`:
Update `syncRateLimits` so `bot` and `personal` resolve directly to `overrideBotToken !== undefined ? overrideBotToken : config.BOT_GITHUB_TOKEN` and `overridePersonalToken !== undefined ? overridePersonalToken : config.PERSONAL_GITHUB_TOKEN`.
And ensure that `this.state.lastError` preserves the bot error if bot is configured:
```typescript
  public async syncRateLimits(
    overrideBotToken?: string,
    overridePersonalToken?: string
  ): Promise<RateLimitStatus> {
    const now = Date.now();
    const bot = overrideBotToken !== undefined ? overrideBotToken : config.BOT_GITHUB_TOKEN;
    const personal = overridePersonalToken !== undefined ? overridePersonalToken : config.PERSONAL_GITHUB_TOKEN;

    this.botToken = bot;
    this.personalToken = personal;
    this.state.bot.configured = Boolean(bot);
    this.state.personal.configured = Boolean(personal);
    this.state.lastError = undefined;

    if (bot) {
      try {
        const octokit = new Octokit({ auth: bot });
        const res = await octokit.rest.rateLimit.get();
        const core = res.data?.resources?.core ?? { limit: 5000, remaining: 5000, reset: 0, used: 0 };
        const search = res.data?.resources?.search ?? { limit: 30, remaining: 30, reset: 0, used: 0 };
        this.state.bot.core = {
          limit: core.limit ?? 5000,
          remaining: core.remaining ?? 5000,
          reset: core.reset ?? 0,
          used: core.used ?? 0,
        };
        this.state.bot.search = {
          limit: search.limit ?? 30,
          remaining: search.remaining ?? 30,
          reset: search.reset ?? 0,
          used: search.used ?? 0,
        };
        if (res.data?.resources?.graphql) {
          this.state.bot.graphql = res.data.resources.graphql;
        }
        this.state.bot.lastChecked = now;
        this.state.bot.lastError = undefined;
      } catch (err: any) {
        this.state.bot.core.remaining = 0;
        this.state.bot.search.remaining = 0;
        this.state.bot.lastError = `Bot GitHub Token error: ${err.message || String(err)}`;
        this.state.lastError = this.state.bot.lastError;
        logger.warn("RATE_LIMIT", this.state.bot.lastError);
      }
    } else {
      this.state.bot.core.remaining = 0;
      this.state.bot.search.remaining = 0;
    }

    if (personal) {
      try {
        const octokit = new Octokit({ auth: personal });
        const res = await octokit.rest.rateLimit.get();
        const core = res.data?.resources?.core ?? { limit: 5000, remaining: 5000, reset: 0, used: 0 };
        const search = res.data?.resources?.search ?? { limit: 30, remaining: 30, reset: 0, used: 0 };
        this.state.personal.core = {
          limit: core.limit ?? 5000,
          remaining: core.remaining ?? 5000,
          reset: core.reset ?? 0,
          used: core.used ?? 0,
        };
        this.state.personal.search = {
          limit: search.limit ?? 30,
          remaining: search.remaining ?? 30,
          reset: search.reset ?? 0,
          used: search.used ?? 0,
        };
        if (res.data?.resources?.graphql) {
          this.state.personal.graphql = res.data.resources.graphql;
        }
        this.state.personal.lastChecked = now;
        this.state.personal.lastError = undefined;
      } catch (err: any) {
        this.state.personal.core.remaining = 0;
        this.state.personal.search.remaining = 0;
        this.state.personal.lastError = `Personal GitHub Token error: ${err.message || String(err)}`;
        if (!this.state.lastError) {
          this.state.lastError = this.state.personal.lastError;
        }
        logger.warn("RATE_LIMIT", this.state.personal.lastError);
      }
    } else {
      this.state.personal.core.remaining = 0;
      this.state.personal.search.remaining = 0;
    }

    this.updateBackoffState();
    return this.state;
  }
```

---

## Assistant

Created At: 2026-08-08T15:16:58-06:00
Completed At: 2026-08-08T15:16:58-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/telemetry/rate_limiter.ts`
Total Lines: 254
Total Bytes: 9803
Showing lines 1 to 254
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import { Octokit } from "@octokit/rest";
2: import { config } from "../config";
3: import { logger } from "./logger";
4: 
5: export interface RateLimitResource {
6:   limit: number;
7:   remaining: number;
8:   reset: number; // Unix epoch seconds
9:   used: number;
10: }
11: 
12: export interface AccountRateLimits {
13:   configured: boolean;
14:   core: RateLimitResource;
15:   search: RateLimitResource;
16:   graphql?: RateLimitResource;
17:   lastChecked: number;
18:   lastError?: string;
19: }
20: 
21: export interface RateLimitStatus {
22:   bot: AccountRateLimits;
23:   personal: AccountRateLimits;
24:   activeAccount: "bot" | "personal" | "none";
25:   searchBackoffActive: boolean;
26:   searchBackoffUntil?: number;
27:   coreBackoffActive: boolean;
28:   coreBackoffUntil?: number;
29:   lastError?: string;
30: }
31: 
32: export class RateLimitManager {
33:   private botToken?: string;
34:   private personalToken?: string;
35:   private state: RateLimitStatus;
36:   private minSafeSearchRemaining = 3;
37:   private minSafeCoreRemaining = 25;
38: 
39:   constructor(botToken?: string, personalToken?: string) {
40:     this.botToken = botToken ?? config.BOT_GITHUB_TOKEN;
41:     this.personalToken = personalToken ?? config.PERSONAL_GITHUB_TOKEN;
42: 
43:     this.state = {
44:       bot: {
45:         configured: Boolean(this.botToken),
46:         core: { limit: 5000, remaining: this.botToken ? 5000 : 0, reset: 0, used: 0 },
47:         search: { limit: 30, remaining: this.botToken ? 30 : 0, reset: 0, used: 0 },
48:         lastChecked: 0,
49:       }
<truncated 7414 bytes>
his.state.bot.search?.remaining ?? 0) : (this.state.bot.core?.remaining ?? 0);
208:     const personalQuota = resource === "search" ? (this.state.personal.search?.remaining ?? 0) : (this.state.personal.core?.remaining ?? 0);
209: 
210:     if (this.state.bot.configured && botQuota >= this.minSafeSearchRemaining && botQuota >= personalQuota) {
211:       this.state.activeAccount = "bot";
212:       return { token: this.botToken, account: "bot" };
213:     }
214: 
215:     if (this.state.personal.configured && personalQuota >= this.minSafeSearchRemaining) {
216:       this.state.activeAccount = "personal";
217:       return { token: this.personalToken, account: "personal" };
218:     }
219: 
220:     if (this.state.bot.configured && this.botToken) {
221:       return { token: this.botToken, account: "bot" };
222:     }
223: 
224:     if (this.state.personal.configured && this.personalToken) {
225:       return { token: this.personalToken, account: "personal" };
226:     }
227: 
228:     return { token: config.GITHUB_TOKEN, account: "none" };
229:   }
230: 
231:   public shouldBackoff(resource: "core" | "search" = "search"): { backoff: boolean; waitMs: number } {
232:     this.updateBackoffState();
233:     const now = Date.now();
234: 
235:     if (resource === "search" && this.state.searchBackoffActive && this.state.searchBackoffUntil) {
236:       const waitMs = Math.max(0, this.state.searchBackoffUntil - now);
237:       return { backoff: true, waitMs };
238:     }
239: 
240:     if (resource === "core" && this.state.coreBackoffActive && this.state.coreBackoffUntil) {
241:       const waitMs = Math.max(0, this.state.coreBackoffUntil - now);
242:       return { backoff: true, waitMs };
243:     }
244: 
245:     return { backoff: false, waitMs: 0 };
246:   }
247: 
248:   public getRateLimitSummary(): RateLimitStatus {
249:     return this.state;
250:   }
251: }
252: 
253: export const rateLimitManager = new RateLimitManager();
254: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-08T15:17:00-06:00
Completed At: 2026-08-08T15:17:00-06:00
The following changes were made by the multi_replace_file_content tool to: /Users/matt/projects/jules-burner/src/telemetry/rate_limiter.ts. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -64,8 +64,8 @@
     overridePersonalToken?: string
   ): Promise<RateLimitStatus> {
     const now = Date.now();
-    const bot = overrideBotToken !== undefined ? overrideBotToken : (config.BOT_GITHUB_TOKEN ?? this.botToken);
-    const personal = overridePersonalToken !== undefined ? overridePersonalToken : (config.PERSONAL_GITHUB_TOKEN ?? this.personalToken);
+    const bot = overrideBotToken !== undefined ? overrideBotToken : config.BOT_GITHUB_TOKEN;
+    const personal = overridePersonalToken !== undefined ? overridePersonalToken : config.PERSONAL_GITHUB_TOKEN;
 
     this.botToken = bot;
     this.personalToken = personal;
@@ -133,7 +133,9 @@
         this.state.personal.core.remaining = 0;
         this.state.personal.search.remaining = 0;
         this.state.personal.lastError = `Personal GitHub Token error: ${err.message || String(err)}`;
-        this.state.lastError = this.state.personal.lastError;
+        if (!this.state.lastError) {
+          this.state.lastError = this.state.personal.lastError;
+        }
         logger.warn("RATE_LIMIT", this.state.personal.lastError);
       }
     } else {
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T15:17:01-06:00
Completed At: 2026-08-08T15:17:01-06:00
Message sent to "380a0d9b-233e-4e47-8904-7dbed9335103".

Created At: 2026-08-08T15:17:03-06:00
Completed At: 2026-08-08T15:17:03-06:00
Message sent to "380a0d9b-233e-4e47-8904-7dbed9335103".

The requested updates to `/Users/matt/projects/jules-burner/src/telemetry/rate_limiter.ts` have been completed successfully.

- **Token Resolution**: The `syncRateLimits` method now correctly uses `overrideBotToken !== undefined ? overrideBotToken : config.BOT_GITHUB_TOKEN` and the corresponding logic for the `personal` token.
- **Error Handling**: `this.state.lastError` now preserves any existing bot error and only falls back to the personal error if a bot error hasn't already been set.

I have communicated these changes to the parent agent.

---
