---
title: "Please write `/Users/matt/projects/jules-burner/src/config.ts` using `write_to_file` with Overwrite: true."
date: "2026-08-07"
conversation_id: "ee33df9c-53ba-4fd8-b9e9-6a1fe1ba1f61"
source: "antigravity"
---

# Please write `/Users/matt/projects/jules-burner/src/config.ts` using `write_to_file` with Overwrite: true.

## User

Please write `/Users/matt/projects/jules-burner/src/config.ts` using `write_to_file` with Overwrite: true.

Here is the exact code:
```ts
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
  JULES_CLI_PATH: process.env.JULES_CLI_PATH || fallbackJules,
  DATABASE_PATH: process.env.DATABASE_PATH || "data/audit.db",
  HEALTH_PATH: process.env.HEALTH_PATH || "data/health.json",
};
```

---
