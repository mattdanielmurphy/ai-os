# Agent Quirks and Workarounds

This file tracks ongoing behavioral issues, quirks, and anti-patterns exhibited by agents, along with the strategies and workarounds used to mitigate them.

## Issue 1: Ignoring Native Tools in Favor of Bash
- **Problem**: Agents often default to using raw bash commands (e.g., `ls -la | grep`, `cat`, `sed`) via `run_command` instead of prioritizing native, purpose-built tools like `list_dir`, `view_file`, or `grep_search`. This leads to brittle operations (like missing untracked symlinks or hitting bash escaping issues).
- **Current Mitigation**: Command interceptions (e.g., overriding shell commands or wrapping them in scripts) have been set up to block or redirect some of these behaviors. However, intercepting complex piped sequences (like `ls -la | grep ...`) remains difficult.
- **Future Work**: We need a systemic way to enforce native tool usage rules or expand command interceptions to handle pipes and complex shell strings safely.

## Issue 2: output.md Not Opening in Preview Pane
- **Problem**: The output markdown preview pane sometimes fails to load or open `.ai-os/output.md` automatically, despite the file being written by the agent. This may be caused by Tauri filesystem scope/permission restrictions or path resolution mismatches.
- **Current Mitigation**: Added console error logging in the frontend polling loop (`src/main.ts`) to capture file read/existence errors. This allows checking the web inspector for details (e.g., security/scope exceptions).
- **Future Work**: Investigate if Tauri scope configurations (`tauri.conf.json`) need wildcard or project-directory-specific scopes, or if the path needs to be canonicalized.

