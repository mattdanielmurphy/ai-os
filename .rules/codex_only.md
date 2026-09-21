# ChatGPT & Codex macOS Orchestration Rules

## 1. Primary Operating Decision
- **Daily Interface & Home**: ChatGPT on macOS is Matt's primary conversational surface, router, and front-end.
- **Default Reasoning & Execution Agent**: Antigravity (`agy`) is the default capable reasoning and execution backend whenever usable Antigravity quota is available.
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
- `healthy` (quota >= 20%): Route non-trivial work to `agy` by default.
- `low` (quota < 20%): Preserve quota for higher-value tasks; fall back to direct ChatGPT by default unless forced.
- `exhausted` (quota 0% / exhausted): Fall back cleanly to direct ChatGPT.
- `unavailable` / `unknown`: Fall back cleanly to direct ChatGPT, noting the status.
- **Invocation Failure**: If calling `agy` fails or times out, fall back cleanly to direct ChatGPT rather than blocking the user.

## 7. Routing Visibility
For each routed task, make routing visible in the response or task record:
- **Backend Selected**: `agy` | `chatgpt (direct)` | other
- **Selection Origin**: `automatic` | `explicit`
- **Quota Status**: `healthy` (X% remaining) | `low` | `exhausted` | `unavailable` | `unknown`
- **Fallback Occurred**: `true` | `false`
- **Fallback Reason**: (if applicable: `low quota`, `exhausted quota`, `unavailable quota`, `disabled backend`, `invocation failure`)

## 8. Thread Context Visibility (Trial)
- **Threshold Footer:** Once the active ChatGPT/Codex thread has reached or exceeded 100,000 context tokens, append a compact footer to every final response: `> Thread context: <size>`.
- **Truthful Measurement:** Use an exact token count only when the runtime exposes an authoritative meter. Otherwise, state `> Thread context: 100k+ (exact count unavailable)`; never invent a precise total.
- **Scope:** Do not show a context footer below the threshold. This trial is informational only: continue the requested work normally and do not create or switch threads automatically. If the context becomes materially constraining, explicitly recommend a new task in the normal response.
