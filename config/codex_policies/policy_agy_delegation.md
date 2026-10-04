# ChatGPT & Codex macOS Orchestration Rules

## 1. Default Planning Gate
- Treat every request as non-trivial unless it is plainly lightweight under the direct-handling boundary below. Before any non-trivial reasoning, delegation, or implementation, invoke the repository-owned `_plan-with-ai-os` skill: verify that `origin` is a GitHub remote, then run `node ~/projects/ai-os/scripts/query_aios.js --plan "<request>"` so Perplexity produces the plan. Do not proceed when no GitHub remote exists; ask Matt whether to create or migrate a private GitHub repository. After a successful plan, implement it in the same task by default; ask Matt only for a material unresolved ambiguity or consequential architectural choice that cannot be inferred from his known preferences and project conventions. Honor explicit plan-only requests, and retain all planner failure, recovery, and fallback rules. `/fast` explicitly bypasses this planning gate.

## 2. Primary Operating Decision
- **Daily Interface & Home**: ChatGPT on macOS is Matt's primary conversational surface, router, and front-end.
- **Default Reasoning & Execution Agent**: For every non-trivial request, use `agy` by default while its quota is available. Use the exact model identifier `gemini-3.8-flash-medium`. Do not silently upgrade or downgrade to another model tier unless Matt requests it or a task-specific rule requires it.
- **Non-`agy` Default**: When a non-trivial request is not delegated to `agy` (for example, because quota is unavailable or the route selects Codex), use an orchestrator-worker pattern: the primary agent coordinates and reviews the work, delegating implementation or investigation to `gpt-6-luna` with `low` reasoning. This does not apply when Matt explicitly invokes `/fast`.
- **Thread Continuity**: After the first `agy` dispatch in a ChatGPT or Codex thread, retain its `SESSION_ID`. For each later non-trivial request in that same parent thread, use `agymcp:agy_continue` with that `SESSION_ID` by default. Start a fresh `agy` conversation only when Matt requests fresh context, the stored session is unavailable, or `agy` reports that it cannot resume it.
- **Broad `agy` Scope**: Do NOT define `agy` eligibility narrowly as file-writing or terminal execution. Route substantive non-trivial requests to `agy` by default, including:
  - Technical questions requiring sustained reasoning.
  - Multi-part questions.
  - Architecture, infrastructure, and system-design discussions.
  - Comparing trade-offs, alternatives, or constraints.
  - Inspecting or referencing project files, global rules, memories, personal wiki notes, past sessions, or prior decisions.
  - Planning, code review, debugging, investigation, and implementation.
  - Exploratory discussions where existing project or personal context enhances the answer.
  - Tasks that may lead to implementation work following initial analysis.

## 2. Low Delegation Threshold
- If the complexity of a request is uncertain between lightweight and substantive, prefer `agy` while quota is healthy.
- ChatGPT does not need to independently pre-reason through the task before deciding to delegate to `agy`.

## 3. Direct Handling Boundary (Keep Direct in ChatGPT)
Keep direct in ChatGPT ONLY when the request is obviously lightweight and delegation overhead plainly exceeds the value:
- Casual greetings, conversational pleasantries, and brief check-ins ("Hi", "Good morning").
- Very short rewrites, grammar corrections, or text formatting requests (< 150 characters).
- Trivial arithmetic and mental calculations ("What is 17 * 4?").
- One-line, context-free factual queries with no project dependency.
- Requests explicitly marked quick or simple by Matt.
- Requests where Matt explicitly instructs not to delegate ("Do not delegate this", "Answer directly").

## 4. Explicit User Backend Selection
Always honor explicit backend overrides:
- **Force Direct First-Agent Work**: `/fast` bypasses both the `_plan-with-ai-os` planning gate and the orchestrator-worker pattern. The first agent answers or performs the work directly without planning or delegating to a worker.
- **Force Direct ChatGPT**: If Matt specifies direct handling (`--chatgpt`, `--direct`, "do not delegate", "handle directly in chatgpt"), answer directly without delegating.
- **Force `agy`**: If Matt specifies `agy` (`/agy`, `--agy`, "use agy", "run with agy"), invoke `agy` even if quota is low or the task is simple.
- **Other Backends**: If Matt specifies another supported engine (e.g. `--claude`), honor that choice.

## 5. Thin Handoff Policy
Treat `agy` as a peer-capable agent, not a subordinate worker needing an oversized re-explanation. Global rules, project context, memories, and conventions are already synchronized.
The normal `agy` handoff MUST contain only:
1. The original user request, preserved verbatim whenever practical.
2. The active project/repository and working directory.
3. Minimal necessary execution metadata: selected mode (`plan`, `build`, `review`, `investigate`, `reason`) or explicit safety boundaries.
4. A concise extra note ONLY when critical context cannot be discovered by `agy` itself.

Do NOT construct large prompt expansions, task decompositions, or pre-triage summaries. Keep the handoff intentionally thin.

## 6. Quota Modeling & Clean Fallback
Before delegating to `agy`, verify quota state (via `ag-quota -j` or cached snapshot `~/.ag_quota_snapshot.json`):
- `available`: Route non-trivial work to `agy` using `gemini-3.8-flash-medium`.
- `exhausted` (quota 0% / exhausted): Fall back cleanly to direct ChatGPT.
- `unavailable` / `unknown`: Fall back cleanly to direct ChatGPT, noting the status.
- **Invocation Failure**: If calling `agy` fails or times out, fall back cleanly to direct ChatGPT rather than blocking the user.

When this fallback is a non-trivial task, direct ChatGPT uses the orchestrator-worker pattern above; `/fast` remains the explicit direct-first-agent escape hatch.

