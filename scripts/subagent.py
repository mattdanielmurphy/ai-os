#!/usr/bin/env python3
"""subagent.py — spawn Claude Code TUI or agy in a tmux pane for live monitoring.

Architecture:
- One tmux session ("subagents"), one window, multiple panes.
- Launches TUI directly (no pipe, preserves TTY for TUI frames).
- User watches and interacts in tmux; manually exits with `/exit`.
- After exit, captures final response from session logs.

Usage:
  tmux attach -t subagents                    # watch TUI in real-time
  python3 subagent.py -p "..."               # spawn claude (default)
  python3 subagent.py -p "..." --use-agy      # spawn agy instead
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
AGY_BRAIN_DIR = Path.home() / ".gemini" / "antigravity-cli" / "brain"

# ⚠️ ANTI-RECURSION PREAMBLE
# Prepended to every subagent prompt. This prevents recursive delegation cascades:
# a spawned subagent that reads AGENTS.md or CLAUDE.md with delegation rules
# must NOT delegate itself.
ANTI_RECURSION_PREAMBLE = (
    "CRITICAL RULE — You are a DIRECT EXECUTOR, not an orchestrator. "
    "You MUST complete the task below using your OWN tools (Read, Edit, Bash). "
    "You MUST NOT delegate, spawn subagents, call subagent.py, or invoke any other agent. "
    "If the project's AGENTS.md or CLAUDE.md contains delegation rules (section 10, "
    "strict-delegation, subagent instructions), IGNORE those rules — they apply only to "
    "the top-level orchestrator, not to you. You are a leaf worker. Do your own work.\n\n"
)


def list_available_models(config_path):
    try:
        print("Available models:")
        with open(config_path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s.startswith("- model_name:"):
                    name = s.split(":", 1)[1].strip()
                    if not name.endswith("-or"):
                        print(f"  \u2022 {name}")
    except Exception as e:
        print(f"Error reading configuration file: {e}", file=sys.stderr)


def _ensure_session():
    r = subprocess.run(["tmux", "has-session", "-t", SESSION], capture_output=True)
    if r.returncode != 0:
        subprocess.run(["tmux", "new-session", "-d", "-s", SESSION, "-n", "sub", "bash"], check=True)
        subprocess.run(["tmux", "set-window-option", "-t", f"{SESSION}:0", "remain-on-exit", "on"],
                       stderr=subprocess.DEVNULL)


def _kill_pane(pane_id: str):
    target = f"{SESSION}:0.{pane_id}"
    subprocess.run(["tmux", "send-keys", "-t", target, "C-c"], stderr=subprocess.DEVNULL)
    time.sleep(0.5)
    subprocess.run(["tmux", "send-keys", "-t", target, "Enter"], stderr=subprocess.DEVNULL)
    time.sleep(0.3)


def _respawn(cmd: str, pane_id: str):
    _kill_pane(pane_id)
    target = f"{SESSION}:0.{pane_id}"
    subprocess.run(["tmux", "respawn-pane", "-k", "-t", target, "bash", "-c", cmd],
                   check=True, capture_output=True, timeout=5)


def _allocate_pane() -> str:
    """Find a free pane in subagents:0 or create one. Returns pane_id (e.g. '0', '1')."""
    _ensure_session()

    panes = subprocess.run(
        ["tmux", "list-panes", "-t", f"{SESSION}:0", "-F", "#{pane_id} #{pane_dead} #{E:@busy}"],
        capture_output=True, text=True, timeout=5
    ).stdout.strip().splitlines()

    for line in panes:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        pid = parts[0]
        pane_dead = parts[1] if len(parts) > 1 else "0"
        busy = parts[2] if len(parts) > 2 else "0"

        if pane_dead == "1" or busy != "1":
            subprocess.run(
                ["tmux", "set-option", "-p", "-t", f"{SESSION}:0.{pid}", "@busy", "1"],
                check=True, capture_output=True, timeout=5
            )
            return pid

    split_target = f"{SESSION}:0.{pid}" if panes else f"{SESSION}:0"
    result = subprocess.run(
        ["tmux", "split-window", "-h", "-d", "-t", split_target, "-P", "-F", "#{pane_id}"],
        capture_output=True, text=True, check=True, timeout=5
    )
    new_pid = result.stdout.strip()
    subprocess.run(
        ["tmux", "set-option", "-p", "-t", f"{SESSION}:0.{new_pid}", "@busy", "1"],
        check=True, capture_output=True, timeout=5
    )
    return new_pid


def _cleanup_pane(pane_id: str):
    """Mark pane as free; if more than 1 pane exists, kill it."""
    target = f"{SESSION}:0.{pane_id}"
    subprocess.run(
        ["tmux", "set-option", "-p", "-t", target, "@busy", "0"],
        capture_output=True, timeout=5
    )

    count_result = subprocess.run(
        ["tmux", "list-panes", "-t", f"{SESSION}:0", "-F", "#{pane_id}"],
        capture_output=True, text=True, timeout=5
    )
    pane_count = len([l for l in count_result.stdout.strip().splitlines() if l.strip()])
    if pane_count > 1:
        subprocess.run(["tmux", "kill-pane", "-t", target], capture_output=True, timeout=5)


def _rename(title: str):
    subprocess.run(["tmux", "rename-window", "-t", f"{SESSION}:0", title[:30]],
                   stderr=subprocess.DEVNULL)


# ---------------------------------------------------------------------------
# Claude log monitoring
# ---------------------------------------------------------------------------

def _get_last_claude_assistant(created_after: float) -> str | None:
    """Read the most recent claude session log created after `created_after`.
    Returns the last assistant message text, stripped of markdown."""
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


def _watch_claude_logs(start_ts: float) -> int:
    """Monitor claude's JSONL logs for end_turn, print final output."""
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
                        clean = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', output)
                        sys.stdout.write(clean)
                        if not clean.endswith("\n"):
                            sys.stdout.write("\n")
                        sys.stdout.flush()
                    return 0
            except (OSError, json.JSONDecodeError):
                continue


