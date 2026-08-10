---
name: ai-os-auto-commit
description: Delegate git commits to agy's auto_commit.py script for cheap, AI-generated commit messages via the LiteLLM proxy.
version: 1.0.0
metadata:
  hermes:
    tags: [ai-os, git, commit, automation]
---

# AI-OS Auto-Commit

When working in the `ai-os` project at `~/projects/ai-os`, use this workflow for automated git commits. The script delegates commit message generation to the local LiteLLM proxy (localhost:8082) using a cheap model (claude-haiku), then stages and commits all changes.

## When to Use

- At the end of a session where you've made code changes
- After completing a feature or bug fix
- When you want to checkpoint work with a descriptive commit message
- **Do NOT** use for manual commits where you want a specific, hand-crafted message

## Usage

```bash
cd ~/projects/ai-os
python3 scripts/auto_commit.py
```

The script will:
1. Automatically transition any in-progress `.devtool/features/*.md` tasks to `status: "review"`
2. Stage all changes (`git add .`)
3. Generate a commit message via LiteLLM (claude-haiku) using the staged diff
4. Commit with the generated message (format: `<action>: <description>`)
5. Fall back to `Update files` if LiteLLM is unreachable

## Fallback (if LiteLLM is down)

If the LiteLLM proxy is not running, the script gracefully falls back. If you need a custom commit message instead:

```bash
git add .
git commit -m "your message here"
```

## Important

- The script is **agnostic** to who calls it — both Hermes and agy use the same script
- Always run it from the ai-os project root
- The LiteLLM proxy must be running (tmux session `litellm` on port 8082)
- Only use this in the `~/projects/ai-os` workspace
