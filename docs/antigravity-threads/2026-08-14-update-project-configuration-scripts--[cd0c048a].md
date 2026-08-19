---
title: "Update Project Configuration Scripts"
date: "2026-08-14"
conversation_id: "cd0c048a-e8f6-4f65-bd88-fced58b216fd"
source: "antigravity"
---

<span style="display: flex; flex-direction: column-reverse; height: 100cqh; overflow-y: auto; position: absolute; top: 0; left: 0; right: 0; bottom: 0; padding: 4rem 1.5rem; scrollbar-width: thin;">

<span style="display: block; text-align: center; opacity: 0.45; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; padding: 0 0 2.5rem 0;">Thread Started — August 13, 2026</span>

<span style="display: block; width: 100%; margin-top: 8px;">

<span title="Sent at " style="display: table; margin-left: auto; max-width: 75%; text-align: left; background: rgba(85, 68, 197, 0.16); border: 1.5px solid rgba(85, 68, 197, 0.45); padding: 12px 16px; border-radius: 14px 14px 2px 14px; white-space: pre-wrap; line-height: 1.5; font-size: 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12);">

Perform these 3 precise edits immediately:

1. File: `/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py`
Replace lines 21-38 (the git check) with:
```python

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
```

And in `generate_planner_prompt.py`, update execution instructions at the end:
```python

    print("✅ Planner prompt generated at ./tmp/planner_prompt.txt")
    print("\n--- EXECUTION INSTRUCTIONS ---")
    print("1. Read the contents of ./tmp/planner_prompt.txt")
    print("2. Read the entire text of ./tmp/planner_prompt.txt and pass it VERBATIM as the `message` parameter to `proxima:ask_perplexity`. Do NOT extract or pass only the user request.")
    print("3. CRITICAL: NEVER pass the `files` parameter/array to `proxima:ask_perplexity`! Perplexity file upload quota is extremely limited. Context is accessed via GitHub connector and the textual prompt.")
    print("4. IMPORTANT: Do NOT perform the work yourself. Wait for the planner's response, then delegate tasks to subagents.")
```

2. File: `/Users/matt/projects/ai-os/scripts/preflight.py`
In `step_git()`:
Replace:
```python

def step_git():
    if os.path.exists(".git"):
```

with:
```python

def step_git():
    is_git_out, is_git_code = run_cmd(["git", "rev-parse", "--is-inside-work-tree"], timeout=1)
    if is_git_code == 0 and is_git_out == "true":
```

3. File: `/Users/matt/.gemini/config/global_workflows/proxima-planner.md`
Add under Step 4:
```markdown

   - **CRITICAL FILE UPLOAD BAN**: NEVER pass the `files` argument/array to `proxima:ask_perplexity`. Perplexity file upload quotas are extremely limited and valuable. Always rely on the GitHub connector and the generated text prompt.
```

Execute these edits now.

</span>



<span title="Responded at 3:16am" style="display: table; margin-right: auto; max-width: 85%; text-align: left; background: none; border: 1.5px solid rgba(113, 100, 175, 0.35); padding: 14px 18px; border-radius: 14px 14px 14px 2px; line-height: 1.6; font-size: 14px; margin-bottom: 24px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">

All requested edits have been completed successfully.
1.  **`/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py`**:
    *   Replaced the Git check logic to properly verify the repository and remote URL.
    *   Updated the execution instructions to emphasize passing the message as verbatim text and forbidding the use of the `files` parameter.
    *   Removed a redundant instruction line.
2.  **`/Users/matt/projects/ai-os/scripts/preflight.py`**:
    *   Updated the `step_git()` function to use `run_cmd` and perform a more robust check for `is-inside-work-tree`.
3.  **`/Users/matt/.gemini/config/global_workflows/proxima-planner.md`**:
    *   Added the **CRITICAL FILE UPLOAD BAN** instruction to Step 4 of the workflow documentation.

</span>



</span>

</span>