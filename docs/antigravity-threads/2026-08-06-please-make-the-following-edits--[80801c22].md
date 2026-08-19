---
title: "Please make the following edits:"
date: "2026-08-06"
conversation_id: "80801c22-4bf6-4f1f-a8cd-a511a84115a3"
source: "antigravity"
---

# Please make the following edits:

## User

Please make the following edits:

1. Update `/Users/matt/projects/jules-burner/AG_CONTEXT.md`:
Replace the contents of `/Users/matt/projects/jules-burner/AG_CONTEXT.md` with:
```markdown
# AG_CONTEXT - Jules Quota Burner (JQB)

## Architectural & System Context
- **Project Purpose**: Automated, ToS-compliant dispatch daemon designed to harvest compute value from Google Jules daily quota (100 tasks/day on a single Google AI Pro account).
- **Runtime Host**: Production daemon runs on the **Oracle VPS (`ubuntu@40.233.124.200`)** under PM2 process name `jules-burner`.
- **Local Workspace**: `/Users/matt/projects/jules-burner` (SSD local drive). Avoid FUSE CloudMounter paths.
- **Core Strategy**: High-density task discovery (Algora micro-bounties, open-source spec/doc generation, internal self-improvement), automated staging fork validation, strict 100% self-auditing telemetry, and iterative self-improvement loops.
- **Tech Stack**: Bun, TypeScript, `@google/jules` CLI wrapper, SQLite telemetry store, GitHub GraphQL / REST APIs.
- **Safety Firewall**: Staging fork isolation (`staging-*`), CI gate checks before upstream submission, rate limiting with jitter (3-7 min intervals), strict ToS compliance (no unauthorized scraping, mining, or public issue spam).

## Operational Rules
- **VPS Status Rule**: The production daemon runs on the Oracle VPS (`ubuntu@40.233.124.200`) under PM2. NEVER check local macOS LaunchAgents (`la`) or local process lists when checking daemon status. ALWAYS inspect via SSH: `ssh ubuntu@40.233.124.200 "pm2 status; pm2 logs jules-burner --lines 50 --nostream"`.
- **File Edits**: All file edits must be performed via `flash_lite` subagent delegation per system rules.
- **Single Account Mode**: Max 100 tasks/day cap strictly enforced in dispatch state.
- **Telemetry**: Every Jules session MUST emit structured telemetry to `data/audit.db` and trigger failure pattern classification.
```

2. Create file `/Users/matt/.gemini/config/rules/jules-burner.md`:
```markdown
# Jules Burner Service Location & Debugging Rules

## VPS Runtime Environment
- **Production Host**: Oracle VPS (`ubuntu@40.233.124.200`).
- **Process Manager**: PM2 process name `jules-burner`.
- **Status & Logs Probe Command**:
  `ssh ubuntu@40.233.124.200 "pm2 status; pm2 logs jules-burner --lines 50 --nostream"`

## Prohibited Local Probes for Jules Burner
- DO NOT run `la status jules-burner` or inspect local macOS `/Users/matt/Library/LaunchAgents/` for `jules-burner`.
- DO NOT check local `ps aux` for `index.ts` daemon execution when diagnosing production daemon status — the production daemon runs remotely on the VPS under PM2.

## Local Repository Location
- Local path: `/Users/matt/projects/jules-burner`
- Avoid FUSE / CloudMounter mounted paths (`/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/...`) to prevent file read timeouts.
```

---
