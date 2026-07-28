## Gemini / Antigravity Specific Rules

## Flash-Lite Edit Delegation (Antigravity Native)
- **Rule:** When running in Antigravity, the top-level orchestrator agent MUST **never write or modify files directly** using `write_to_file`, `replace_file_content`, or `multi_replace_file_content` itself. Instead, it MUST delegate ALL file creation and editing operations to a `flash_lite` subagent via `invoke_subagent` with `Model: "flash_lite"`.
- **How:** Spawn the subagent with a fully self-contained prompt that includes the exact target file path(s), precise instructions for what to write/change, and sufficient context so it needs no clarifying questions. The subagent inherits the workspace and has full write tool access. Include the directive `[LEAF AGENT: DO NOT RE-DELEGATE]` in the subagent prompt so the child knows it is a leaf agent.
- **Exceptions** (orchestrator may edit directly):
  1. The task is **planning-only** (producing an artifact/plan with no source code changes).
  2. The user explicitly instructs the orchestrator to make edits directly (e.g. "do it yourself", "edit it directly").
  3. The edit is a single-character or trivially obvious fix (e.g. fixing a typo the user just pointed out inline).
  4. The agent is a subagent spawned via invoke_subagent (i.e. running as a leaf agent). Subagents MUST perform file edits directly using write_to_file / replace_file_content and MUST NEVER call invoke_subagent recursively.
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
