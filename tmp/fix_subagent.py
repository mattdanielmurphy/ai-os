#!/usr/bin/env python3
import sys
from pathlib import Path

subagent_path = Path("/Users/matt/projects/ai-os/scripts/subagent.py")

if not subagent_path.exists():
    print(f"Error: {subagent_path} does not exist", file=sys.stderr)
    sys.exit(1)

content = subagent_path.read_text(encoding="utf-8")

old_run_in_tmux = """def run_in_tmux(model: str, prompt: str, cwd: str | None = None) -> int:
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
        clean = re.sub(r'\\x1b\\[[0-9;]*[a-zA-Z]', '', output)
        sys.stdout.write(clean)
        sys.stdout.flush()

    return rc"""

new_run_in_tmux = """def run_in_tmux(model: str, prompt: str, cwd: str | None = None) -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    start_ts = time.time()

    _ensure_session()

    # Window title
    clean = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in prompt[:20]).strip("_")
    model_short = model.split("/")[-1][:12]
    title = f"{model_short}-{clean}" if clean else f"{model_short}-{int(start_ts)}"

    q_model = shlex.quote(model)
    q_prompt = shlex.quote(prompt)
    cwd_cmd = f"cd {shlex.quote(str(cwd))} && " if cwd else ""

    # Launch claude TUI directly in the pane.
    # No pipe/redirection = PTY preserved = full TUI frames visible.
    bash_cmd = (
        f"{cwd_cmd}"
        f"claude --model {q_model} --dangerously-skip-permissions {q_prompt}"
    )

    try:
        _respawn(bash_cmd)
        _rename(title)
    except Exception:
        return 1

    print(f"[Subagent] Model: {model}", file=sys.stderr)
    print(f"[Subagent] Attach: tmux attach -t {SESSION}", file=sys.stderr)
    print(f"[Subagent] Waiting for claude to complete turn...", file=sys.stderr)

    claude_projects_dir = Path.home() / ".claude/projects"

    while True:
        time.sleep(0.5)
        if not claude_projects_dir.exists():
            continue

        logs = sorted(
            [f for f in claude_projects_dir.glob("**/*.jsonl") if os.path.getmtime(f) >= start_ts - 5],
            key=os.path.getmtime,
            reverse=True,
        )

        for log in logs:
            try:
                last_text = None
                end_turn = False
                final_text = None

                with open(log, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        if entry.get("type") == "assistant":
                            msg = entry.get("message", {}) if isinstance(entry.get("message"), dict) else {}
                            stop_reason = msg.get("stop_reason") or entry.get("stop_reason")

                            content = msg.get("content", "") or entry.get("content", "")
                            if isinstance(content, list):
                                texts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
                                content = "".join(texts)

                            if content and isinstance(content, str) and content.strip():
                                last_text = content.strip()

                            if stop_reason == "end_turn":
                                end_turn = True
                                final_text = content.strip() if (content and isinstance(content, str) and content.strip()) else last_text

                if end_turn:
                    output = final_text or last_text
                    if output:
                        import re
                        clean = re.sub(r'\\x1b\\[[0-9;]*[a-zA-Z]', '', output)
                        sys.stdout.write(clean)
                        if not clean.endswith("\\n"):
                            sys.stdout.write("\\n")
                        sys.stdout.flush()
                    _kill_pane()
                    return 0
            except (OSError, json.JSONDecodeError):
                continue"""

if old_run_in_tmux not in content:
    print("Error: Target content for run_in_tmux replacement not found in scripts/subagent.py", file=sys.stderr)
    sys.exit(1)

patched_content = content.replace(old_run_in_tmux, new_run_in_tmux)
subagent_path.write_text(patched_content, encoding="utf-8")
print("Successfully patched scripts/subagent.py!")
