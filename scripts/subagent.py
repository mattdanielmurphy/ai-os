#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import argparse
import shlex
from pathlib import Path
from parse_litellm_models import validate_model, get_available_models, DEFAULT_CONFIG_PATH

def cleanup_stale_tmux_windows(session_name="subagents", max_dead=20):
    """
    Cleans up oldest dead panes/windows in the tmux session if count exceeds max_dead.
    """
    try:
        out = subprocess.check_output(
            ["tmux", "list-panes", "-a", "-F", "#{window_id} #{pane_dead}", "-t", session_name],
            text=True,
            stderr=subprocess.DEVNULL
        )
        dead_windows = []
        for line in out.strip().splitlines():
            parts = line.strip().split()
            if len(parts) == 2 and parts[1] == "1":
                dead_windows.append(parts[0])

        if len(dead_windows) > max_dead:
            to_remove = dead_windows[:-max_dead]
            for win_id in to_remove:
                subprocess.run(["tmux", "kill-window", "-t", win_id], stderr=subprocess.DEVNULL)
    except Exception:
        pass

def run_in_tmux(cmd_args, model="claude", prompt="", session_name="subagents"):
    cwd_tmp = Path.cwd() / "tmp" / "subagent_logs"
    if not cwd_tmp.parent.exists():
        cwd_tmp = Path("/Users/matt/projects/ai-os/tmp/subagent_logs")
    cwd_tmp.mkdir(parents=True, exist_ok=True)

    timestamp = int(time.time())
    run_id = f"{model.replace('/', '_')}_{timestamp}_{os.getpid()}"
    log_file = cwd_tmp / f"{run_id}.log"
    exit_file = cwd_tmp / f"{run_id}.exit"

    res = subprocess.run(["tmux", "has-session", "-t", session_name], capture_output=True)
    if res.returncode != 0:
        subprocess.run(["tmux", "new-session", "-d", "-s", session_name, "-n", "overview", "bash"], check=True)

    cleanup_stale_tmux_windows(session_name)

    clean_prompt = "".join(c if (c.isalnum() or c in ("-", "_")) else "_" for c in prompt[:15]).strip("_")
    model_short = model.split("/")[-1][:10]
    window_name = f"{model_short}-{clean_prompt}" if clean_prompt else f"{model_short}-{timestamp}"

    inner_cmd = " ".join(shlex.quote(arg) for arg in cmd_args)
    bash_cmd = f"{inner_cmd} 2>&1 | tee {shlex.quote(str(log_file))}; echo ${{PIPESTATUS[0]}} > {shlex.quote(str(exit_file))}"

    tmux_cmd = [
        "tmux", "new-window", "-P", "-F", "#{window_id}",
        "-t", session_name,
        "-n", window_name,
        f"bash -c {shlex.quote(bash_cmd)}"
    ]

    try:
        window_id = subprocess.check_output(tmux_cmd, text=True).strip()
        subprocess.run(["tmux", "set-window-option", "-t", window_id, "remain-on-exit", "on"], stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[Subagent Tmux Error] Could not spawn tmux window: {e}. Falling back to standard process.", file=sys.stderr)
        return None

    print(f"[Subagent Invoker] Model: {model} | Prompt length: {len(prompt)} chars", file=sys.stderr)
    print(f"[Subagent Tmux] Session: '{session_name}' | Window: '{window_name}' ({window_id})", file=sys.stderr)

    last_pos = 0
    while not exit_file.exists():
        time.sleep(0.2)
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                f.seek(last_pos)
                chunk = f.read()
                if chunk:
                    sys.stdout.write(chunk)
                    sys.stdout.flush()
                    last_pos = f.tell()

    if log_file.exists():
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            f.seek(last_pos)
            chunk = f.read()
            if chunk:
                sys.stdout.write(chunk)
                sys.stdout.flush()

    try:
        exit_code = int(exit_file.read_text().strip())
    except Exception:
        exit_code = 1

    return exit_code

def main():
    models_str = ", ".join(get_available_models(DEFAULT_CONFIG_PATH))
    epilog_str = f"Available Models (excluding fallbacks):\n  {models_str}"

    parser = argparse.ArgumentParser(
        description="Invoke subagents with strict model validation against LiteLLM config.yaml.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog_str
    )

    parser.add_argument("-p", "--prompt", type=str, required=True, help="Prompt / task description for the subagent.")
    parser.add_argument("-m", "--model", type=str, default="deepseek-v4-flash", help="Model name as defined in litellm config.yaml")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to litellm config.yaml")
    parser.add_argument("--no-tmux", action="store_true", help="Bypass tmux and run subagent directly in current process.")

    args = parser.parse_args()

    valid, msg, available = validate_model(args.model, config_path=args.config)
    if not valid:
        print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    cmd = ["claude", "--model", args.model, "-p", args.prompt]

    if not args.no_tmux:
        exit_code = run_in_tmux(cmd, model=args.model, prompt=args.prompt)
        if exit_code is not None:
            sys.exit(exit_code)

    print(f"[Subagent Invoker Direct] Model: {args.model} | Prompt length: {len(args.prompt)} chars", file=sys.stderr)
    try:
        res = subprocess.run(cmd)
        sys.exit(res.returncode)
    except Exception as e:
        print(f"Execution Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
