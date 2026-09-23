---
name: _plan-with-ai-os
description: "MANDATORY: Initiate high-reasoning planning via ai-os Perplexity before executing non-trivial tasks."
---

# Plan With AI-OS (Perplexity High Reasoning)

Run high-reasoning planning using the unified `query_aios.js` planner.

> ⚠️ **SINGLE-COMMAND WORKFLOW**: There is NO separate `generate_prompt.py` or prompt-generation step. Do NOT run any such script. `query_aios.js --plan` handles everything in one command.

---

## Workflow Steps

1. **Sanity Check**: Analyze the user's request against the current active project directory.
2. **Pre-flight Git Check**: Ensure a GitHub remote is configured (`git config --get remote.origin.url`). If missing, STOP and ask the user if they want to create a remote repository.
3. **Execute Unified Planner (Single-Step Prompt & Query)**:
   - Run `node ~/projects/ai-os/scripts/query_aios.js --plan "<request>"` using `run_command` (with `WaitMsBeforeAsync: 500`). Antigravity will notify you when the task completes.
   - This single command automatically: inspects Git context, reads agent logs, resolves contextual Antigravity thread mappings (auto-resuming ongoing planner threads on turn 2+ or creating fresh threads on turn 1), generates `./tmp/planner_prompt.txt`, dispatches the query to Perplexity (Gemini Flash Thinking), and writes the completed plan to `./tmp/planner_output.txt`.
   - **Thread Controls**: Use `--new-thread` / `-n` to force a new planner thread, `--resume <id>` to resume a specific session, or `--no-resume` to run standalone without modifying stored thread state.
   - **Screenshot & Multiple Attachment Support**: Pass images via multiple `--screenshot <path>`, `--image <path>`, or `-f <path>` flags. All image paths referenced in prompts are also auto-detected and attached in batch.
   - **CRITICAL PERPLEXITY UPLOAD POLICY**: NEVER pass codebase/text files via the `files` argument. For screenshots/visual assets, upload only if quota > 25 AND elements are too complex to transcribe. Otherwise, act as the vision provider and pass `--image-desc "<description>"` in the command.
4. **On slow or failed planner calls**:
   - The planner request stays attached to the original `query_aios.js` process. If the shell tool returns a running-process/session ID, continue waiting on that same process; do not launch a second request.
   - If the original process completed and saved its output, recover it with `node ~/projects/ai-os/scripts/query_aios.js --recover --output ./tmp/planner_output.txt`. Recovery verifies the adjacent query-state checksum and prints the saved result without contacting a provider.
   - If recovery reports that the query is still running, wait for the original process. If no completed output exists, report that plainly; do not interpret an empty-prompt response as recovery.
   - For an actual `ECONNREFUSED` result, use the established AI-OS companion recovery path. Do not restart `agy-proxy`; it is a different service.
5. **Format Output**: Format `./tmp/planner_output.txt` into `implementation_plan.md`.

---

**Vision Provider & Image Attachment Protocol**: Perplexity file upload quota is 50/week. If remaining upload quota is > 25 AND a screenshot contains complex visual elements that cannot be easily/accurately transcribed into text, passing the image file to Perplexity is permitted. If quota is <= 25 or the visual content is easily describable, the main orchestrator MUST act as the vision provider and describe it textually via `--image-desc` instead of uploading.

**FALLBACK POLICY**: Fall back to `agy` ONLY if Perplexity quota is 0, or if the user specifically requests it. Never use Gemini 3.1 Pro for any reason; use `Gemini 3.7 Flash (High)` if falling back.
