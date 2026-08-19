---
title: "Update Project Operational Rules"
date: "2026-08-09"
conversation_id: "eb88185b-c986-4454-bf5a-2c83b3d38837"
source: "antigravity"
---

# Update Project Operational Rules

## User

Add the mandatory rule against creating stubs/mocks to `/Volumes/127.0.0.1/projects/jules-burner/AG_CONTEXT.md` under `## Operational Rules`:

Append:
`- **NO MOCKS / NO STUBS RULE**: NEVER write placeholder, stub, or mock implementations when requested to build a feature or integration. Implement fully functional, production-ready code with real network calls, protocols, and authentic error handling.`

Use `replace_file_content` on `/Volumes/127.0.0.1/projects/jules-burner/AG_CONTEXT.md`.

---

## Assistant

Created At: 2026-08-08T20:47:25-06:00
Completed At: 2026-08-08T20:47:25-06:00
File Path: `file:///Volumes/127.0.0.1/projects/jules-burner/AG_CONTEXT.md`
Total Lines: 24
Total Bytes: 2055
Showing lines 1 to 24
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # AG_CONTEXT - Jules Quota Burner (JQB)
2: 
3: ## ⚠️ CRITICAL: DEPLOYMENT ENVIRONMENT
4: - **This project runs on a VPS, NOT locally.** The local mount at `/Volumes/127.0.0.1/projects/jules-burner` is SSHFS from the VPS.
5: - **VPS SSH**: `ssh -i ~/.ssh/Oracle-Minecraft-Server-SSH.key ubuntu@40.233.124.200`
6: - **VPS project path**: `~/projects/jules-burner`
7: - **All servers (dashboard, daemon) run ON THE VPS** via SSH. Any restart, process check, or `bun run` MUST be done over SSH.
8: - **Process manager**: PM2 via `~/.bun/bin/pm2`. The `jules-burner` PM2 process (id 0) runs `src/index.ts` which starts BOTH the daemon AND the dashboard server.
9: - **After any code change**: `~/.bun/bin/pm2 restart jules-burner` (via SSH). This is the ONLY way to apply code changes.
10: - **Dashboard URL**: `http://100.123.57.17:4242` (Tailscale)
11: - **To check status**: `~/.bun/bin/pm2 list`
12: - **To view logs**: `~/.bun/bin/pm2 logs jules-burner --lines 50`
13: 
14: ## Architectural & System Context
15: - **Project Purpose**: Automated, local, ToS-compliant dispatch daemon designed to harvest compute value from Google Jules daily quota (100 tasks/day on a single Google AI Pro account).
16: - **Core Strategy**: High-density task discovery (Algora micro-bounties, open-source spec/doc generation, internal self-improvement), automated staging fork validation, strict 100% self-auditing telemetry, and iterative self-improvement loops.
17: - **Tech Stack**: Bun, TypeScript, `@google/jules` CLI wrapper, SQLite telemetry store, GitHub GraphQL / REST APIs.
18: - **Safety Firewall**: Staging fork isolation (`staging-*`), CI gate checks before upstream submission, rate limiting with jitter (3-7 min intervals), strict ToS compliance (no unauthorized scraping, mining, or public issue spam).
19: 
20: ## Operational Rules
21: - All file edits must be performed via `flash_lite` subagent delegation per system rules.
22: - Single account mode: Max 100 tasks/day cap strictly enforced in dispatch state.
23: - Every Jules session MUST emit structured telemetry to `data/audit.db` and trigger failure pattern classification.
24: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-08T20:48:13-06:00
Completed At: 2026-08-08T20:48:13-06:00
The following changes were made by the replace_file_content tool to: /Volumes/127.0.0.1/projects/jules-burner/AG_CONTEXT.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -21,4 +21,5 @@
 - All file edits must be performed via `flash_lite` subagent delegation per system rules.
 - Single account mode: Max 100 tasks/day cap strictly enforced in dispatch state.
 - Every Jules session MUST emit structured telemetry to `data/audit.db` and trigger failure pattern classification.
+- **NO MOCKS / NO STUBS RULE**: NEVER write placeholder, stub, or mock implementations when requested to build a feature or integration. Implement fully functional, production-ready code with real network calls, protocols, and authentic error handling.
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-08T20:48:14-06:00
Completed At: 2026-08-08T20:48:14-06:00
Message sent to "c1a99726-cbe8-4216-b6f3-f5bd05ba57fe".

The rule against creating stubs/mocks has been added to `/Volumes/127.0.0.1/projects/jules-burner/AG_CONTEXT.md`.

---
