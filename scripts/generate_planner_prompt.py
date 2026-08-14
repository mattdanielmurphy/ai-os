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
    
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    user_request = args.request
    
    # 1. Check Git repo & remote
    if not os.path.exists(".git"):
        print("❌ ERROR: No Git remote configured for this project.")
        print("ACTION REQUIRED: Check if a GitHub remote exists or create one (e.g. via 'gh repo create --private'). Perplexity GitHub connector requires a synced GitHub repo.")
        sys.exit(1)
        
    try:
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
    log_dir = Path("./agent-logs/")
    if log_dir.exists():
        keywords = [w for w in re.findall(r'\w+', user_request.lower()) if len(w) > 3]
        matching_logs = []
        
        for log_file in log_dir.glob("*.log"):
            content = log_file.read_text(errors='ignore')
            if any(k in content.lower() for k in keywords):
                matching_logs.append(log_file)
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
    if os.path.exists("./AG_CONTEXT.md"):
        ag_context_str = "\n--- AG_CONTEXT.md ---\n" + Path("./AG_CONTEXT.md").read_text() + "\n"

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

Please act as a senior planner. Analyze the request and output a detailed architectural implementation plan for the orchestrator."""

    with open("./tmp/planner_prompt.txt", "w") as f:
        f.write(prompt_content)
        
    # 5. Print execution instructions
    print("✅ Planner prompt generated at ./tmp/planner_prompt.txt")
    print("\n--- EXECUTION INSTRUCTIONS ---")
    print("1. Read the contents of ./tmp/planner_prompt.txt")
    print("2. Read the entire text of ./tmp/planner_prompt.txt and pass it VERBATIM as the `message` parameter to `proxima:ask_perplexity`. Do NOT extract or pass only the user request.")
    print("3. IMPORTANT: Do NOT perform the work yourself. Wait for the planner's response, then delegate tasks to subagents.")

if __name__ == "__main__":
    main()
