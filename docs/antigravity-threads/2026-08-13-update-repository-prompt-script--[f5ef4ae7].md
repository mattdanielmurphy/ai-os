---
title: "Update Repository Prompt Script"
date: "2026-08-13"
conversation_id: "f5ef4ae7-7c90-46c5-99e5-40e97adb1a65"
source: "antigravity"
---

# Update Repository Prompt Script

## User

Please update `/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py` so that:
1. It extracts `repo_name` from git remote `origin` (e.g., `mattdanielmurphy/lightllm` or `mattdanielmurphy/ai-os`).
2. If `repo_name` is found, it includes it explicitly in `prompt_content`. For example:
   `Target GitHub Repository: {repo_name}`
   `Please query the GitHub connector for repository source code and documentation for repo '{repo_name}' if needed.`
   or similar clear statement so that Perplexity receives the exact repository name.
3. Keep the script robust and preserve existing functionality (git remote check, agent log keyword search, writing to `./tmp/planner_prompt.txt`).

---

## Assistant

The update to `/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py` is complete. It now automatically extracts the GitHub repository name from the `origin` remote and includes it in the generated prompt for the planner, ensuring the GitHub connector receives the correct repository context.

---
