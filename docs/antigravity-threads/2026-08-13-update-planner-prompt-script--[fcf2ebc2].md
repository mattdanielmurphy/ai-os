---
title: "Update Planner Prompt Script"
date: "2026-08-13"
conversation_id: "fcf2ebc2-7a3c-4102-b0d7-c20d7fb98d62"
source: "antigravity"
---

# Update Planner Prompt Script

## User

Please update /Users/matt/projects/ai-os/scripts/generate_planner_prompt.py:

1. Check for Git repo & remote URL:
   - Check if current directory has `.git` and `remote.origin.url`.
   - If missing `.git` or missing remote URL, print a clear error and exit 1:
     `❌ ERROR: No Git remote configured for this project.`
     `ACTION REQUIRED: Check if a GitHub remote exists or create one (e.g. via 'gh repo create --private'). Perplexity GitHub connector requires a synced GitHub repo.`
2. Keyword match agent logs:
   - Look for log files in `./agent-logs/` matching keywords in `user_request` (e.g., words > 3 chars).
   - If matching logs are found, extract their file names or top matching lines (up to 3 logs).
   - Include these matching log references/summaries in the prompt string.
3. Remove repomix bundling requirement for full source files, but keep standard system instructions/headers for Perplexity.
4. Write the final formatted prompt to `./tmp/planner_prompt.txt` so the agent can read/pass it directly to `proxima:ask_perplexity`.
5. Print clear execution instructions for the orchestrator agent.

---

## Assistant

I have updated `/Users/matt/projects/ai-os/scripts/generate_planner_prompt.py` as requested.

### Key Updates:
- **Git Validation**: Added check for `.git` and `remote.origin.url`. Errors will exit with code 1 and display the required action.
- **Log Keyword Matching**: Added logic to find relevant logs in `./agent-logs/` based on user request keywords and embed their summaries into the prompt.
- **Prompt Simplification**: Removed `repomix` dependency and formatted the prompt for Perplexity using standard system instructions.
- **Output Management**: Writes the final prompt to `./tmp/planner_prompt.txt`.
- **Orchestration**: Prints clear execution steps for the orchestrator agent.

You can now use the updated script:
```bash
python3 /Users/matt/projects/ai-os/scripts/generate_planner_prompt.py "your request"
```

I have communicated these changes to the parent agent.

---