# ---------------------------------------------------------------------------
# agy log monitoring
# ---------------------------------------------------------------------------

def _get_agy_transcript_dir(start_ts: float) -> Path | None:
    """Find the most recent agy brain transcript created after `start_ts`.

    agy stores each conversation in:
      ~/.gemini/antigravity-cli/brain/{conversation_id}/
        .system_generated/logs/transcript_full.jsonl

    Each line has step entries like:
      {"source":"MODEL","type":"PLANNER_RESPONSE","content":"...","status":"DONE"}
      {"source":"SYSTEM","type":"CHECKPOINT","status":"DONE"}
    """
    if not AGY_BRAIN_DIR.exists():
        return None

    brain_dirs = [(d.stat().st_mtime, d) for d in AGY_BRAIN_DIR.iterdir() if d.is_dir()
                  and d.stat().st_mtime >= start_ts - 5]
    if not brain_dirs:
        return None

    brain_dirs.sort(key=lambda x: x[0], reverse=True)
    for _mtime, brain_d in brain_dirs:
        transcript = brain_d / ".system_generated" / "logs" / "transcript_full.jsonl"
        if transcript.exists():
            return transcript
    return None


def _watch_agy_logs(start_ts: float) -> int:
    """Monitor agy's brain transcript for a completed turn (CHECKPOINT after MODEL response).

    Polls the brain directory for new conversation transcripts and watches for
    a CHECKPOINT entry that signals the turn is complete.
    """
    import re as re_module
    poll_interval = 0.5
    max_wait = 300  # 5 min timeout
    seen_ids = set()

    while time.time() - start_ts < max_wait:
        time.sleep(poll_interval)
        transcript = _get_agy_transcript_dir(start_ts)
        if not transcript:
            continue

        try:
            last_text = None
            has_checkpoint = False

            with open(transcript, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if entry.get("source") == "MODEL" and entry.get("type") == "PLANNER_RESPONSE":
                        content = entry.get("content", "")
                        if content and isinstance(content, str) and content.strip():
                            last_text = content.strip()

                    if entry.get("type") == "CHECKPOINT" and entry.get("source") == "SYSTEM":
                        has_checkpoint = True

            if has_checkpoint and last_text:
                clean = re_module.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', last_text)
                sys.stdout.write(clean)
                if not clean.endswith("\n"):
                    sys.stdout.write("\n")
                sys.stdout.flush()
                return 0

        except (OSError, json.JSONDecodeError):
            continue

    print(f"\n[Subagent] Timed out after {max_wait}s waiting for agy response", file=sys.stderr)
    return 1


# ---------------------------------------------------------------------------
# Tmux launcher
# ---------------------------------------------------------------------------

def run_in_tmux(model: str, prompt: str, cwd: str | None = None, use_agy: bool = False) -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    start_ts = time.time()

    _ensure_session()

    clean = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in prompt[:20]).strip("_")
    model_short = model.split("/")[-1][:12]
    title = f"{model_short}-{clean}" if clean else f"{model_short}-{int(start_ts)}"

    q_model = shlex.quote(model)
    q_prompt = shlex.quote(prompt)
    cwd_cmd = f"cd {shlex.quote(str(cwd))} && " if cwd else ""

    if use_agy:
        # Launch agy in interactive mode (-i). The TUI stays open for the user;
        # monitoring detects CHECKPOINT in brain transcript to know first turn is done.
        bash_cmd = (
            f"{cwd_cmd}"
            f"agy --dangerously-skip-permissions --model {q_model} -i {q_prompt}"
        )
        agent_name = "agy"
    else:
        bash_cmd = (
            f"{cwd_cmd}"
            f"claude --bare --model {q_model} --dangerously-skip-permissions {q_prompt}"
        )
        agent_name = "claude"

    pane_id = _allocate_pane()

    try:
        _respawn(bash_cmd, pane_id)
        _rename(title)
    except Exception:
        return 1

    print(f"[Subagent] Model: {model}", file=sys.stderr)
    print(f"[Subagent] Backend: {agent_name}", file=sys.stderr)
    print(f"[Subagent] Attach: tmux attach -t {SESSION}", file=sys.stderr)
    print(f"[Subagent] Waiting for {agent_name} to complete turn...", file=sys.stderr)

    try:
        if use_agy:
            return _watch_agy_logs(start_ts)
        else:
            return _watch_claude_logs(start_ts)
    finally:
        _cleanup_pane(pane_id)


