#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess
import shutil
from pathlib import Path

DEFAULT_SANDBOX_REPO = "mattdanielmurphy/gitl-emails"

def run_cmd(cmd, cwd=None, check=True):
    res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if check and res.returncode != 0:
        print(f"Command failed: {cmd}\nStderr: {res.stderr.strip()}", file=sys.stderr)
        sys.exit(res.returncode)
    return res.stdout.strip()

def build_context_file(task_description, context_files=None, rules_file=None):
    context_lines = [
        "# AGENT & ARCHITECTURAL DIRECTIVES (JULE INSTRUCTIONS)\n",
        "## Primary Task Goal",
        f"{task_description}\n",
        "## System Rules & Constraints",
        "- All code must be clean, modular, and follow established project conventions.",
        "- Do not introduce unnecessary third-party dependencies.",
        "- Ensure proper error handling and descriptive comments where needed.\n"
    ]

    if rules_file and os.path.exists(rules_file):
        context_lines.append("## Project Directives")
        with open(rules_file) as f:
            context_lines.append(f.read())
        context_lines.append("")

    if context_files:
        context_lines.append("## Relevant Context Files\n")
        for cf in context_files:
            if os.path.exists(cf):
                context_lines.append(f"### File: {os.path.basename(cf)}")
                context_lines.append("```")
                with open(cf) as f:
                    context_lines.append(f.read())
                context_lines.append("```\n")

    return "\n".join(context_lines)

def cmd_provision(args):
    repo = args.repo or DEFAULT_SANDBOX_REPO
    task_prompt = args.prompt
    branch_name = args.branch or f"jules-task-{int(os.path.getmtime(__file__))}"

    print(f"[*] Preparing micro-task context for repo: {repo} on branch: {branch_name}")
    
    # Generate AGENTS.md context payload
    agents_content = build_context_file(task_prompt, args.files, args.rules)
    
    tmp_dir = Path("/Users/matt/projects/ai-os/tmp/jules_sandbox")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Cloning sandbox repo {repo}...")
    run_cmd(f"gh repo clone {repo} {tmp_dir}")

    agents_md_path = tmp_dir / "AGENTS.md"
    with open(agents_md_path, "w") as f:
        f.write(agents_content)

    print("[*] Committing context & pushing branch...")
    run_cmd("git checkout -b main 2>/dev/null || git checkout main", cwd=tmp_dir, check=False)
    run_cmd("git add AGENTS.md", cwd=tmp_dir)
    run_cmd(f'git commit -m "jules-provision: inject task directives for {branch_name}"', cwd=tmp_dir, check=False)
    run_cmd("git push origin main", cwd=tmp_dir, check=False)

    print("[*] Dispatching task session via jules_delegate.py...")
    delegate_script = "/Users/matt/projects/ai-os/scripts/jules_delegate.py"
    dispatch_cmd = f'python3 {delegate_script} create --repo {repo} --prompt "{task_prompt} (Refer to AGENTS.md for full directives)"'
    out = run_cmd(dispatch_cmd)
    print("\n=== Jules Session Dispatched Successfully ===")
    print(out)

def main():
    parser = argparse.ArgumentParser(description="Jules Micro-Repo & Context Provisioner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_prov = subparsers.add_parser("provision", help="Provision context & dispatch to Jules")
    p_prov.add_argument("--prompt", required=True, help="Task prompt for Jules")
    p_prov.add_argument("--repo", default=DEFAULT_SANDBOX_REPO, help="Target GitHub repo (default: gitl-emails)")
    p_prov.add_argument("--branch", help="Custom branch name")
    p_prov.add_argument("--files", nargs="*", help="Local file paths to inject into AGENTS.md context")
    p_prov.add_argument("--rules", help="Path to custom rules file (e.g. AG_CONTEXT.md)")

    args = parser.parse_args()
    if args.command == "provision":
        cmd_provision(args)

if __name__ == "__main__":
    main()
