# Agent Work Log: Fix Claude Rules Enforcement & Tmux Subagent Simplicity

## Goal
Fix two issues:
1. Claude ignored the preflight/housekeeping rules — needed explicit "MUST" enforcement in `claude_only.md`
2. Tmux subagent monitoring was broken: `new-window` created separate windows that appeared dead/empty when user attached. The user saw nothing.

## User Feedback & Decisions
- Confirmed: no fancy split panes, no multiple sessions — one subagent at a time, simple and reliable.
- Explicitly want preflight + auto-commit enforced as mandatory steps for Claude sessions.

## Changes Made
- **`.rules/claude_only.md`**: Added "Mandatory Preflight (Always)" and "Mandatory Auto-Commit (Always)" as the first two rules for Claude — explicit language, no ambiguity.
- **`.rules/common.md`**: No changes (preflight rule already existed but was buried).
- **`scripts/subagent.py`**: Replaced `new-window` approach with `respawn-pane -k -t session:0.0` — always reuses the same single pane. Removed `cleanup_stale_tmux_windows()` (no longer needed). Simplified to one window, one pane, always visible when user attaches with `tmux attach -t subagents`.
- **`scripts/build_rules.py`**: Re-ran after rule edit.

## What Worked
- Single-pane `respawn-pane` approach: subagent output appears in the only pane and remains visible via `remain-on-exit`.
- User attaches with `tmux attach -t subagents` and sees the subagent output directly.
- Verified: pane content is preserved after command completes ("Pane is dead" but scrollback buffer retains output).

## What Didn't Work / Known Issues
- `tmux capture-pane` on a dead pane prints "Pane is dead" before scrollback content — but attaching interactively shows the output fine since `remain-on-exit` is `on`.
- Logs still written to `tmp/subagent_logs/` for file-based streaming.

## Architecture Notes
- `respawn-pane -k` kills the current process in the pane and starts a new one — so it handles both the first spawn (when pane is alive in bash) and respawns (when pane is dead from a previous subagent).
- Important: need to set `remain-on-exit on` after respawn because fresh panes reset this option.