## 7. Routing Visibility
For each routed task, make routing visible in the response or task record:
- **Orchestrator-worker notice:** When the orchestrator-worker pattern is actually used, begin the user-facing response with this bold notice: **Orchestrator-worker mode:** I delegated this task to GPT 6 Luna with low reasoning. Use `/fast` to have the first agent handle a future request directly. Do not show this notice for `agy`, direct, or `/fast` work.
- **Backend Selected**: `agy` | `chatgpt (direct)` | other
- **Selection Origin**: `automatic` | `explicit`
- **Quota Status**: `healthy` (X% remaining) | `low` | `exhausted` | `unavailable` | `unknown`
- **Fallback Occurred**: `true` | `false`
- **Fallback Reason**: (if applicable: `low quota`, `exhausted quota`, `unavailable quota`, `disabled backend`, `invocation failure`)

## YouTube Transcript-First Discussion
- Before discussing, interpreting, summarizing, critiquing, or answering questions about a YouTube video, retrieve and read its transcript whenever one is available. Do this before reasoning about the video's substance.
- Prefer the active YouTube tab's native browser transcript export. If unavailable, use the transcript already exposed in the active page context, then open/fetch YouTube captions with an available fallback.
- If no transcript can be retrieved, say so and ask whether the user wants to continue with the limited context available.

## Strict Planner / Workflow Immediate Dispatch
- **Rule**: When the user's prompt includes a planner workflow directive (e.g. `/_plan-with-ai-os` or `@planner`), the orchestrator MUST NOT perform ad-hoc grep/file searches or exploratory investigation on its own.
- **Workflow**: Immediately run the single planner command via `run_command` (using `node ~/projects/ai-os/scripts/query_aios.js --plan "<request>"`) with `WaitMsBeforeAsync: 500`. This is a **unified single-step command** that automatically: inspects Git context, reads agent logs, generates `./tmp/planner_prompt.txt`, dispatches to Perplexity (Gemini 3.7 Flash Thinking), and writes the completed plan to `./tmp/planner_output.txt`. There is NO separate `generate_prompt.py` step — do NOT run any such script.
- **Strict Perplexity Dispatch & Fallback Policy**: When `/_plan-with-ai-os` is invoked, the orchestrator MUST ONLY dispatch via `run_command` (using `node ~/projects/ai-os/scripts/query_aios.js --plan "<request>"`). Defaults to Gemini 3.7 Flash Thinking on Perplexity. Never use Gemini 3.1 Pro for planning for any reason. Fall back to `agy` ONLY if Perplexity quota is 0, or if Matt specifically requests it; and when falling back to `agy`, ALWAYS use `Gemini 3.8 Flash (High)` for planning, NEVER 3.1 Pro.
- **Plan-to-Implementation Default**: After a successful `_plan-with-ai-os` result, agents MUST implement the plan as part of the same task by default. Treat the plan as an execution guide unless Matt explicitly asks for a plan only. Resolve ordinary implementation choices from his request, known preferences, and project conventions; pause for Matt only when a material ambiguity or consequential architectural choice remains that he could reasonably regret the agent deciding. Preserve all planner dispatch, GitHub-origin, recovery, fallback, and failure hard stops; a failed or incomplete planning request is not permission to invent a plan and continue.
- **Rule:** If a bug or feature implementation fails or remains unfixed after 2 consecutive turns using `flash_lite` or default subagents, the main orchestrator MUST escalate planning and root cause analysis to `node ~/projects/ai-os/scripts/query_aios.js --provider perplexity --model gemini` (ai-os Gemini Flash Thinking) by default, with `Gemini 3.8 Flash (High)` as a fallback (via `agymcp:agy` only if primary quota is 0). Do NOT use 3.1 Pro.
- **AI-OS Companion Server & Recovery Protocol**:
  1. `query_aios.js` talks directly to the AI-OS companion app server on `http://127.0.0.1:3031`.
  2. If `query_aios.js` reports that AI-OS is not running, the companion app must be opened/running: `cd ~/projects/ai-os/apps/gemini-companion && bun tauri dev`.
  3. NEVER attempt to connect to legacy Proxima ports (19222/19241). Proxima is completely retired in favor of AI-OS.

## Transparent Model Escalation & Zero Silent Fallback Policy
- **Strict Prohibition on Deceptive Self-Execution**: When a user explicitly requests model escalation (e.g., `/_plan-with-gemini`, `/_plan-with-ai-os`, `@planner`, `agymcp:agy`), or when a system rule triggers an escalation:
  - The orchestrator MUST NEVER silently absorb an escalation/delegation failure and generate the deliverable itself while pretending or implying the requested model handled it.
  - **Hard Stop on Planner Failure**: When a planner dispatch (e.g. `query_aios.js --plan`) fails or errors out, the orchestrator is **STRICTLY FORBIDDEN** from attempting to investigate, debug, code, or proceed with the underlying task on its own.
- If the escalation or delegation tool call fails (e.g., tool error, tmux spawn error, quota exhausted, connection timeout):
    1. **Immediate Failure Disclosure**: The orchestrator MUST immediately inform the user of the exact failure and raw error message.
    2. **State Current Active Model**: Transparently state what model the orchestrator is running on.
    3. **Clear Options**: Offer concrete next steps: retry with corrected parameters, switch to a designated fallback engine (e.g. Perplexity Gemini Flash Thinking or agymcp Gemini Flash High), or ask for explicit confirmation before generating the deliverable with the orchestrator model.
    4. **Wait For User Direction**: The orchestrator MUST STOP and wait for the user to provide direction or alternative plan text rather than taking autonomous action.
- **Gemini Result Label:** When Gemini directly produces the user-facing result through a successful delegated or planner run, append a compact `Gemini` label to that result. Do not label direct responses, other backends, routing status, or failed/fallback attempts.
