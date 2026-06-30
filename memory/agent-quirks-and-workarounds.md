# Agent Quirks and Workarounds

This file tracks ongoing behavioral issues, quirks, and anti-patterns exhibited by agents, along with the strategies and workarounds used to mitigate them.

## Issue 1: Ignoring Native Tools in Favor of Bash
- **Problem**: Agents often default to using raw bash commands (e.g., `ls -la | grep`, `cat`, `sed`) via `run_command` instead of prioritizing native, purpose-built tools like `list_dir`, `view_file`, or `grep_search`. This leads to brittle operations (like missing untracked symlinks or hitting bash escaping issues).
- **Current Mitigation**: Command interceptions (e.g., overriding shell commands or wrapping them in scripts) have been set up to block or redirect some of these behaviors. However, intercepting complex piped sequences (like `ls -la | grep ...`) remains difficult.
- **Future Work**: We need a systemic way to enforce native tool usage rules or expand command interceptions to handle pipes and complex shell strings safely.

## Issue 2: output.md Not Opening in Preview Pane
- **Problem**: The output markdown preview pane fails to load or open `.ai-os/output.md` automatically, throwing a Tauri error: `"path not allowed on the configured scope: .../.ai-os/output.md"`.
- **Root Cause**: Tauri's filesystem scope glob patterns (e.g. `$HOME/**`) do not match hidden files or directories starting with a dot (like `.ai-os/`) by default as a security measure.
- **Current Mitigation / Fix**: 
  1. Added console error logging in the frontend polling loop (`src/main.ts`) to make security/scope exceptions visible.
  2. Added explicit scopes (e.g. `$HOME/**/.ai-os/*` and `$HOME/**/.ai-os/**/*`) to the fs scope configuration in `src-tauri/tauri.conf.json`.
- **Note**: The user must restart the Tauri application/dev process for the `tauri.conf.json` scope changes to take effect.


