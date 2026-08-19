---
title: "Update Health Monitor Logic"
date: "2026-08-07"
conversation_id: "8e3fb9cf-d1a0-4039-9e68-aec768b2f7dd"
source: "antigravity"
---

# Update Health Monitor Logic

## User

In `/Users/matt/projects/jules-burner/src/daemon/health_monitor.ts`, replace lines 80 to 88 with:

```ts
    const hasConfiguredTokens = Boolean(config.BOT_GITHUB_TOKEN || config.PERSONAL_GITHUB_TOKEN || config.GITHUB_TOKEN);
    if (hasConfiguredTokens) {
      const botExhausted = config.BOT_GITHUB_TOKEN && (health.tokens.botRateLimitRemaining === undefined || health.tokens.botRateLimitRemaining <= 0);
      const personalExhausted = config.PERSONAL_GITHUB_TOKEN && (health.tokens.personalRateLimitRemaining === undefined || health.tokens.personalRateLimitRemaining <= 0);
      
      if (botExhausted && personalExhausted) {
        health.healthy = false;
        health.needsHumanIntervention = true;
        health.humanInterventionReason = "GitHub rate limits are fully exhausted on configured bot and personal accounts.";
      }
    }
```

Please update the file directly using replace_file_content.

---

## Assistant

Created At: 2026-08-07T12:16:23-06:00
Completed At: 2026-08-07T12:16:23-06:00
File Path: `file:///Users/matt/projects/jules-burner/src/daemon/health_monitor.ts`
Total Lines: 175
Total Bytes: 5856
Showing lines 80 to 88
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
80:     const noValidTokens =
81:       (!health.tokens.botRateLimitRemaining || health.tokens.botRateLimitRemaining <= 0) &&
82:       (!health.tokens.personalRateLimitRemaining || health.tokens.personalRateLimitRemaining <= 0);
83: 
84:     if (noValidTokens && !config.GITHUB_TOKEN) {
85:       health.healthy = false;
86:       health.needsHumanIntervention = true;
87:       health.humanInterventionReason = "GitHub tokens are missing or rate limits are fully exhausted on both bot and personal accounts.";
88:     }
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

---
