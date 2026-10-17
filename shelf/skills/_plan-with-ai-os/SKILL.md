---
name: _plan-with-ai-os
description: "Initiate high-reasoning planning via ai-os (Gemini) when explicitly requested by user."
---

# Plan With AI-OS (Gemini High Reasoning)

Run high-reasoning planning using the unified `query_aios.js` planner when explicitly requested.

> ⚠️ **SINGLE-COMMAND WORKFLOW**: There is NO separate `generate_prompt.py` or prompt-generation step. Do NOT run any such script. `query_aios.js --plan` handles everything in one command.
> ⚠️ **EXPLICIT REQUEST ONLY**: Do NOT use `query_aios` unless Matt specifically asks for it. Background companion services are stopped by default.

---

## Workflow Steps

1. **Sanity Check**: Analyze the user's request against the current active project directory.
2. **Execute Unified Planner (Single-Step Prompt & Query)**:
   - Ensure the AI-OS companion is started if Matt requested query_aios (`la start aios-server`).
   - Run `node ~/projects/ai-os/scripts/query_aios.js --plan "<request>"` using `run_command` (with `WaitMsBeforeAsync: 500`). Antigravity will notify you when the task completes.
   - This single command automatically: inspects Git context, reads agent logs, resolves contextual Antigravity thread mappings, generates `./tmp/planner_prompt.txt`, dispatches the query to Gemini webview, and writes the completed plan to `./tmp/planner_output.txt`.
   - **Thread Controls**: Use `--new-thread` / `-n` to force a new planner thread, `--resume <id>` to resume a specific session, or `--no-resume` to run standalone without modifying stored thread state.
3. **On slow or failed planner calls**:
   - The planner request stays attached to the original `query_aios.js` process. If the shell tool returns a running-process/session ID, continue waiting on that same process; do not launch a second request.
   - If the original process completed and saved its output, recover it with `node ~/projects/ai-os/scripts/query_aios.js --recover --output ./tmp/planner_output.txt`. Recovery verifies the adjacent query-state checksum and prints the saved result without contacting a provider.
4. **Format Output**: Format `./tmp/planner_output.txt` into `implementation_plan.md`.
5. **Implement by Default**: After a successful plan is available, continue the user's requested task by implementing the plan in the same task. Treat the plan as the execution guide, not as the final deliverable, unless the user explicitly asked for a plan only.
