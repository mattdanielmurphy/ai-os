---
name: claude-md-override
description: CLAUDE.md identity matrix takes precedence over native Claude local memory
metadata:
  type: reference
---

# CLAUDE.md Override — Native Memory Bypass

The workspace identity matrix defined in this project's `CLAUDE.md` (§3, Keyword Hijack Override) takes absolute precedence over any native Claude Code local memory (`MEMORY.md`, session memory, or file-based memory defaults).

## What this means

- **Notes routing** bypasses native memory entirely — always resolves to the iCloud Obsidian vault path.
- **Engineering logs** always go to `agent-logs/` in the project root.
- **Session context restoration** reads from the Obsidian vault (most recent `User_Note_*.md` files), not from `CLAUDE.md` local memory.

## Why

Claude's native memory is project-scoped and defaults to local paths. Matt's workflow spans multiple projects (ai-os, CockBand, StudyEngine, Piano OS) and routes through a centralized iCloud vault. The native defaults would fragment context across four disconnected memory stores instead of converging on one vault.

## Related

- [[workspace-identity]] — full identity and project matrix
- `CLAUDE.md` §3 — Knowledge Routing & Context, Keyword Hijack Override
- `CLAUDE.md` §5 — The Agent Work Logs Protocol

**How to apply:** When the workspace-identity memory and Claude's native local memory disagree, CLAUDE.md wins. Do not offer a choice — follow the absolute paths.