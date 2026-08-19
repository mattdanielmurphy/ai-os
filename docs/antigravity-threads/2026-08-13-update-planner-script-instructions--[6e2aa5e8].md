---
title: "Update Planner Script Instructions"
date: "2026-08-13"
conversation_id: "6e2aa5e8-1f5f-4883-a0ab-5626a5790978"
source: "antigravity"
---

# Update Planner Script Instructions

## User

Please update /Users/matt/projects/ai-os/scripts/generate_planner_prompt.py:

Remove line 61 (`[IMPORTANT: Ensure all changes are committed and pushed to GitHub. Use the GitHub connector for repo '{repo_name}' to access live file context.]`) and any mentions of the GitHub connector directive in prompt_content and stdout instructions.

The final prompt should simply be:

User Request: {user_request}
{log_context}

Please act as a senior planner. Analyze the request and output a detailed architectural implementation plan for the orchestrator.

---

## Assistant

I have

---
