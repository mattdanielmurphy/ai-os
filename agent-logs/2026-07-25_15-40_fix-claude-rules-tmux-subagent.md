# Agent Work Log: Fix Subagent Tmux Integration — Simplify + TUI Mode

## Goal
Fix two issues:
1. Claude ignored preflight/housekeeping rules in `claude_only.md`
2. Tmux subagent showed nothing when user attached — `new-window` created hidden windows; output was lost

## User Feedback & Decisions
- Explicitly want `/subagents` tmux session to show Claude Code **TUI mode** (full interactive interface with frames, thinking, tool calls)
- One pane, one window, no split panes or multiple sessions
- When subagent finishes, the calling agent needs to see Claude's response (capture from session logs)
- User exits claude manually with `/exit` after reviewing TUI output

## Changes Made
- **`.rules/claude_only.md`**: Added "Mandatory Preflight (Always)" and "Mandatory Auto-Commit (Always)" as first two rules — explicit "MUST" language, no ambiguity. Rebuilt into `CLAUDE.md`.
- **`scripts/subagent.py`**: Complete rewrite:
  - **Mode 1: TUI (default)**: Launches `claude TUI 'prompt'` directly in the pane. No pipe, no redirection — preserves PTY for full TUI frames. User watches/interacts in tmux, exits with `/exit`. After exit, captures Claude's final response from `~/.claude/projects/...` session JSONL logs (last assistant message).
  - **Mode 2: Direct (`--no-tmux`)**: Uses `claude -p` mode, skipping tmux entirely.
  - **One session, one pane**: `tmux attach -t subagents` shows Claude working in real-time.
  - Reliable exit detection via sentinel file (written after claude exits).
- **Removed `tmp/subagent_runner.sh`** (temp artifact from failed `script -c` approach).

## What Worked
- TUI mode with capture from claude session logs works end-to-end:
  ```
  tmux attach -t subagents  # see claude TUI live
  python3 subagent.py -p "..."  # spawn, blocks until exit, prints output
  ```
- `deepseek-v4-flash` works fully. `gemini-3.1-pro` rejected by claude CLI's hardcoded model validation (separate issue).
- Direct mode (`--no-tmux`) works for non-interactive use.

## What Didn't Work / Known Issues
- `script -c` approach: broke on quoting through `tmux send-keys` + `bash -c` + `script -c` nesting. Raw TUI mode avoids this entirely.
- `gemini-3.1-pro` rejected by claude CLI v2.1.212 — the CLI has a hardcoded model allowlist and rejects non-Anthropic models like `gemini-3.1-pro`. But `gemini-3.1-pro-preview` works. This is a LiteLLM config.yaml mapping issue (the actual Google model ID is `gemini-3.1-pro-preview`).
- `/exit` detection via `❯` prompt is unreliable due to stale pane content. Using sentinel file + session log capture instead.

## Architecture Notes
- Using `tmux respawn-pane -k` to reuse the same pane — kills whatever's running, starts new command
- `remain-on-exit on` preserves output after command exits so user can review
- Claude session logs in `~/.claude/projects/` contain full assistant responses — good single source for capture
- `claude --dangerously-skip-permissions -p` is not the same as `claude --dangerously-skip-permissions 'prompt'` (TUI). The former exits immediately after printing; the latter stays open at `❯` for interaction.