
# No Command May Hang a Thread (Matt, 2026-10-23)
- Two threads froze 20+ min on a render/test command. Foreground Bash must always end fast.
- Renders, encodes, playback, dev servers, watchers and anything over ~1 min run detached: `run_in_background`, or `nohup <cmd> > tmp/<name>.log 2>&1 &`, then poll the log in later calls. Never a bare `&` (it holds the tool's pipe open) and never `sleep` 60s+ in the foreground.
- Short probes of possibly-hanging things get a hard cap: `perl -e 'alarm 60; exec @ARGV' -- <cmd>` (macOS has no `timeout`).
- Enforced by `scripts/hooks/bash_timeout_guard.py` (PreToolUse; denies the above, `# long-ok` in the command overrides). `scripts/tool_watchdog.py` (launchd, every minute) toasts Matt when a Claude shell command runs 8+ min, with the kill command. It never kills anything itself.
