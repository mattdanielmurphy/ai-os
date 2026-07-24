#!/usr/bin/env python3
import subprocess
import sys
import json
import urllib.request
import urllib.error

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

    # 1. Stage all changes
    print("Staging changes...")
    run_cmd(["git", "add", "."])

    # 2. Check if there are any staged changes
    _, code = run_cmd(["git", "diff", "--cached", "--quiet"], check=False)
    if code == 0:
        print("No staged changes to commit.")
        sys.exit(0)

    # 3. Get the cached diff (cap characters to prevent context blowout)
    diff, _ = run_cmd(["git", "diff", "--cached"])
    if len(diff) > 8000:
        diff = diff[:8000] + "\n\n... [Diff truncated to protect context] ..."

    # 4. Request commit message from local LiteLLM proxy
    print("Generating commit message via LiteLLM...")
    prompt = (
        "You are a technical assistant. Generate a concise, clear git commit message (1-2 sentences max) summarizing the staged changes.\n"
        "Format the commit message as: \"[Auto-Commit] <Action verb in present tense>: <Concise description of changes made>\"\n"
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
        commit_msg = f"[Auto-Commit] Update {files_summary}"
    else:
        commit_msg = "[Auto-Commit] Update project files"

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
    print("Git commit completed successfully!")

    # 6. Push changes to remote repository
    print("Pushing commits to remote repository...")
    _, push_code = run_cmd(["git", "push"], check=False)
    if push_code == 0:
        print("Git push completed successfully!")
    else:
        print("Warning: git push failed or no remote configured.", file=sys.stderr)

    # 7. Postflight Quota Delta Check
    print("\n--- Running Post-flight Quota Delta Check ---")
    snapshot_path = os.path.expanduser("~/.ag_quota_snapshot.json")
    if os.path.exists(snapshot_path):
        try:
            with open(snapshot_path, "r", encoding="utf-8") as f:
                prev_snapshot = json.load(f)
            quota_out, quota_code = run_cmd(["ag-quota", "--all", "-j"], check=False)
            if quota_code == 0 and quota_out:
                current_data = json.loads(quota_out)
                deltas = []
                for acct in current_data:
                    email = acct.get("email") or acct.get("quota_summary", {}).get("Email", "unknown")
                    models = acct.get("quota_summary", {}).get("Models", [])
                    for m in models:
                        disp = m.get("DisplayName") or m.get("ModelID", "")
                        key = f"{email} | {disp}"
                        curr_frac = m.get("RemainingFraction", 1.0)
                        if isinstance(curr_frac, (int, float)) and key in prev_snapshot:
                            prev_frac = prev_snapshot[key]
                            diff = curr_frac - prev_frac
                            if abs(diff) > 0.0001:
                                sign = "+" if diff > 0 else ""
                                deltas.append(f"{disp}: {curr_frac:.4f} ({sign}{diff:.4f})")
                if deltas:
                    print(f"Quota Delta since preflight: {', '.join(deltas)}")
                else:
                    print("Quota Delta: No quota change detected since preflight.")
        except Exception as e:
            print(f"Post-flight quota check skipped: {e}")
    else:
        print("No preflight quota snapshot found (~/.ag_quota_snapshot.json). Skipping delta check.")

if __name__ == "__main__":
    main()

