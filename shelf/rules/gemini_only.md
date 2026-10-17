<!-- Shelved 2026-10-17 from .rules/gemini_only.md. Not compiled. -->

## Mandatory agymcp Delegation Protocol (NO Native Subagents & NO Raw Terminal agy)
- **Strict Prohibition**: The main orchestrator (M) MUST NEVER use native Antigravity `invoke_subagent` OR run raw `run_command("agy -p ...")` terminal commands. 
- **Mandatory Tool (`agymcp`)**: ALL subagent tasks (Context Fetching, Pro Planning, File Edits, QA Audits) MUST be invoked via the `agymcp` server tools (`agymcp:agy`, `agymcp:agy_continue`, or `agymcp:agy_start`), which manages tmux background sessions cleanly.

## High-Reasoning Escalation for Recurring/Stuck Bugs
- **Rule:** If a bug or feature implementation fails or remains unfixed after 2 consecutive turns using `flash_lite` or default subagents, the main orchestrator MUST escalate planning and root cause analysis to {HIGH_REASONING_ENGINE}. Do NOT use 3.1 Pro.


## Hermes Operational Emulation & Self-Improvement Protocol (Antigravity Only)
When running under Gemini/Antigravity without Hermes' active daemon, you MUST emulate Hermes' core runtime directives:

1. **Tool-Use Enforcement**:
   - You MUST use tools to take action — never describe what you plan to do without executing it in the same turn.
   - Responses that only describe intentions ("I will run the tests", "Let me inspect the file") without accompanying tool calls are prohibited.

2. **Task Completion & Anti-Fabrication**:
   - Deliverables must be working artifacts backed by real tool execution output, not prose summaries.

## ai-os Integration Guardrails
- **query_aios Invariant**: Stop using `query_aios` unless Matt specifically and explicitly asks for it. Background query_aios services are stopped. Perplexity endpoint is removed.
- **Automated File Context Ingestion**: When `query_aios.js` is explicitly invoked, it automatically detects file path mentions in prompt text and inlines their contents directly into the prompt payload.
- **Async Recovery on Timeout**: If an explicit planning query times out, run `node ~/projects/ai-os/scripts/query_aios.js --recover --output ./tmp/planner_output.txt --timeout 600` to retrieve the finished output.
