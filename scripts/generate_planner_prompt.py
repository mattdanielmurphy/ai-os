#!/usr/bin/env python3
import sys
import os
import subprocess
import re
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Generate planner prompt for Perplexity")
    parser.add_argument("request", help="User request string")
    parser.add_argument("--image-desc", help="Description of attached image", default=None)
    parser.add_argument("--context", help="Context mode", default="full")
    
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    user_request = args.request
    
    # 1. Check Git repo & remote
    is_git = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], capture_output=True, text=True)
    if is_git.returncode != 0 or is_git.stdout.strip() != "true":
        print("❌ ERROR: No Git repository detected for this project.")
        print("ACTION REQUIRED: Check if a GitHub remote exists or create one (e.g. via 'gh repo create --private'). Perplexity GitHub connector requires a synced GitHub repo.")
        sys.exit(1)

    try:
        git_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
        remote_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], text=True).strip()
        if not remote_url:
            raise Exception("Empty remote URL")
        
        m = re.search(r"github\.com[:/]([^/]+/[^/.]+)", remote_url)
        repo_name = m.group(1) if m else "unknown"
    except Exception:
        print("❌ ERROR: No Git remote configured for this project.")
        print("ACTION REQUIRED: Check if a GitHub remote exists or create one (e.g. via 'gh repo create --private'). Perplexity GitHub connector requires a synced GitHub repo.")
        sys.exit(1)

    # 2. Keyword match agent logs
    log_context = ""
    log_dirs = [Path("./agent-logs/"), Path(git_root) / "agent-logs/"]
    matching_logs = []
    
    keywords = [w for w in re.findall(r'\w+', user_request.lower()) if len(w) > 3]
    
    for log_dir in log_dirs:
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                content = log_file.read_text(errors='ignore')
                if any(k in content.lower() for k in keywords):
                    matching_logs.append(log_file)
                    if len(matching_logs) >= 3:
                        break
        if len(matching_logs) >= 3:
            break
            
    if matching_logs:
        log_context = "\n--- Relevant Agent Logs ---\n"
        for log in matching_logs:
            lines = log.read_text(errors='ignore').splitlines()
            summary = "\n".join(lines[-10:])
            log_context += f"\nFile: {log.name}\n{summary}\n"

    # 3 & 4. Write final prompt
    ag_context_str = ""
    ag_context_paths = [Path("./AG_CONTEXT.md"), Path(git_root) / "AG_CONTEXT.md"]
    for path in ag_context_paths:
        if path.exists():
            ag_context_str = "\n--- AG_CONTEXT.md ---\n" + path.read_text() + "\n"
            break

    os.makedirs("./tmp", exist_ok=True)
    if repo_name != "unknown":
        repo_info = (
            f"\n--- GitHub Connector Context ---\n"
            f"Target Private Repository: '{repo_name}'\n"
            f"IMPORTANT: You have access to my authenticated GitHub account via your GitHub connector. "
            f"Please use your GitHub connector to directly read, search, and inspect the codebase, files, and documentation "
            f"in my repository '{repo_name}' (including private files and configs) as needed to construct this plan.\n"
        )
    else:
        repo_info = ""
    if args.image_desc:
        image_context = f"\n--- Visual Context & Image Description ---\n{args.image_desc}\n"
    else:
        image_context = ""
        
    prompt_content = f"""User Request: {user_request}
{image_context}{ag_context_str}{repo_info}{log_context}

Please act as a senior architect and systems planner. Analyze the request and output a detailed, actionable implementation plan for the orchestrator.

The plan MUST include:
1. Architectural Strategy: High-level overview of the proposed approach.
2. Data Structures & State Management: Define new data structures or changes to existing state.
3. API/Interface Contracts: Define function signatures, classes, and expected interface contracts.
4. Logic Flow & Algorithms: Step-by-step pseudo-code or logic description for the main execution flow.
5. Error Handling & Edge Cases: Identify potential failure points and mitigation strategies.
6. Implementation Steps: A list of specific files to modify and the required changes in each, ordered for execution.

DO NOT provide full code implementations. Focus on structural details, signatures, and clear instructions so that downstream agents can implement the changes efficiently without guessing. Ensure all decisions are concrete and leave no gaps in requirements."""

    with open("./tmp/planner_prompt.txt", "w") as f:
        f.write(prompt_content)
        
    # 5. Print execution instructions
    print("✅ Planner prompt generated at ./tmp/planner_prompt.txt")
    print("\n--- EXECUTION INSTRUCTIONS ---")
    print("1. Read the contents of ./tmp/planner_prompt.txt")
    print("2. Run the following command via `run_command` (with `WaitMsBeforeAsync: 500`):")
    print("   node ~/projects/ai-os/scripts/query_aios.js --plan \"<request>\"")
    print("3. CRITICAL: NEVER pass files to the planner. Context is accessed via GitHub connector and the textual prompt.")
    print("4. IMPORTANT: Wait for Antigravity to notify you that the planning task is complete, then read ./tmp/planner_output.txt and delegate tasks to subagents.")


if __name__ == "__main__":
    main()
