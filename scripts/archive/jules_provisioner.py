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

def build_context_file(task_description, context_files=None, system_directives_file=None, ag_context_file=None):
    sections = [
        "# AGENT & ARCHITECTURAL DIRECTIVES FOR JULES\n",
        "## 1. Primary Task Goal",
        f"{task_description}\n"
    ]

    # 1. System Directives (Global operational rules, safety guardrails, constraints)
    if system_directives_file and os.path.exists(system_directives_file):
        sections.append("## 2. System Directives & Behavioral Guardrails")
        with open(system_directives_file) as f:
            sections.append(f.read())
        sections.append("")

    # 2. AG_CONTEXT.md (Project architectural durable context)
    if ag_context_file and os.path.exists(ag_context_file):
        sections.append("## 3. AG_CONTEXT.md (Project Architecture & Durable Knowledge)")
        with open(ag_context_file) as f:
            sections.append(f.read())
        sections.append("")

    # 3. Task Context Files
    if context_files:
        sections.append("## 4. Relevant Source Code Files\n")
        for cf in context_files:
            if os.path.exists(cf):
                sections.append(f"### File: {os.path.basename(cf)}")
                sections.append("```")
                with open(cf) as f:
                    sections.append(f.read())
                sections.append("```\n")

    return "\n".join(sections)

def cmd_provision(args):
    repo = args.repo or DEFAULT_SANDBOX_REPO
    task_prompt = args.prompt
    branch_name = args.branch or f"jules-task-{int(os.path.getmtime(__file__))}"

    print(f"[*] Preparing micro-task context for repo: {repo}")
    
    ag_context_path = args.ag_context or os.path.expanduser("~/projects/ai-os/AG_CONTEXT.md")
    directives_path = args.directives or os.path.expanduser("~/projects/ai-os/.rules/common.md")

    agents_content = build_context_file(
        task_prompt,
        context_files=args.files,
        system_directives_file=directives_path,
        ag_context_file=ag_context_path
    )
    
    tmp_dir = Path("/Users/matt/projects/ai-os/tmp/jules_sandbox")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"[*] Cloning sandbox repo {repo}...")
    run_cmd(f"gh repo clone {repo} {tmp_dir}")

    agents_md_path = tmp_dir / "AGENTS.md"
    with open(agents_md_path, "w") as f:
        f.write(agents_content)

    print("[*] Committing context & pushing to origin main...")
    run_cmd("git checkout -b main 2>/dev/null || git checkout main", cwd=tmp_dir, check=False)
    run_cmd("git add AGENTS.md", cwd=tmp_dir)
    run_cmd(f'git commit -m "jules-provision: inject directives & AG_CONTEXT.md for {branch_name}"', cwd=tmp_dir, check=False)
    run_cmd("git push origin main", cwd=tmp_dir, check=False)

    print("[*] Dispatching task session via jules_delegate.py...")
    delegate_script = "/Users/matt/projects/ai-os/scripts/jules_delegate.py"
    dispatch_cmd = f'python3 {delegate_script} create --repo {repo} --prompt "{task_prompt} (Refer to AGENTS.md for system directives, AG_CONTEXT.md, and source code files)"'
    out = run_cmd(dispatch_cmd)
    print("\n=== Jules Session Dispatched Successfully ===")
    print(out)

def main():
    parser = argparse.ArgumentParser(description="Jules Micro-Repo Context Provisioner")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_prov = subparsers.add_parser("provision", help="Provision context & dispatch to Jules")
    p_prov.add_argument("--prompt", required=True, help="Task prompt for Jules")
    p_prov.add_argument("--repo", default=DEFAULT_SANDBOX_REPO, help="Target GitHub repo")
    p_prov.add_argument("--branch", help="Custom branch name")
    p_prov.add_argument("--files", nargs="*", help="Local file paths to inject into AGENTS.md")
    p_prov.add_argument("--directives", help="Path to system directives file (e.g. .rules/common.md)")
    p_prov.add_argument("--ag-context", help="Path to project AG_CONTEXT.md file")

    args = parser.parse_args()
    if args.command == "provision":
        cmd_provision(args)

if __name__ == "__main__":
    main()
