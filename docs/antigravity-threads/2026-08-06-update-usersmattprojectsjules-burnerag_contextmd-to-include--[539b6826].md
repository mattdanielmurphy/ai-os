---
title: "Update `/Users/matt/projects/jules-burner/AG_CONTEXT.md` to include the Dual GitHub Token rules under Operational Rules:"
date: "2026-08-06"
conversation_id: "539b6826-3b50-48a1-b43b-d8294906682d"
source: "antigravity"
---

# Update `/Users/matt/projects/jules-burner/AG_CONTEXT.md` to include the Dual GitHub Token rules under Operational Rules:

## User

Update `/Users/matt/projects/jules-burner/AG_CONTEXT.md` to include the Dual GitHub Token rules under Operational Rules:

```markdown
# AG_CONTEXT - Jules Quota Burner (JQB)

## Architectural & System Context
- **Project Purpose**: Automated, ToS-compliant dispatch daemon designed to harvest compute value from Google Jules daily quota (100 tasks/day on a single Google AI Pro account).
- **Runtime Host**: Production daemon runs on the **Oracle VPS (`ubuntu@40.233.124.200`)** under PM2 process name `jules-burner`.
- **Local Workspace**: `/Users/matt/projects/jules-burner` (SSD local drive). Avoid FUSE CloudMounter paths.
- **Core Strategy**: High-density task discovery (Algora micro-bounties, open-source spec/doc generation, internal self-improvement), automated staging fork validation, strict 100% self-auditing telemetry, and iterative self-improvement loops.
- **Tech Stack**: Bun, TypeScript, `@google/jules` CLI wrapper, SQLite telemetry store, GitHub GraphQL / REST APIs.
- **Safety Firewall**: Staging fork isolation (`staging-*`), CI gate checks before upstream submission, rate limiting with jitter (3-7 min intervals), strict ToS compliance (no unauthorized scraping, mining, or public issue spam).

## Dual GitHub Account Architecture
- **`BOT_GITHUB_TOKEN` (`ZephyrAethes`)**: Used for ALL external operations — querying live bounties, creating target forks, staging branches, Jules sessions, and submitting external PRs.
- **`PERSONAL_GITHUB_TOKEN` (`mattdanielmurphy`)**: Strictly reserved ONLY for auto-merging PRs submitted to `jules-burner` itself.

## Operational Rules
- **VPS Status Rule**: The production daemon runs on the Oracle VPS (`ubuntu@40.233.124.200`) under PM2. NEVER check local macOS LaunchAgents (`la`) or local process lists when checking daemon status. ALWAYS inspect via SSH: `ssh ubuntu@40.233.124.200 "pm2 status; pm2 logs jules-burner --lines 50 --nostream"`.
- **Token Boundaries**: All external pull requests and API operations MUST be signed/submitted under `BOT_GITHUB_TOKEN` (`ZephyrAethes`).
- **File Edits**: All file edits must be performed via `flash_lite` subagent delegation per system rules.
- **Single Account Mode**: Max 100 tasks/day cap strictly enforced in dispatch state.
- **Telemetry**: Every Jules session MUST emit structured telemetry to `data/audit.db` and trigger failure pattern classification.
```

---
