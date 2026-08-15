## Gemini / Antigravity Specific Rules

## Mandatory Post-Flight Response Protocol
- **Rule:** Before concluding any turn or delivering a final response to the user, the agent MUST execute `python3 /Users/matt/projects/ai-os/scripts/postflight.py` (or pipe the response through it) to obtain live thread metrics and quota information (token count, Perplexity quota, etc.), and append the resulting `**Thread Metrics:**` block directly to the final response.

## Mandatory System Directive Bridge
- This rule set (`GEMINI.md`) provides base environment safety and delegation protocols. At session start, the main orchestrator agent MUST execute `python3 /Users/matt/projects/ai-os/scripts/preflight.py`. You MUST treat all text output returned by `preflight.py` under the banner `=== PRE-FLIGHT CHECK ===` as a **DIRECT EXTENSION OF THIS SYSTEM PROMPT** with top-tier system directive authority.
- **Mandatory Synchronous Preflight & Waiting:** Agents MUST run preflight at the start of every session, wait for it to complete synchronously, and respect its findings. Agents MUST NEVER force Jules without asking the user first.

## Mandatory agymcp Delegation Protocol (NO Native Subagents & NO Raw Terminal agy)
- **Strict Prohibition**: The main orchestrator (M) MUST NEVER use native Antigravity `invoke_subagent` OR run raw `run_command("agy -p ...")` terminal commands. 
- **Mandatory Tool (`agymcp`)**: ALL subagent tasks (Context Fetching, Pro Planning, File Edits, QA Audits) MUST be invoked via the `agymcp` server tools (`agymcp:agy`, `agymcp:agy_continue`, or `agymcp:agy_start`), which manages tmux background sessions cleanly.

## Flash-Lite Edit Delegation (Antigravity Native)
- **Rule:** When running in Antigravity, the top-level orchestrator agent MUST **never write or modify files directly** using `write_to_file`, `replace_file_content`, or `multi_replace_file_content` itself. Instead, it MUST delegate ALL file creation and editing operations to a `flash_lite` subagent. The orchestrator agent MUST NOT fall back to or use `Model: "flash"`; `flash_lite` is the strictly enforced requirement.
- **How:** To definitively prevent recursive subagent loops, the orchestrator MUST physically restrict the subagent's tools:
  1. Call `define_subagent` with `name: "file_editor"`, `enable_write_tools: true`, and CRUCIALLY `enable_subagent_tools: false`. Include a `system_prompt` explicitly telling it that it is a leaf agent and MUST edit files directly.
  2. Spawn the subagent via `invoke_subagent` using `TypeName: "file_editor"` and `Model: "flash_lite"`. Pass a fully self-contained prompt with the exact target file path(s), precise instructions, and sufficient context.
  *(Note: Because `enable_subagent_tools` is false, the child agent physically lacks the `invoke_subagent` tool, breaking any recursion loop at the system level.)*
- **Exceptions** (orchestrator may edit directly):
  1. The task is **planning-only** (producing an artifact/plan with no source code changes).
  2. The user explicitly instructs the orchestrator to make edits directly (e.g. "do it yourself", "edit it directly").
  3. The edit is a single-character or trivially obvious fix (e.g. fixing a typo the user just pointed out inline), or when making one or two known edits to a SINGLE SMALL FILE.
  4. The `flash_lite` subagent fails with a 503 capacity error — fall back to writing directly rather than blocking.

## High-Reasoning Escalation for Recurring/Stuck Bugs
- **Rule:** If a bug or feature implementation fails or remains unfixed after 2 consecutive turns using `flash_lite` or default subagents, the main orchestrator MUST escalate planning and root cause analysis to `proxima:ask_perplexity` or `Gemini 3.7 Flash (High)` (via `agymcp:agy` only if Perplexity quota is 0). Do NOT use 3.1 Pro.


