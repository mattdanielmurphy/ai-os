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
        "You are a technical assistant. Generate a concise, one-sentence git commit message summarizing the staged changes.\n"
        "Format the commit message as: \"[Auto-Commit] <Action verb in present tense>: <Concise description>\"\n"
        "Do not include any other text, markdown formatting, or surrounding quotes. Respond with ONLY the commit message itself.\n\n"
        f"Here is the diff:\n{diff}"
    )

    req_data = json.dumps({
        "model": "claude-haiku*",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
        "temperature": 0.2
    }).encode("utf-8")

    req = urllib.request.Request(
        "http://localhost:8082/v1/chat/completions",
        data=req_data,
        headers={"Content-Type": "application/json"}
    )

    commit_msg = "[Auto-Commit] Update files"
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            content = res_body["choices"][0]["message"]["content"].strip()
            # Clean up the output in case it wrapped with quotes
            if content.startswith('"') and content.endswith('"'):
                content = content[1:-1].strip()
            if content.startswith("'") and content.endswith("'"):
                content = content[1:-1].strip()
            if content:
                commit_msg = content
    except Exception as e:
        print(f"Warning: Failed to generate commit message via LiteLLM ({e}). Using fallback.", file=sys.stderr)

    print(f"Committing with message: {commit_msg}")
    
    # 5. Execute git commit
    run_cmd(["git", "commit", "-m", commit_msg])
    print("Git commit completed successfully!")

if __name__ == "__main__":
    main()
