---
title: "Implement GitHub Context Workflow"
date: "2026-08-13"
conversation_id: "9fac1a43-98fb-4960-bb5c-32ebe33d63a7"
source: "antigravity"
---

# Implement GitHub Context Workflow

## User

Perform 3 file edits to implement the GitHub-based Perplexity context workflow:

1. Target File: /Users/matt/projects/ai-os/scripts/preflight.py
Update step_git() to check for uncommitted changes and prompt/warn about uncommitted work:

Replace lines 107-118 in /Users/matt/projects/ai-os/scripts/preflight.py:
def step_git():
    if os.path.exists(".git"):
        _, diff_code = run_cmd(["git", "diff", "--quiet"], timeout=1)
        _, cached_code = run_cmd(["git", "diff", "--cached", "--quiet"], timeout=1)
        _, untracked_out = run_cmd(["git", "ls-files", "--others", "--exclude-standard"], timeout=1)
        has_local_changes = (diff_code != 0 or cached_code != 0 or len(untracked_out) > 0)
        
        if has_local_changes:
            # Count modified/untracked files
            status_out, _ = run_cmd(["git", "status", "--porcelain"], timeout=1)
            num_changes = len(status_out.strip().splitlines()) if status_out else 0
            if num_changes > 10:
                print(f"\n⚠️ WARNING: {num_changes} uncommitted file changes detected! Please review and commit changes via auto_commit.py or ask the user before proceeding.\n")
                return f"Git: WARNING ({num_changes} uncommitted changes — commit required before Perplexity plan)"
            return f"Git: OK ({num_changes} uncommitted changes present — commit before planning)"
        
        out, code = run_cmd(["git", "pull"], timeout=5)
        if code == 0:
            res_str = "Up-to-date" if "Already up to date" in out else "Pulled changes"
            return f"Git: OK ({res_str})"
        return "Git: WARNING (pull failed or timed out)"
    return "Git: Skipped (no .git)"

2. Target File: /Users/matt/projects/ai-os/scripts/generate_planner_prompt.py
Update the output prompt formatting to include GitHub connector instructions at the top of planner_prompt.txt.

In /Users/matt/projects/ai-os/scripts/generate_planner_prompt.py, get remote repo name via `git config --get remote.origin.url` and prepend GitHub instruction to planner_prompt.txt:

Replace lines 67-70:
    # Get remote github repo name if available
    repo_name = ""
    try:
        remote_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"], text=True).strip()
        # Parse github repo name e.g. owner/repo from https://github.com/owner/repo.git or git@github.com:owner/repo.git
        m = re.search(r"github\.com[:/]([^/]+/[^/.]+)", remote_url)
        if m:
            repo_name = m.group(1)
    except Exception:
        pass

    github_header = ""
    if repo_name:
        github_header = f"[IMPORTANT: Ensure all changes are committed and pushed to GitHub. Use the GitHub connector for repo '{repo_name}' to access live file context.]\n\n"

    # write planner prompt
    with open("./tmp/planner_prompt.txt", "w") as f:
        f.write(github_header + user_request)

3. Target File: /Users/matt/.gemini/config/global_workflows/proxima-planner.md
Update line 10 to include committing and pushing uncommitted work to GitHub first:

Replace line 10 in proxima-planner.md:
3. Pre-flight Git Check & Auto-Commit: Ensure all uncommitted changes are committed and pushed (`python3 ~/projects/ai-os/scripts/auto_commit.py`) so Perplexity can read the latest commits via the GitHub connector.
4. Run `python3 ~/projects/ai-os/scripts/generate_planner_prompt.py "<insert user request here>"` — this generates `./tmp/planner_prompt.txt` with GitHub connector instructions included.

---

## Assistant

The requested file edits to implement the GitHub-based Perplexity context workflow have been successfully completed:

1.  **`/Users/matt/projects/ai-os/scripts/preflight.py`**: Updated `step_git()` to detect and warn about uncommitted local changes, preventing workflows from proceeding if significant uncommitted work is detected.
2.  **`/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py`**: Added logic to parse the `remote.origin.url` to identify the GitHub repository and inject an important header into `planner_prompt.txt` that reminds the user to commit and push their changes for the GitHub connector.
3.  **`/Users/matt/.gemini/config/global_workflows/proxima-planner.md`**: Updated the planner workflow documentation to explicitly include committing and pushing changes to GitHub as a required step before planning.

All changes have been verified and reported to the parent agent.

---
