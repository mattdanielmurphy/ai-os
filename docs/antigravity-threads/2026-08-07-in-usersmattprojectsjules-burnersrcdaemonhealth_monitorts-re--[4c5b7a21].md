---
title: "In `/Users/matt/projects/jules-burner/src/daemon/health_monitor.ts`, replace lines 80 to 88 with:"
date: "2026-08-07"
conversation_id: "4c5b7a21-7c1b-4032-990d-21b9f316f654"
source: "antigravity"
---

# In `/Users/matt/projects/jules-burner/src/daemon/health_monitor.ts`, replace lines 80 to 88 with:

## User

In `/Users/matt/projects/jules-burner/src/daemon/health_monitor.ts`, replace lines 80 to 88 with:

```ts
    const hasConfiguredTokens = Boolean(config.BOT_GITHUB_TOKEN || config.PERSONAL_GITHUB_TOKEN || config.GITHUB_TOKEN);
    if (hasConfiguredTokens) {
      const botExhausted = Boolean(config.BOT_GITHUB_TOKEN) && (health.tokens.botRateLimitRemaining === undefined || health.tokens.botRateLimitRemaining <= 0);
      const personalExhausted = Boolean(config.PERSONAL_GITHUB_TOKEN) && (health.tokens.personalRateLimitRemaining === undefined || health.tokens.personalRateLimitRemaining <= 0);
      
      if (botExhausted && personalExhausted) {
        health.healthy = false;
        health.needsHumanIntervention = true;
        health.humanInterventionReason = "GitHub rate limits are fully exhausted on configured bot and personal accounts.";
      }
    }
```

Make sure the old `const noValidTokens = ... if (noValidTokens && !config.GITHUB_TOKEN)` code is completely removed.

---
