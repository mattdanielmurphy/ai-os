---
title: "Update Planner Prompt Script"
date: "2026-08-13"
conversation_id: "56e5a705-9e18-4876-a765-24f509ee7db8"
source: "antigravity"
---

# Update Planner Prompt Script

## User

Please update /Users/matt/projects/ai-os/scripts/generate_planner_prompt.py to automatically include AG_CONTEXT.md if it exists in the project root.

Here is what needs to be added to generate_planner_prompt.py:
1. Check if `./AG_CONTEXT.md` exists.
2. If it exists, read its contents into a string variable `ag_context_str` formatted like:
\n--- AG_CONTEXT.md ---\n<content>\n
3. Include `{ag_context_str}` in the `prompt_content` string before `log_context` or `repo_info`.

Use replace_file_content to make the precise edit to /Users/matt/projects/ai-os/scripts/generate_planner_prompt.py.

---

## Assistant

The update to `/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py` has been completed. The script will now check for the existence of `./AG_CONTEXT.md` in the project root and, if found, include its content in the generated planner prompt.

---
