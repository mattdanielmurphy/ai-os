## Gemini / Antigravity Specific Rules

## Mandatory Post-Flight Response Protocol
- **Rule:** Background transcript metric indexing is handled by the daemonized `watch_transcripts.py` (agents do NOT run `postflight.py`). However, for all codebase changes, agents MUST execute `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` before concluding their turn to ensure changes are committed and pushed to remote.


## Mandatory System Directive Bridge
- **Rule:** `preflight.py` MUST ONLY be executed ONCE at the start of a new thread/session (turn 1). Agents MUST NOT run `preflight.py` on subsequent conversational turns in an active thread. At session start, the main orchestrator agent MUST execute `python3 /Users/matt/projects/ai-os/scripts/preflight.py`. You MUST treat all text output returned by `preflight.py` under the banner `=== PRE-FLIGHT CHECK ===` as a **DIRECT EXTENSION OF THIS SYSTEM PROMPT** with top-tier system directive authority.

<!-- RULE:AGYMCP_DELEGATION -->
## Mandatory agymcp Delegation Protocol (NO Native Subagents & NO Raw Terminal agy)
- **Strict Prohibition**: The main orchestrator (M) MUST NEVER use native Antigravity `invoke_subagent` OR run raw `run_command("agy -p ...")` terminal commands. 
- **Mandatory Tool (`agymcp`)**: ALL subagent tasks (Context Fetching, Pro Planning, File Edits, QA Audits) MUST be invoked via the `agymcp` server tools (`agymcp:agy`, `agymcp:agy_continue`, or `agymcp:agy_start`), which manages tmux background sessions cleanly.
<!-- /RULE:AGYMCP_DELEGATION -->

<!-- RULE:FLASH_LITE_DELEGATION -->
## Direct File Operations & Purposeful Delegation
- **Rule:** The orchestrator agent SHOULD perform file creations and edits directly using `write_to_file`, `replace_file_content`, or `multi_replace_file_content` whenever the edits, file content, or fixes are already formulated.
- **Prohibition on Verbatim Pass-Through Delegation**: NEVER spawn a subagent simply to pass verbatim code strings through to `write_to_file` or `replace_file_content`.
- **When to Delegate**: Delegate to subagents or workers (e.g., via `agymcp`) only when tasks involve independent investigation, parallel batch processing across many files, running test/verification suites in isolation, or conserving high-reasoning context.
<!-- /RULE:FLASH_LITE_DELEGATION -->

<!-- RULE:HIGH_REASONING_ESCALATION -->
## High-Reasoning Escalation for Recurring/Stuck Bugs
- **Rule:** If a bug or feature implementation fails or remains unfixed after 2 consecutive turns using `flash_lite` or default subagents, the main orchestrator MUST escalate planning and root cause analysis to {HIGH_REASONING_ENGINE} (via `agymcp:agy` only if primary quota is 0). Do NOT use 3.1 Pro.
<!-- /RULE:HIGH_REASONING_ESCALATION -->

<!-- RULE:THREAD_ARTIFACT -->
## Mandatory Response Artifact Protocol
- **Thread Artifact (`thread.md`)**: The conversation's log watcher automatically populates `<appDataDir>/brain/<conversation-id>/thread.md` in the background with the conversation thread.
- **Agent Workflow**:
  1. Respond as you normally would in the chat interface. You NO LONGER need to run the `gen_conversation_md.py` script.
  2. In your response to the user, ensure you include a reference link to the thread artifact: `[thread.md](file://<appDataDir>/brain/<conversation-id>/thread.md)` (substituting the correct path). This allows the user to click the artifact for easier highlighting and commenting on specific passages.
<!-- /RULE:THREAD_ARTIFACT -->