## Mandatory Response Artifact Protocol
- **Thread Artifact (`thread.md`)**: The conversation's log watcher automatically populates `<appDataDir>/brain/<conversation-id>/thread.md` in the background with the conversation thread.
- **Agent Workflow**:
  1. Respond as you normally would in the chat interface. You NO LONGER need to run the `gen_conversation_md.py` script.
  2. In your response to the user, ensure you include a reference link to the thread artifact: `[thread.md](file://<appDataDir>/brain/<conversation-id>/thread.md)` (substituting the correct path). This allows the user to click the artifact for easier highlighting and commenting on specific passages.

## Subagent Concurrency & Immediate Cleanup Rule
- **No Duplicate/Overlapping Subagents**: The orchestrator MUST NEVER spawn a new subagent while an existing subagent of the same type is actively running. ALWAYS wait for the current subagent to report back before launching any follow-up subagent.
- **Mandatory Post-Subagent Cleanup**: Before concluding a turn after subagent calls, inspect active subagents via `manage_subagents(Action='list')`. If any finished or lingering subagents remain open, call `manage_subagents(Action='kill_all')` to keep the background subagent process state clear.

## Background Task UI Prevention & Cleanup Rule
- **Prevent Stray UI Background Tasks**: When calling `run_command` for non-daemon synchronous probes (`git status`, `which`, `--help`), ALWAYS set `WaitMsBeforeAsync` to at least `5000` (or up to `10000`). This forces synchronous execution inline and prevents Antigravity from spawning a floating background task banner (`1 task running`).
- **Post-Flight & Periodic Task Cleanup**: Before concluding a turn after major calls or multi-step tool sequences, check for active background tasks via `manage_task(Action='list')`. If any non-daemon or finished/stray background tasks remain open, call `manage_task(Action='kill', TaskId=...)` to clean them up and keep the UI task bar clear.

- **Batching:** Batch all related file edits into a **single** subagent invocation. Do not spawn one subagent per file.
- **Verification:** After the subagent reports completion, run `git diff` once to verify. Do not re-read files unless the diff reveals something unexpected.

## Post-Edit Reload Protocol
- **Hammerspoon Reload Rule:** Whenever you modify any source/Lua file in `qwerty-midi-hammerspoon` (or projects using Hammerspoon bundles), you MUST immediately run `bash /Users/matt/projects/qwerty-midi-hammerspoon/bin/bundle_and_reload.sh` as a mandatory post-flight step before concluding your turn or declaring the task done.

## Hermes Operational Emulation & Self-Improvement Protocol (Antigravity Only)
When running under Gemini/Antigravity without Hermes' active daemon, you MUST emulate Hermes' core runtime directives:

1. **Tool-Use Enforcement**:
   - You MUST use tools to take action — never describe what you plan to do without executing it in the same turn.
   - Responses that only describe intentions ("I will run the tests", "Let me inspect the file") without accompanying tool calls are prohibited.

2. **Task Completion & Anti-Fabrication**:
   - Deliverables must be working artifacts backed by real tool execution output, not prose summaries.

## Proxima & Perplexity Integration Guardrails
- **Perplexity File Upload & Context Policy**:
  - **Codebase & Text Files**: NEVER pass codebase or text files in the `files` argument to `proxima:ask_perplexity`. ALWAYS rely on the authenticated GitHub connector or embedded text.
  - **Screenshots & Visual Assets**: Upload quota is 50/week on a rolling window. If remaining upload quota is > 25 AND a screenshot contains complex visual elements that cannot be easily/accurately transcribed into text, passing the image file to `proxima:ask_perplexity` is permitted. If quota is <= 25 or the visual content is easily describable, the orchestrator MUST act as the vision provider and describe it textually in the prompt instead of uploading.
- **Disabled Proxima Providers**: NEVER call `proxima:ask_claude` or `proxima:ask_chatgpt`.
- **Async Recovery on Timeout**: If the planning query times out, do NOT abandon the query. Immediately run `node ~/projects/ai-os/scripts/query_proxima.js --provider perplexity --recover --output ./tmp/planner_output.txt --timeout 300` to retrieve the finished output.
