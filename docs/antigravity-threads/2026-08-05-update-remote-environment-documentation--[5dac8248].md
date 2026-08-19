---
title: "Update Remote Environment Documentation"
date: "2026-08-05"
conversation_id: "5dac8248-262a-402f-b18c-e1c238d8a21b"
source: "antigravity"
---

# Update Remote Environment Documentation

## User

Append a prominent, bold section to `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/AG_CONTEXT.md`:

```markdown

## ⚠️ CRITICAL EXECUTION ENVIRONMENT RULE (REMOTE VPS)
- **Local Filesystem vs Remote Host**: This workspace is accessed via an SFTP mount (`CloudMounter-OracleVPS`). File edits directly write to the remote VPS, BUT running `run_command` in Antigravity executes commands locally on the host Mac by default!
- **SSH Command Rule**: ALL shell commands, background tasks, service management, and script executions MUST be run over SSH on the VPS via `ssh oracle-minecraft-server "<command>"`.
- **Process Management**: ALWAYS use `pm2` on the VPS via `ssh oracle-minecraft-server "export PATH=\$PATH:~/.bun/bin; pm2 ..."` for persistent background tasks or cron services. NEVER run cron tools (`schedule`) or background daemons locally in Antigravity for this repository.
```

Make sure to append this cleanly to `AG_CONTEXT.md` using `replace_file_content` or `write_to_file`.

---

## Assistant

Created At: 2026-08-05T17:01:57-06:00
Completed At: 2026-08-05T17:01:57-06:00
File Path: `file:///Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/AG_CONTEXT.md`
Total Lines: 13
Total Bytes: 1162
Showing lines 1 to 13
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: # AG_CONTEXT - Jules Quota Burner (JQB)
2: 
3: ## Architectural & System Context
4: - **Project Purpose**: Automated, local, ToS-compliant dispatch daemon designed to harvest compute value from Google Jules daily quota (100 tasks/day on a single Google AI Pro account).
5: - **Core Strategy**: High-density task discovery (Algora micro-bounties, open-source spec/doc generation, internal self-improvement), automated staging fork validation, strict 100% self-auditing telemetry, and iterative self-improvement loops.
6: - **Tech Stack**: Bun, TypeScript, `@google/jules` CLI wrapper, SQLite telemetry store, GitHub GraphQL / REST APIs.
7: - **Safety Firewall**: Staging fork isolation (`staging-*`), CI gate checks before upstream submission, rate limiting with jitter (3-7 min intervals), strict ToS compliance (no unauthorized scraping, mining, or public issue spam).
8: 
9: ## Operational Rules
10: - All file edits must be performed via `flash_lite` subagent delegation per system rules.
11: - Single account mode: Max 100 tasks/day cap strictly enforced in dispatch state.
12: - Every Jules session MUST emit structured telemetry to `data/audit.db` and trigger failure pattern classification.
13: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-05T17:01:59-06:00
Completed At: 2026-08-05T17:01:59-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/AG_CONTEXT.md. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -10,4 +10,9 @@
 - All file edits must be performed via `flash_lite` subagent delegation per system rules.
 - Single account mode: Max 100 tasks/day cap strictly enforced in dispatch state.
 - Every Jules session MUST emit structured telemetry to `data/audit.db` and trigger failure pattern classification.
+
+## ⚠️ CRITICAL EXECUTION ENVIRONMENT RULE (REMOTE VPS)
+- **Local Filesystem vs Remote Host**: This workspace is accessed via an SFTP mount (`CloudMounter-OracleVPS`). File edits directly write to the remote VPS, BUT running `run_command` in Antigravity executes commands locally on the host Mac by default!
+- **SSH Command Rule**: ALL shell commands, background tasks, service management, and script executions MUST be run over SSH on the VPS via `ssh oracle-minecraft-server "<command>"`.
+- **Process Management**: ALWAYS use `pm2` on the VPS via `ssh oracle-minecraft-server "export PATH=\$PATH:~/.bun/bin; pm2 ..."` for persistent background tasks or cron services. NEVER run cron tools (`schedule`) or background daemons locally in Antigravity for this repository.
 
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

Created At: 2026-08-05T17:02:00-06:00
Completed At: 2026-08-05T17:02:00-06:00
Message sent to "b5975665-c0ec-416e-ad2f-f24a34652c81".

The requested section has been successfully appended to `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/AG_CONTEXT.md`.

---