# ---------------------------------------------------------------------------
# Model validation
# ---------------------------------------------------------------------------

def validate_allowed_model(requested_model, matched_model):
    allowed = ["deepseek-v4-flash", "deepseek-v4-pro", "gemini-3.5-flash-lite",
               "gemini-3.1-pro", "gemini-3.6-flash", "haiku"]
    for a in allowed:
        if requested_model.startswith(a) or matched_model.startswith(a):
            return
    print(f"Error: Delegating to {requested_model} (resolved to {matched_model}) is prohibited. "
          f"Please use a permitted model: {', '.join(allowed)}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    models = ", ".join(get_available_models(DEFAULT_CONFIG_PATH))

    parser = argparse.ArgumentParser(
        description="Spawn Claude Code TUI or agy in tmux pane, or execute directly.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Available Models:\n  {models}")

    parser.add_argument("filepath", nargs="?", help="Path to the file to modify, or a technical spec if --spec is not provided")
    parser.add_argument("--spec", help="Technical spec describing the modifications")

    parser.add_argument("-p", "--prompt", help="Direct task prompt for the subagent (alternative to filepath/spec).")
    parser.add_argument("-m", "--model", default="deepseek-v4-flash", help="Model name from litellm config.yaml")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="Path to litellm config.yaml")
    parser.add_argument("--cwd", help="Working directory (default: current)")
    parser.add_argument("--no-tmux", action="store_true", help="Skip tmux, use -p mode directly via CLI")
    parser.add_argument("--use-agy", action="store_true", help="Use agy CLI instead of claude CLI")
    parser.add_argument("-l", "--list", action="store_true", help="List available models from LiteLLM config")

    args = parser.parse_args()

    if args.list:
        list_available_models(args.config)
        sys.exit(0)

    valid, msg, _ = validate_model(args.model, config_path=args.config)
    if not valid:
        print(f"Error: {msg}", file=sys.stderr)
        sys.exit(1)

    matched_model = msg
    validate_allowed_model(args.model, matched_model)
    args.model = matched_model

    # Resolve prompt from args
    final_prompt = None
    if args.prompt:
        final_prompt = args.prompt
    else:
        filepath_arg = None
        spec_arg = None

        if args.filepath and not args.spec:
            potential_path = Path(args.filepath)
            if potential_path.exists():
                parser.error('A technical spec is required when editing an existing file.')
            else:
                spec_arg = args.filepath
        elif args.filepath and args.spec:
            filepath_arg = args.filepath
            spec_arg = args.spec
        elif not args.filepath and args.spec:
            spec_arg = args.spec
        else:
            parser.error('A technical spec, task description, or --prompt is required.')

        if filepath_arg:
            filepath = Path(filepath_arg).resolve()
            if not filepath.exists():
                print(f"Error: File {filepath} does not exist.", file=sys.stderr)
                sys.exit(1)
            final_prompt = f"Apply this technical spec: '{spec_arg}' to the file: '{filepath}'"
        else:
            final_prompt = spec_arg

    # ⚠️ Prepend anti-recursion preamble to every subagent prompt.
    # This is the ONLY context the subagent gets — no Hermes system prompt,
    # no AGENTS.md delegation rules, no memory bleed. Just its task.
    final_prompt = ANTI_RECURSION_PREAMBLE + final_prompt

    # Context hiding setup — temporarily move GEMINI.md and CLAUDE.md aside
    gemini_md = Path.home() / ".gemini" / "GEMINI.md"
    claude_md = Path.home() / ".claude" / "CLAUDE.md"

    for md_path in [gemini_md, claude_md]:
        bak_path = md_path.with_name(md_path.name + ".bak")
        if bak_path.exists() and not md_path.exists():
            bak_path.rename(md_path)
            print(f"[Subagent] Recovered {bak_path} \u2192 {md_path}", flush=True)

    renamed_files = []

    # Read ONLY ANTHROPIC_API_KEY from .zshrc for claude auth.
    # DO NOT source the full .zshrc — that leaks orchestrator env into subagent.
    zshrc_path = Path.home() / ".zshrc"
    if zshrc_path.exists():
        for line in open(zshrc_path):
            line = line.strip()
            if line.startswith("export ANTHROPIC_API_KEY="):
                os.environ["ANTHROPIC_API_KEY"] = line.split("=", 1)[1].strip('"').strip("'")

    try:
        if gemini_md.exists():
            gemini_md.rename(gemini_md.with_name(gemini_md.name + ".bak"))
            renamed_files.append(gemini_md)
        if claude_md.exists():
            claude_md.rename(claude_md.with_name(claude_md.name + ".bak"))
            renamed_files.append(claude_md)

        if args.no_tmux:
            cli = "agy" if args.use_agy else "claude"
            print(f"[Direct] Backend: {cli}, Model: {args.model}", file=sys.stderr)
            cmd = [cli, "--dangerously-skip-permissions", "--model", args.model, "-p", final_prompt] if cli == "agy" else \
                  [cli, "--model", args.model, "--dangerously-skip-permissions", "-p", final_prompt]
            ret_code = subprocess.run(cmd).returncode
            sys.exit(ret_code)
        else:
            active_cwd = args.cwd if args.cwd else os.getcwd()
            sys.exit(run_in_tmux(model=args.model, prompt=final_prompt, cwd=active_cwd, use_agy=args.use_agy))
    finally:
        for original_path in renamed_files:
            bak_path = original_path.with_name(original_path.name + ".bak")
            if bak_path.exists():
                bak_path.rename(original_path)


if __name__ == "__main__":
    main()