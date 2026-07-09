## Goal
Fix context architecture routing, clean up redundant/confused rules files, and isolate agent rules.

## Changes Made
- Updated [append_system_rule.py](file:///Users/matthewmurphy/projects/ai-os/scripts/append_system_rule.py) to route rule appending based on target agent:
  - `--agent global` writes to both `~/.gemini/GEMINI.md` (under `### GLOBAL RULES`) and `CLAUDE.md` (under `## GLOBAL RULES`).
  - `--agent agy` writes only to `~/.gemini/GEMINI.md` (under `### ANTIGRAVITY (PREMIUM) RULES`).
  - `--agent claude` writes only to `CLAUDE.md` (under `## CLAUDE-SPECIFIC RULES`).
- Cleaned up [GEMINI.md](file:///Users/matthewmurphy/.gemini/GEMINI.md) by removing Claude-specific rules and telemetry constraints.
- Initialized a standalone [CLAUDE.md](file:///Users/matthewmurphy/projects/ai-os/CLAUDE.md) containing the deletion ban, memory constraint, and Claude-specific cost telemetry rule.
- Documented these changes in [FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md).

## What Worked
- Programmatic routing updates to `append_system_rule.py` via LiteLLM/mechanical-editor fallback.
- Context cleanups for both `GEMINI.md` and `CLAUDE.md` successfully validated via tests and reset to baseline.

## What Didn't Work / Known Issues
- LiteLLM was initially not running, causing direct unified patch application in the mechanical editor to fail. Resolved by launching the local `litellm` process on port `4000` mapped to `openrouter/deepseek/deepseek-chat` in the background.

## Architecture Notes
- Splitting the instructions guarantees that the Antigravity TUI isn't confused by Claude-specific rules and Claude Code reads from `CLAUDE.md` without missing the core system rules.
