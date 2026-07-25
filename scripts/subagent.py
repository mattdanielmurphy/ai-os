#!/usr/bin/env python3
"""subagent.py — spawn claude Code TUI in a tmux pane for live monitoring.

Architecture:
- One tmux session ("subagents"), one window, one pane.
- Launches claude TUI directly (no pipe, preserves TTY for TUI frames).
- User watches and interacts in tmux; manually exits with `/exit`.
- After exit, captures claude's final response from session JSONL logs.

Usage:
  tmux attach -t subagents                    # watch TUI in real-time
  python3 subagent.py -p "..."               # spawn (blocking, returns output)
  python3 subagent.py -p "..." --no-tmux      # skip tmux, use -p mode
"""

import json
import os
import subprocess
import argparse
import shlex
import sys
import time
from pathlib import Path
from parse_litellm_models import validate_model, get_available_models, DEFAULT_CONFIG_PATH

SESSION = "subagents"
LOG_DIR = Path("/Users/matt/projects/ai-os/tmp/subagent_logs")
CLAUDE_SESSION_DIR = Path.home() / ".claude/projects/-Users-matt-projects-ai-os"


def _ensure_session():
    r = subprocess.run(["tmux", "has-session", "-t", SESSION], capture_output=True)
    if r.returncode != 0:
        subprocess.run(["tmux", "new-session", "-d", "-s", SESSION, "-n", "sub", "bash"], check=True)
        subprocess.run(["tmux", "set-window-option", "-t", f"{SESSION}:0", "remain-on-exit", "on"],
                       stderr=subprocess.DEVNULL)


def _kill_pane():
    subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0.0", "C-c"], stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    subprocess.run(["tmux", "send-keys", "-t", f"{SESSION}:0.0", "Enter"], stderr=subprocess.DEVNULL)
    time.sleep(0.3)


def _respawn(cmd: str):
    _kill_pane()
    subprocess.run(["tmux", "respawn-pane", "-k", "-t", f"{SESSION}:0.0", "bash", "-c", cmd],
                   check=True, capture_output=True, timeout=5)


def _rename(title: str):
    subprocess.run(["tmux", "rename-window", "-t", f"{SESSION}:0", title[:30]],
                   stderr=subprocess.DEVNULL)


def _get_last_assistant(created_after: float) -> str | None:
    """Read the most recent claude session log created after `created_after`.
    Returns the last assistant message text, stripped of markdown.
    """
    if not CLAUDE_SESSION_DIR.exists():
        return None

    logs = sorted(CLAUDE_SESSION_DIR.glob("*.jsonl"), key=os.path.getmtime, reverse=True)
    for log in logs:
        if os.path.getmtime(log) < created_after:
            continue
        try:
            last_text = None
            for line in open(log, "r", encoding="utf-8", errors="replace"):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if entry.get("type") == "assistant":
                    # Different formats for content
                    content = entry.get("message", {}).get("content", "") or entry.get("content", "")
                    if isinstance(content, list):
                        texts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
                        content = "".join(texts)
                    if content and isinstance(content, str) and content.strip():
                        last_text = content.strip()
            if last_text:
                return last_text
        except (OSError, json.JSONDecodeError):
            continue
    return None


def run_in_tmux(model: str, prompt: str, cwd: str | None = None) -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    start_ts = time.time()
    run_id = f"{model.replace('/', '_')}_{int(start_ts)}_{os.getpid()}"
    exit_file = LOG_DIR / f"{run_id}.exit"

    _ensure_session()

    # Window title
    clean = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in prompt[:20]).strip("_")
    model_short = model.split("/")[-1][:12]
    title = f"{model_short}-{clean}" if clean else f"{model_short}-{int(start_ts)}"

    q_model = shlex.quote(model)
    q_prompt = shlex.quote(prompt)
    q_exit = shlex.quote(str(exit_file))
    cwd_cmd = f"cd {shlex.quote(str(cwd))} && " if cwd else ""

    # Launch claude TUI directly in the pane.
    # No pipe/redirection = PTY preserved = full TUI frames visible.
    # The ; echo runs after claude exits (user types /exit).
    bash_cmd = (
        f"{cwd_cmd}"
        f"claude --model {q_model} --dangerously-skip-permissions {q_prompt}; "
        f"echo $? > {q_exit}"
    )

    try:
        _respawn(bash_cmd)
        _rename(title)
    except Exception:
        return 1

    print(f"[Subagent] Model: {model}", file=sys.stderr)
    print(f"[Subagent] Attach: tmux attach -t {SESSION}", file=sys.stderr)
    print(f"[Subagent] Waiting for claude to exit...", file=sys.stderr)

    # Wait for exit file (written when claude exits)
    while not exit_file.exists():
        time.sleep(0.5)

    try:
        rc = int(Path(exit_file).read_text().strip())
    except (ValueError, OSError):
        rc = 1

    # Capture final response from claude's session logs
    output = _get_last_assistant(start_ts)
    if output:
        # Strip ANSI escape codes
        import re
        clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', output)
        sys.stdout.write(clean)
        sys.stdout.flush()

    return rc


def main():
    models = ", ".join(get_available_models(DEFAULT_CONFIG_PATH))

    parser = argparse.ArgumentParser(
        description="Spawn claude Code TUI in tmux pane. Captures response from claude session logs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Available Models:\n  {models}")

    parser.add_argument("-p", "--prompt", required=True, help="Task for the subagent.")
    parser.add_argument("-m", "--model", default="deepseek-v4-flash", help="Model name from litellm config.yaml")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to litellm config.yaml")
    parser.add_argument("--cwd", help="Working directory (default: current)")
    parser.add_argument("--no-tmux", action="store_true", help="Skip tmux, use -p mode")

    args = parser.parse_args()

    valid, msg, _ = validate_model(args.model, config_path=args.config)
    if not valid:
        print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    if args.no_tmux:
        print(f"[Direct] Model: {args.model}", file=sys.stderr)
        sys.exit(subprocess.run(["claude", "--model", args.model,
                                 "--dangerously-skip-permissions", "-p", args.prompt]).returncode)

    sys.exit(run_in_tmux(model=args.model, prompt=args.prompt, cwd=args.cwd))


if __name__ == "__main__":
    main()