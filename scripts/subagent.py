#!/usr/bin/env python3
import json
import os
import sys
import time
import subprocess
import argparse
import shlex
import tempfile
from pathlib import Path
from parse_litellm_models import validate_model, get_available_models, DEFAULT_CONFIG_PATH

LITELLM_URL = "http://localhost:8082/v1/messages"

def run_in_tmux(model, prompt="", session_name="subagents"):
    cwd_tmp = Path.cwd() / "tmp" / "subagent_logs"
    if not cwd_tmp.parent.exists():
        cwd_tmp = Path("/Users/matt/projects/ai-os/tmp/subagent_logs")
    cwd_tmp.mkdir(parents=True, exist_ok=True)

    timestamp = int(time.time())
    run_id = f"{model.replace('/', '_')}_{timestamp}_{os.getpid()}"
    log_file = cwd_tmp / f"{run_id}.log"
    exit_file = cwd_tmp / f"{run_id}.exit"

    # Ensure the subagents session exists with one window, one pane
    res = subprocess.run(["tmux", "has-session", "-t", session_name], capture_output=True)
    if res.returncode != 0:
        subprocess.run(["tmux", "new-session", "-d", "-s", session_name, "-n", "sub", "bash"], check=True)
    else:
        subprocess.run(["tmux", "respawn-pane", "-k", "-t", f"{session_name}:0.0", "bash"],
                       stderr=subprocess.DEVNULL)

    clean_prompt = "".join(c if (c.isalnum() or c in ("-", "_")) else "_" for c in prompt[:15]).strip("_")
    model_short = model.split("/")[-1][:10]
    title = f"{model_short}-{clean_prompt}" if clean_prompt else f"{model_short}-{timestamp}"

    # Write payload to a temp file to avoid shell/json escaping issues
    payload = json.dumps({
        "model": model,
        "max_tokens": 8192,
        "messages": [{"role": "user", "content": prompt}]
    })
    payload_file = cwd_tmp / f"{run_id}.payload.json"
    payload_file.write_text(payload)

    quoted_log = shlex.quote(str(log_file))
    quoted_exit = shlex.quote(str(exit_file))
    quoted_payload = shlex.quote(str(payload_file))

    bash_cmd = (
        f"curl -s -w '\\n%{{http_code}}' -X POST {LITELLM_URL} "
        f"-H 'Content-Type: application/json' "
        f"-H 'x-api-key: dummy' "
        f"-H 'anthropic-version: 2023-06-01' "
        f"-d @{quoted_payload} "
        f"2>&1 | tee {quoted_log}; echo ${{PIPESTATUS[0]}} > {quoted_exit}; "
        f"rm -f {quoted_payload}"
    )

    try:
        subprocess.run(["tmux", "respawn-pane", "-k",
                        "-t", f"{session_name}:0.0",
                        "bash", "-c", bash_cmd],
                       check=True, capture_output=True)
        subprocess.run(["tmux", "set-window-option", "-t", f"{session_name}:0",
                        "remain-on-exit", "on"],
                       stderr=subprocess.DEVNULL)
        subprocess.run(["tmux", "rename-window", "-t", f"{session_name}:0", title],
                       stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[Subagent Tmux Error] Could not respawn tmux pane: {e}. Falling back to direct execution.", file=sys.stderr)
        return None

    print(f"[Subagent Invoker] Model: {model} | Prompt length: {len(prompt)} chars", file=sys.stderr)
    print(f"[Subagent Tmux] Session: '{session_name}' (window 0 — attach with: tmux attach -t {session_name})", file=sys.stderr)

    # Stream output as it arrives
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

    # Drain remaining output
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


def call_litellm_direct(model, prompt):
    """Call LiteLLM API directly (used for --no-tmux mode)."""
    payload = json.dumps({
        "model": model,
        "max_tokens": 8192,
        "messages": [{"role": "user", "content": prompt}]
    })
    proc = subprocess.run(
        ["curl", "-s", "-w", "\n%{http_code}",
         "-X", "POST", LITELLM_URL,
         "-H", "Content-Type: application/json",
         "-H", "x-api-key: dummy",
         "-H", "anthropic-version: 2023-06-01",
         "-d", payload],
        capture_output=True, text=True
    )
    # Parse response
    lines = proc.stdout.strip().split("\n")
    http_code = lines[-1].strip() if lines else "000"
    body = "\n".join(lines[:-1])

    if http_code.startswith("2"):
        print(body)
        return 0
    else:
        print(f"API Error ({http_code}): {body}", file=sys.stderr)
        return 1


def main():
    models_str = ", ".join(get_available_models(DEFAULT_CONFIG_PATH))
    epilog_str = f"Available Models (excluding fallbacks):\n  {models_str}"

    parser = argparse.ArgumentParser(
        description="Invoke subagents via LiteLLM proxy. Uses curl directly (not claude CLI) to support any LiteLLM model.",
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

    if not args.no_tmux:
        exit_code = run_in_tmux(model=args.model, prompt=args.prompt)
        if exit_code is not None:
            sys.exit(exit_code)

    # Direct (non-tmux) execution
    exit_code = call_litellm_direct(args.model, args.prompt)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()