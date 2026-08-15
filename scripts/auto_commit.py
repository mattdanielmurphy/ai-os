#!/usr/bin/env python3
import subprocess
import sys
import json
import os
import urllib.request
import urllib.error
import argparse
from pathlib import Path

def write_result(path, status, sha=None, message=None, error=None):
    if not path:
        return
    data = {"status": status}
    if sha: data["sha"] = sha
    if message: data["message"] = message
    if error: data["error"] = error
    try:
        with open(path, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Failed to write result: {e}", file=sys.stderr)

def run_cmd(args, check=True):
    try:
        res = subprocess.run(args, capture_output=True, text=True, check=check)
        return res.stdout.strip(), res.returncode
    except subprocess.CalledProcessError as e:
        print(f"Command {' '.join(args)} failed: {e.stderr}", file=sys.stderr)
        if check:
            sys.exit(e.returncode)
        return "", e.returncode

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-path", help="Path to write JSON status")
    args, unknown = parser.parse_known_args()
    result_path = args.result_path
    # 0. Check and update any active task in-progress to review status
    import glob
    import re
    features = glob.glob(".devtool/features/*.md")
    for feat_path in features:
        try:
            with open(feat_path, "r", encoding="utf-8") as f:
                content = f.read()
            if re.search(r'status:\s*["\']?in-progress["\']?', content):
                new_content = re.sub(r'status:\s*["\']?in-progress["\']?', 'status: "review"', content)
                with open(feat_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Moved active task {feat_path} to 'review' status.")
        except Exception as e:
            print(f"Warning: Failed to read/update task file {feat_path}: {e}", file=sys.stderr)

    # Post-flight step: Auto-update Discussions.html for the active project
    discussions_script = Path(__file__).parent / "discussions_html.py"
    if discussions_script.exists():
        try:
            print("Generating updated Discussions.html...")
            run_cmd([sys.executable, str(discussions_script)], check=False)
        except Exception as e:
            print(f"Warning: Failed to auto-generate Discussions.html: {e}", file=sys.stderr)

    # 1. Stage all changes
    print("Staging changes...")
    run_cmd(["git", "add", "."])

    # 2. Check if there are any staged changes
    _, code = run_cmd(["git", "diff", "--cached", "--quiet"], check=False)
    if code == 0:
        print("No staged changes to commit.")
        write_result(result_path, "no_changes")
        sys.exit(0)

    # 3. Get the cached diff (cap characters to prevent context blowout)
    diff, _ = run_cmd(["git", "diff", "--cached"])
    if len(diff) > 8000:
        diff = diff[:8000] + "\n\n... [Diff truncated to protect context] ..."

    # 4. Request commit message from local LiteLLM proxy
    print("Generating commit message via LiteLLM...")
    prompt = (
        "You are a technical assistant. Generate a concise, clear git commit message (1-2 sentences max) summarizing the staged changes.\n"
        "Format the commit message as: \"<Action verb in present tense>: <Concise description of changes made>\"\n"
        "Do not include generic messages like 'updated files'. Be specific about what changed.\n"
        "Do not include any other text, markdown formatting, or surrounding quotes. Respond with ONLY the commit message itself.\n\n"
        f"Here is the diff:\n{diff}"
    )

    req_data = json.dumps({
        "model": "deepseek-v4-flash-high",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 400,
        "temperature": 0.2
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://localhost:8082/v1/chat/completions",
        data=req_data,
        headers={"Content-Type": "application/json"}
    )

    # Build an informative fallback message based on staged files rather than generic "Update files"
    staged_status, _ = run_cmd(["git", "status", "--porcelain"])
    staged_files = [line.strip().split()[-1] for line in staged_status.splitlines() if line.strip()]
    if staged_files:
        files_summary = ", ".join(staged_files[:3])
        if len(staged_files) > 3:
            files_summary += f" and {len(staged_files) - 3} other file(s)"
        commit_msg = f"Update {files_summary}"
    else:
        commit_msg = "Update project files"

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            message = res_body["choices"][0]["message"]
            content = message.get("content")
            if content:
                content = content.strip()
                # Clean up the output in case it wrapped with quotes
                if content.startswith('"') and content.endswith('"'):
                    content = content[1:-1].strip()
                if content.startswith("'") and content.endswith("'"):
                    content = content[1:-1].strip()
                if content:
                    if content.startswith("[Auto-Commit] "):
                        content = content[len("[Auto-Commit] "):]
                    commit_msg = content
            else:
                reasoning = message.get("reasoning_content") or message.get("reasoning")
                if reasoning:
                    print(f"Warning: Model returned reasoning but no content: {reasoning[:100]}...", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Failed to generate commit message via LiteLLM ({e}). Using fallback.", file=sys.stderr)

    print(f"Committing with message: {commit_msg}")
    
    # 5. Execute git commit
    run_cmd(["git", "commit", "-m", commit_msg])
    sha, _ = run_cmd(["git", "rev-parse", "HEAD"])
    print(f"Git commit completed successfully! SHA: {sha}")
    write_result(result_path, "committed", sha=sha, message=commit_msg)

    # 6. Push changes to remote repository
    print("Pushing commits to remote repository...")
    _, push_code = run_cmd(["git", "push"], check=False)
    if push_code == 0:
        print("Git push completed successfully!")
    else:
        print("Warning: git push failed or no remote configured.", file=sys.stderr)

if __name__ == "__main__":
    main()

