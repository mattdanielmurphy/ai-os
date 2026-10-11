---
name: _plan-with-ai-os
description: "MANDATORY: Initiate high-reasoning planning via ai-os Perplexity before executing non-trivial tasks."
---

# Plan With AI-OS (Perplexity High Reasoning)

Run high-reasoning planning using the unified `query_aios.js` planner.

> ⚠️ **SINGLE-COMMAND WORKFLOW**: There is NO separate `generate_prompt.py` or prompt-generation step. Do NOT run any such script. `query_aios.js --plan` handles everything in one command.

---

## Workflow Steps

1. **Classify the task**: Decide whether the requested work changes, investigates, or depends on a software project, repository, or other version-controlled deliverable. Clearly local, self-contained tasks (for example, configuring or troubleshooting a desktop app, device, or personal account) are not project work just because the active directory is a repository. Apply the normal direct-handling boundary; if planning is useful for local work, the planner may run without a GitHub remote. If a task includes required project work, use the project path.
2. **Project pre-flight only**: For project work, verify that `origin` exists and targets GitHub (`https://github.com/...` or `git@github.com:...`). If it is missing or targets another host, STOP and ask the user whether to create or migrate a private GitHub repository before planning. Mixed tasks that include required project work retain this requirement.
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

6. **Implement by Default**: After a successful plan is available, continue the user's requested task by implementing the plan in the same task. Treat the plan as the execution guide, not as the final deliverable, unless the user explicitly asked for a plan only. Infer routine implementation choices from the request, Matt's known preferences, and established project conventions. Pause and ask Matt only when a material ambiguity or consequential architectural decision cannot be responsibly resolved from that context and choosing would risk an outcome he may regret. If a decision does require input, explain the specific choice and its consequences; continue any independent work that does not depend on the answer.

   This continuation rule applies only after a successful planner result. It does not bypass planner dispatch, recovery, fallback, or failure rules above. The GitHub-origin requirement applies to project work and mixed tasks that include required project work; clearly local tasks do not require a repository. A failed or incomplete planning request must follow those existing rules and must not be treated as permission to invent a plan and proceed.

---

**Vision Provider & Image Attachment Protocol**: Perplexity file upload quota is 50/week. If remaining upload quota is > 25 AND a screenshot contains complex visual elements that cannot be easily/accurately transcribed into text, passing the image file to Perplexity is permitted. If quota is <= 25 or the visual content is easily describable, the main orchestrator MUST act as the vision provider and describe it textually via `--image-desc` instead of uploading.

**FALLBACK POLICY**: Fall back to `agy` ONLY if Perplexity quota is 0, or if the user specifically requests it. Never use Gemini 3.1 Pro for any reason; use `Gemini 3.7 Flash (High)` if falling back.
