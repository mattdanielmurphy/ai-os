# Hang protection (2026-10-23)

## 22:20 Global guard so no agent command hangs forever
- Asked by coordinator: two threads froze 20+ min on a render/test command.
- Built: PreToolUse hook `scripts/hooks/bash_timeout_guard.py` (in ~/.claude/settings.json). Denies foreground renders/encodes/playback/servers/watchers, `sleep` 60s+, timeout over 5 min, bare trailing `&`. Escape: `# long-ok`. Tested with 8 sample commands.
- Built: `scripts/tool_watchdog.py` + launchd `com.matt.agent.tool-watchdog` (every 60s). Toasts via claude-notify when a Claude-spawned shell command runs 8+ min, with a kill command. Detection verified; real toast not triggered.
- Rule added to `.rules/claude_only.md`, compiled with build_rules.py.
- Rejected: auto-kill (background servers look identical to stuck commands); wrapping every command in a timeout (breaks cd persistence; macOS has no `timeout`); updatedInput timeout injection (Bash default is already 120s, the freeze was likely a pipe held open or an oversized timeout).
- Unknown: the exact cause of tonight's freeze. Not reproduced.
- Undo: remove the hook line from ~/.claude/settings.json; `launchctl bootout gui/$(id -u)/com.matt.agent.tool-watchdog`.
