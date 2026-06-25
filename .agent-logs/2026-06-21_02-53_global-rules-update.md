## Goal
Address two major user complaints regarding agent behavior:
1. Littering files in generic parent folders (specifically ~/projects) when creating new projects/utilities without creating a dedicated subdirectory.
2. Inadequate/missing context documentation between threads, making fresh threads feel disconnected instead of behaving continuously using past logs, user decisions, and context.

## User Feedback & Decisions
- The user requested adding a rule/step where the agent must inspect its current directory, and if it's a generic parent folder, create a dedicated sub-directory before making files inside.
- The user requested detailed context documentation (logs, context files, user messages, decisions, project goals) so that any fresh thread can resume work seamlessly by reading past work logs.

## Changes Made
- **Modified [/Users/matthewmurphy/.gemini/GEMINI.md](file:///Users/matthewmurphy/.gemini/GEMINI.md)**:
  - Added Rule 9 under `<CORE_RULES>` for Directory Consideration & Nesting.
  - Enhanced Rule 0 under `<AGENT_WORK_LOGS>` (Fresh Thread Context) to require reading `AG_CONTEXT.md`, `FEATURES.md`, and the most recent 2-3 logs from `.agent-logs/` at startup to reconstruct continuous thread context.
  - Updated Rule 3 under `<AGENT_WORK_LOGS>` (Writing Logs) to require documenting a `## User Feedback & Decisions` section containing user feedback and choices made.
- **Modified [/Users/matthewmurphy/projects/ai-os/rulebook.md](file:///Users/matthewmurphy/projects/ai-os/rulebook.md)**:
  - Added a new constraint under "Development Constraints" for Directory Consideration & Nesting, matching the global rule.
- **Modified [/Users/matthewmurphy/projects/ai-os/FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md)**:
  - Added "Directory Consideration & Nesting Rule" and "Context Documentation and Thread Continuity" to the feature list.

## What Worked
- Updated the global user instructions template (`GEMINI.md`), ensuring that any future session initialized for this workspace (or others) inherits these corrected rules.
- Updated the local gateway rulebook and feature list to keep local executions in alignment.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The gateway's rules are governed both globally (by `GEMINI.md`) and locally (by `rulebook.md` and `AG_CONTEXT.md`). Aligning both ensures consistent enforcement across both individual agent runs and gateway proxy execution runs.
