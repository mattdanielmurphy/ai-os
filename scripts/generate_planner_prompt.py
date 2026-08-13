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
    os.makedirs("./tmp", exist_ok=True)
    prompt_content = f"""[IMPORTANT: Ensure all changes are committed and pushed to GitHub. Use the GitHub connector for repo '{repo_name}' to access live file context.]

User Request: {user_request}
{log_context}

Please act as a senior planner. Analyze the request, check the provided GitHub repository, and output a detailed plan for the orchestrator."""

    with open("./tmp/planner_prompt.txt", "w") as f:
        f.write(prompt_content)
        
    # 5. Print execution instructions
    print("✅ Planner prompt generated at ./tmp/planner_prompt.txt")
    print("\n--- EXECUTION INSTRUCTIONS ---")
    print("1. Read the contents of ./tmp/planner_prompt.txt")
    print("2. Call `proxima:ask_perplexity` with the prompt content.")
    print("3. Ensure the GitHub connector is active if the model needs live file context.")
    print("4. IMPORTANT: Do NOT perform the work yourself. Wait for the planner's response, then delegate tasks to subagents.")

if __name__ == "__main__":
    main()
