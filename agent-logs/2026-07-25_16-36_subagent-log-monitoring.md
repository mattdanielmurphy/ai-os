# Subagent Log Monitoring for End Turn

## Goal
Update `scripts/subagent.py` to monitor Claude Code's project JSONL logs (`~/.claude/projects/**/*.jsonl`) for `stop_reason == 'end_turn'`, automatically returning the response output and closing the tmux subagent pane without requiring user manual `/exit` intervention.

## User Feedback & Decisions
- Eliminate manual exit requirement when invoking `claude` subagents via `subagent.py`.
- Continuously poll JSONL session logs for completion events rather than waiting for process exit signals.

## Changes Made
- Modified `scripts/subagent.py`:
  - Removed execution exit file requirement (`run_id.exit`) and bash wrapper `; echo $? > exit_file`.
  - Added continuous scanning of `~/.claude/projects/**/*.jsonl` modified within 5s of execution start.
  - Implemented JSON entry parsing to check for `type == "assistant"` and `stop_reason == "end_turn"`.
  - Extracted completed content text, sanitized ANSI escape sequences, printed clean output to stdout.
  - Automatically terminated the dedicated subagent tmux pane via `_kill_pane()` upon turn completion.

## What Worked
- `subagent.py` detects turn completion dynamically in real-time as Claude finishes generating output.
- Output text is extracted cleanly from JSON logs and flushed to stdout.
- Subagent tmux pane terminates cleanly on `end_turn`.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Claude Code streams session history to JSONL files in `~/.claude/projects/<project-hash>/<session-id>.jsonl`.
- Inspecting `stop_reason == "end_turn"` in real-time allows subagent scripts to act synchronously without losing interactive PTY rendering capability during generation.
