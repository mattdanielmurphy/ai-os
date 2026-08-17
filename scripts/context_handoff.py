#!/usr/bin/env python3
import argparse
import datetime
import glob
import json
import os
import subprocess
import sys


def find_project_root():
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    curr = cwd
    while curr and curr != "/" and curr != home:
        if any(
            os.path.exists(os.path.join(curr, marker))
            for marker in [".git", "package.json", "Cargo.toml", "requirements.txt", "AG_CONTEXT.md"]
        ):
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return cwd


def run_cmd(cmd, cwd):
    try:
        res = subprocess.run(
            cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5
        )
        return res.stdout.strip()
    except Exception as e:
        return f"Error running {cmd}: {e}"


def get_active_task(root_dir):
    devtool_dir = os.path.join(root_dir, ".devtool", "features")
    if os.path.exists(devtool_dir):
        files = glob.glob(os.path.join(devtool_dir, "*.md"))
        in_progress = []
        for fpath in files:
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                    if 'status: "in-progress"' in content or "status: 'in-progress'" in content or 'status: in-progress' in content:
                        in_progress.append((fpath, content))
            except Exception:
                pass
        if in_progress:
            fpath, content = in_progress[0]
            fname = os.path.basename(fpath)
            # Extract title or first header
            lines = content.splitlines()
            header = fname
            body_lines = []
            for l in lines:
                if l.startswith("# "):
                    header = l[2:].strip()
                elif not l.startswith("---") and not ":" in l and l.strip():
                    body_lines.append(l.strip())
            summary = " ".join(body_lines[:3]) if body_lines else "Active feature task."
            return f"**Active Feature ({fname}):** {header}\n{summary}"

    # Fallback to AG_CONTEXT.md
    ag_context_path = os.path.join(root_dir, "AG_CONTEXT.md")
    if os.path.exists(ag_context_path):
        try:
            with open(ag_context_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                return "".join(lines[:10]).strip()
        except Exception:
            pass

    return "No explicit active task file found."


def get_active_plan(root_dir):
    plans_dir = os.path.join(root_dir, "plans")
    if not os.path.exists(plans_dir):
        return None

    status_files = glob.glob(os.path.join(plans_dir, "*", "status.json"))
    for sf in status_files:
        try:
            with open(sf, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("status") == "IN_PROGRESS":
                    plan_name = data.get("plan_name", os.path.basename(os.path.dirname(sf)))
                    curr_step = data.get("current_step", "01")
                    steps = data.get("steps", [])
                    step_title = ""
                    for s in steps:
                        if s.get("id") == curr_step:
                            step_title = s.get("title", "")
                    return f"**Plan:** `{plan_name}` | **Current Step:** `{curr_step}` ({step_title})"
        except Exception:
            pass
    return None


def get_recent_decisions(root_dir):
    # Check DEVELOPMENT_JOURNAL.md
    journal_path = os.path.join(root_dir, "DEVELOPMENT_JOURNAL.md")
    if os.path.exists(journal_path):
        try:
            with open(journal_path, "r", encoding="utf-8") as f:
                content = f.read()
                entries = content.strip().split("\n\n")
                recent = entries[-2:] if len(entries) >= 2 else entries
                return "\n".join(recent)
        except Exception:
            pass

    # Fallback to agent-logs/
    logs_dir = os.path.join(root_dir, "agent-logs")
    if os.path.exists(logs_dir):
        logs = sorted(glob.glob(os.path.join(logs_dir, "*.md")), reverse=True)
        if logs:
            try:
                with open(logs[0], "r", encoding="utf-8") as f:
                    return f.read()[:500]
            except Exception:
                pass

    return "No recent journal or agent log found."


def launch_antigravity_handoff(payload_text: str):
    import subprocess
    # Copy payload to clipboard
    try:
        proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        proc.communicate(input=payload_text.encode("utf-8"))
    except Exception as e:
        print(f"Clipboard error: {e}")

    # Trigger Shift+Cmd+O twice in Antigravity
    applescript = '''
    tell application "Antigravity" to activate
    repeat 10 times
        tell application "System Events"
            if frontmost of process "Antigravity" is true then exit repeat
        end tell
        delay 0.1
    end repeat
    delay 0.3
    tell application "System Events"
        key code 31 using {command down, shift down}
        delay 0.3
        key code 31 using {command down, shift down}
        delay 0.6
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])
    print("[context_handoff] Triggered Antigravity new conversation via Shift+Cmd+O twice.")


def main():
    parser = argparse.ArgumentParser(description="Generate context handoff document for thread restoration.")
    parser.add_argument("--goal", help="Override active goal description")
    parser.add_argument("--completed", help="Override completed items description")
    parser.add_argument("--next_steps", help="Override next steps description")
    parser.add_argument("--discoveries", help="Override key discoveries/decisions")
    parser.add_argument(
        "--compact-and-launch",
        "--trigger-antigravity",
        action="store_true",
        help="Generate payload, copy to clipboard, and trigger new Antigravity thread.",
    )

    args = parser.parse_args()

    root_dir = find_project_root()
    tmp_dir = os.path.join(root_dir, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    handoff_path = os.path.join(tmp_dir, "context_handoff.md")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Gather automated context
    auto_goal = get_active_task(root_dir)
    auto_plan = get_active_plan(root_dir)
    auto_decisions = get_recent_decisions(root_dir)

    git_status = run_cmd(["git", "status", "--porcelain"], root_dir)
    git_diff_stat = run_cmd(["git", "diff", "--stat"], root_dir)
    git_staged_stat = run_cmd(["git", "diff", "--staged", "--stat"], root_dir)
    git_log = run_cmd(["git", "log", "-n", "5", "--oneline"], root_dir)

    goal_text = args.goal if args.goal else auto_goal
    decisions_text = args.discoveries if args.discoveries else (args.completed if args.completed else auto_decisions)

    changes_summary = []
    if git_status:
        changes_summary.append("```\n" + git_status + "\n```")
    if git_staged_stat:
        changes_summary.append("**Staged Diff Stat:**\n```\n" + git_staged_stat + "\n```")
    if git_diff_stat:
        changes_summary.append("**Unstaged Diff Stat:**\n```\n" + git_diff_stat + "\n```")
    if not changes_summary:
        changes_summary.append("Working directory is clean.")

    changes_text = "\n\n".join(changes_summary)

    next_steps_text = args.next_steps if args.next_steps else "Proceed to next pending step in active plan or task file."

    plan_section = f"\n## Active Plan Status\n{auto_plan}\n" if auto_plan else ""

    content = f"""# Context Handoff

**Generated:** `{now}`  
**Project Root:** `{root_dir}`

## Current Task & Goal
{goal_text}
{plan_section}
## Key Decisions & Recent Progress
{decisions_text}

## Changed Files & Git Status
{changes_text}

## Recent Commits
```
{git_log if git_log else 'No recent commits.'}
```

## Immediate Next Steps
{next_steps_text}
"""

    with open(handoff_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Context handoff generated successfully at: {handoff_path}")
    print(f"HANDOFF_FILE_PATH={handoff_path}")

    if args.compact_and_launch:
        try:
            launch_antigravity_handoff(content)
        except Exception as e:
            print(f"Error launching Antigravity: {e}")


if __name__ == "__main__":
    main()