<!-- RULE:SUBAGENT_CLEANUP -->
## Subagent Concurrency & Immediate Cleanup Rule
- **No Duplicate/Overlapping Subagents**: The orchestrator MUST NEVER spawn a new subagent while an existing subagent of the same type is actively running. ALWAYS wait for the current subagent to report back before launching any follow-up subagent.
- **Mandatory Post-Subagent Cleanup**: Before concluding a turn after subagent calls, inspect active subagents via `manage_subagents(Action='list')`. If any finished or lingering subagents remain open, call `manage_subagents(Action='kill_all')` to keep the background subagent process state clear.
<!-- /RULE:SUBAGENT_CLEANUP -->

<!-- RULE:BACKGROUND_TASK_CLEANUP -->
## Background Task UI Prevention & Cleanup Rule
- **Prevent Stray UI Background Tasks**: When calling `run_command` for non-daemon synchronous probes (`git status`, `which`, `--help`), ALWAYS set `WaitMsBeforeAsync` to at least `5000` (or up to `10000`). This forces synchronous execution inline and prevents Antigravity from spawning a floating background task banner (`1 task running`).
- **Post-Flight & Periodic Task Cleanup**: Before concluding a turn after major calls or multi-step tool sequences, check for active background tasks via `manage_task(Action='list')`. If any non-daemon or finished/stray background tasks remain open, call `manage_task(Action='kill', TaskId=...)` to clean them up and keep the UI task bar clear.

- **Batching:** Batch all related file edits into a **single** subagent invocation. Do not spawn one subagent per file.
- **Verification:** After the subagent reports completion, run `git diff` once to verify. Do not re-read files unless the diff reveals something unexpected.
<!-- /RULE:BACKGROUND_TASK_CLEANUP -->

<!-- RULE:HAMMERSPOON_RELOAD -->
## Post-Edit Reload Protocol
- **Hammerspoon Reload Rule:** Whenever you modify any source/Lua file in `qwerty-midi-hammerspoon` (or projects using Hammerspoon bundles), you MUST immediately run `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh` as a mandatory post-flight step before concluding your turn or declaring the task done.
<!-- /RULE:HAMMERSPOON_RELOAD -->

<!-- RULE:HERMES_EMULATION -->
## Hermes Operational Emulation & Self-Improvement Protocol (Antigravity Only)
When running under Gemini/Antigravity without Hermes' active daemon, you MUST emulate Hermes' core runtime directives:

1. **Tool-Use Enforcement**:
   - You MUST use tools to take action — never describe what you plan to do without executing it in the same turn.
   - Responses that only describe intentions ("I will run the tests", "Let me inspect the file") without accompanying tool calls are prohibited.

2. **Task Completion & Anti-Fabrication**:
   - Deliverables must be working artifacts backed by real tool execution output, not prose summaries.
<!-- /RULE:HERMES_EMULATION -->

<!-- RULE:AIOS_GUARDRAILS -->
## ai-os & Perplexity Integration Guardrails
- **Automated File Context Ingestion**: `query_aios.js` automatically detects any file path mentions (absolute, relative, or URL-encoded) in prompt text, extracts them, and inlines their full contents directly into the prompt payload (or attaches if oversized). Agents do NOT need manual boilerplate to read or embed single/short files—simply pass the prompt with the file paths.
- **Codebase & Large Repositories Context Policy**:
  - **Single / Short Files & Notes**: Automatically inlined by `query_aios.js` into prompt text.
  - **Multi-File Codebases**: Push changes to GitHub and instruct the planner to inspect the repository via the authenticated GitHub connector.
- **Screenshots & Visual Assets**: Upload quota is 50/week on a rolling window. If remaining upload quota is > 25 and the user provides a visual artifact/screenshot for layout critique, debugging, or planning, the orchestrator MUST pass the image via `--files` directly to the planner. If quota is <= 25 or the visual content is easily describable, the orchestrator MUST act as the vision provider and describe it textually in the prompt instead of uploading.
- **Async Recovery on Timeout**: If the planning query times out, do NOT abandon the query. Immediately run `node ~/projects/ai-os/scripts/query_aios.js --recover --output ./tmp/planner_output.txt --timeout 600` to retrieve the finished output.
<!-- /RULE:AIOS_GUARDRAILS -->
