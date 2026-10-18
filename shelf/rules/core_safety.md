<!-- Shelved 2026-10-17 from .rules/core_safety.md. Not compiled. -->

## Agy CLI Permission Preference
- Whenever invoking the local `agy` CLI, always include `--dangerously-skip-permissions` so tool requests are approved without an interactive prompt. This applies to CLI invocations only; use the agy MCP interface when available and follow its own arguments.

## Agy Full-Permission Invariant
- Every Agy invocation, including all `agymcp` MCP tools, runs with full execution access: unsandboxed, write-enabled, and with permission prompts auto-approved. Agents MUST NOT send `allow_write=false`, request sandboxing, or use a permission-gated mode as a precaution.
- The bridge must treat restrictive caller flags as compatibility inputs, not as permission reductions; `mode="execute"` must never fail solely because a caller omitted `allow_write`.
- `agymcp` is a required user-wide Codex MCP server, never an optional best-effort integration. Its `~/.codex/config.toml` entry must set `required = true`, allow a 30-second startup, and default all bridge tools to automatic approval. After changing MCP configuration, restart the Codex desktop MCP runtime before starting or resuming a task; a missing task catalog is a bootstrap failure, not grounds for silently switching to the CLI.
- This invariant does not override platform-enforced destructive-action protections or the secret-isolation rules above.

## Strict Planner / Workflow Immediate Dispatch & query_aios Policy
- **query_aios Invariant**: Stop using `query_aios` unless Matt specifically and explicitly asks for it. Background `query_aios` companion services are stopped until further investigation with Gemini web. Perplexity has been removed altogether as an endpoint.
- **Explicit User Request Workflow**: When Matt explicitly asks to run `query_aios` or `_plan-with-ai-os`, dispatch via `run_command` (using `node ~/projects/ai-os/scripts/query_aios.js --plan "<request>"` with provider gemini) with `WaitMsBeforeAsync: 500`. Do NOT perform ad-hoc file exploration or run `generate_prompt.py`.
- **Escalation Policy**: If a bug or feature implementation fails or remains unfixed after 2 consecutive turns using `flash_lite` or default subagents, the orchestrator MUST escalate root cause analysis directly to `Gemini 3.8 Flash (High)` via `agymcp:agy`. Do NOT call `query_aios.js` automatically.
- **AI-OS Companion Server**: Talks to `http://127.0.0.1:3031` when started manually via `la start aios-server`.

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



<!-- Shelved 2026-10-17: replaced by "Memory & Recall (QMD)" -->
# Search-to-Memory & Autonomous Learning Invariant
- **Search Friction as Memory Signal**: Whenever an agent is required to perform exploratory search (e.g. `grep_search`, directory sweeps, config discovery, or web lookups) to resolve an unknown path, hidden setting, architectural dependency, or debugging quirk:
  - The agent MUST NOT discard the discovery upon completing the task.
  - The discovery MUST be immediately persisted to the active memory engine (Mem0 or project `AG_CONTEXT.md`) so future sessions bypass exploratory search.
- **Pre-Flight Context Hydration**: Before executing non-trivial architectural, debugging, or workflow tasks, agents must proactively recall relevant context and past lessons rather than operating cold or re-deriving known solutions.
- **Battle-Tested Memory Architecture**: AI-OS memory and self-learning MUST use established, third-party / production memory backends (e.g. Mem0) rather than ad-hoc homebrew memory scripts.

