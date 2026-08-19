---
title: "In `/Users/matt/projects/jules-burner/src/daemon/health_monitor.ts`, replace lines 58 to 89 with this exact clean logic:"
date: "2026-08-07"
conversation_id: "d2a597dc-2951-4e73-956d-9268a37777f4"
source: "antigravity"
---

# In `/Users/matt/projects/jules-burner/src/daemon/health_monitor.ts`, replace lines 58 to 89 with this exact clean logic:

## User

In `/Users/matt/projects/jules-burner/src/daemon/health_monitor.ts`, replace lines 58 to 89 with this exact clean logic:

```ts
    // 1. Check GitHub tokens & rate limits if configured
    let tokensChecked = false;
    let anyTokenValid = false;

    if (config.BOT_GITHUB_TOKEN) {
      tokensChecked = true;
      try {
        const botOctokit = new Octokit({ auth: config.BOT_GITHUB_TOKEN, request: { timeout: 3000 } });
        const res = await botOctokit.rest.rateLimit.get();
        health.tokens.botRateLimitRemaining = res.data.resources.core.remaining;
        if (res.data.resources.core.remaining > 0) {
          anyTokenValid = true;
        }
      } catch (err: any) {
        health.tokens.botRateLimitRemaining = 0;
        health.lastError = `Bot GitHub Token error: ${err.message}`;
      }
    }

    if (config.PERSONAL_GITHUB_TOKEN) {
      tokensChecked = true;
      try {
        const personalOctokit = new Octokit({ auth: config.PERSONAL_GITHUB_TOKEN, request: { timeout: 3000 } });
        const res = await personalOctokit.rest.rateLimit.get();
        health.tokens.personalRateLimitRemaining = res.data.resources.core.remaining;
        if (res.data.resources.core.remaining > 0) {
          anyTokenValid = true;
        }
      } catch (err: any) {
        health.tokens.personalRateLimitRemaining = 0;
      }
    }

    if (tokensChecked && !anyTokenValid) {
      health.healthy = false;
      health.needsHumanIntervention = true;
      health.humanInterventionReason = "GitHub rate limits are fully exhausted on configured bot and personal accounts.";
    }
```

Please update the file directly using replace_file_content.

---
