#!/usr/bin/env python3
"""PreToolUse guard: no Bash call may hang a thread.

Denies, with a fix-it message, foreground commands that are known to run long or
forever, or that can hold the tool's output pipe open after the command "ends":
  - timeout above 5 min without run_in_background
  - renders / encodes / playback / servers / watchers / `sleep` >= 60s in the foreground
  - a bare trailing `&` (child keeps the pipe open, the tool waits for EOF)
Escape hatch for a deliberate long foreground command: put `# long-ok` in it.
Fails open on any parse problem.
"""
import json
import re
import sys

MAX_FG_MS = 300_000
START = r"(?:^|[;&|(`]|\$\()\s*(?:\w+=\S+\s+)*(?:sudo\s+)?"
LONG = [
    (r"(ffmpeg|ffplay|afplay|mpv)\b", "encode/playback"),
    (r"\b(hyperframes|manim|remotion)\b[^\n]*\b(render|preview)\b", "video render"),
    (r"\b(bun|npm|npx|pnpm|yarn)\s+(run\s+)?(dev|start|serve|watch|render|preview)\b", "dev server / render"),
    (r"\b(next|vite|astro)\s+(dev|start|preview)\b", "dev server"),
    (r"\b(playwright|puppeteer)\b[^\n]*\b(test|codegen|show-report)\b", "browser run"),
    (r"\btail\s+(-\S*f|--follow)", "tail -f"),
    (r"(^|[;&|]\s*)watch\s", "watch"),
    (r"\bpython3?\s+-m\s+http\.server\b|\bphp\s+-S\b|\buvicorn\b|\bflask\s+run\b", "server"),
    (r"\bclaude-control\s+ask\b[^\n]*\b(wait|--urgent)\b", ""),  # placeholder, never matches meaning
]
SLEEP = re.compile(r"\bsleep\s+(\d+(?:\.\d+)?)([smhd]?)")


def long_sleep(cmd):
    for n, u in SLEEP.findall(cmd):
        if float(n) * {"": 1, "s": 1, "m": 60, "h": 3600, "d": 86400}[u] >= 60:
            return True
    return False


def bare_amp(cmd):
    for line in cmd.splitlines():
        s = line.strip()
        if s.endswith("&") and not s.endswith("&&") and not re.search(r"[0-9]?>\s*\S|&>|\|", s):
            return True
    return False


def deny(why):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
          "permissionDecision": "deny", "permissionDecisionReason": why}}))


def main():
    try:
        data = json.load(sys.stdin)
        if data.get("tool_name") != "Bash":
            return 0
        ti = data.get("tool_input") or {}
        cmd = ti.get("command", "")
    except Exception:
        return 0
    if ti.get("run_in_background") or "# long-ok" in cmd:
        return 0
    fix = ("Blocked by the hang guard (a stuck command froze two threads for 20+ min). "
           "Run it detached and poll: set run_in_background=true, or `mkdir -p tmp; nohup <cmd> > tmp/<name>.log 2>&1 &`, "
           "then check `tail tmp/<name>.log` in a later call. Short probes: wrap in `perl -e 'alarm 60; exec @ARGV' -- <cmd>`. "
           "Truly intended foreground? add `# long-ok` to the command.")
    t = ti.get("timeout")
    if isinstance(t, (int, float)) and t > MAX_FG_MS:
        deny(f"timeout {int(t)}ms is over the 5-min foreground cap. " + fix)
        return 0
    if long_sleep(cmd):
        deny("`sleep` of 60s+ in the foreground. Use Monitor/ScheduleWakeup or run_in_background. " + fix)
        return 0
    for pat, label in LONG:
        if label and re.search(START + "(?:" + pat + ")", cmd, re.I | re.M):
            deny(f"Foreground {label} command. " + fix)
            return 0
    if bare_amp(cmd):
        deny("Trailing `&` without redirecting output keeps the tool's pipe open and hangs it. "
             "Use `> tmp/x.log 2>&1 &` or run_in_background. " + fix)
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
