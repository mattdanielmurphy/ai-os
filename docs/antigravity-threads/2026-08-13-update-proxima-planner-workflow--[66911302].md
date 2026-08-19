---
title: "Update Proxima Planner Workflow"
date: "2026-08-13"
conversation_id: "66911302-7997-4e43-9bb6-ccd4f15a0003"
source: "antigravity"
---

# Update Proxima Planner Workflow

## User

Please update /Users/matt/.gemini/config/global_workflows/proxima-planner.md:

Align the workflow steps with the new generate_planner_prompt.py script behavior:

1. **Sanity Check**: Verify project directory.
2. **Pre-flight Git Check**: Ensure a GitHub remote is configured (`git config --get remote.origin.url`). If missing, STOP and ask the user if they want to create a remote repository.
3. **Run Prompt Script**: Run `python3 ~/projects/ai-os/scripts/generate_planner_prompt.py "<request>"`.
4. **Invoke Perplexity**: Call `proxima:ask_perplexity` with `./tmp/planner_prompt.txt` message content. Instruct Perplexity to query the GitHub connector for repo source code/docs.
5. **Format Output**: Format output into `implementation_plan.md`.

---

## Assistant

The workflow file `/Users/matt/.gemini/config/global_workflows/proxima-planner.md` has been updated as requested.

---
