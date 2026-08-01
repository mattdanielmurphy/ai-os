## Gemini / Antigravity Specific Rules

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
  3. The edit is a single-character or trivially obvious fix (e.g. fixing a typo the user just pointed out inline).
  4. The `flash_lite` subagent fails with a 503 capacity error — fall back to writing directly rather than blocking.

## Mandatory Response Artifact Protocol
- **Single Conversation Response Artifact with Folded Turn History**: Every turn response MUST update the single persistent artifact at `<appDataDir>/brain/<conversation-id>/conversation_response.md`.
- **Structure** (strict chronological order — oldest at top, current at bottom):
  ```
  <details><summary><strong>&nbsp;↻&nbsp; VIEW THREAD HISTORY</strong></summary>
  <hr>
  [exchange tables — oldest first]
  <br><hr><br>
  </details>
  <hr>
  <br>
  [current turn exchange table — always visible]
  ```
  Keep a maximum of **15** history exchanges; drop the oldest when exceeded.
- **Agent Workflow (SCRIPTED — do NOT manually manage HTML):**
  1. Generate your response by passing your plain markdown text (no HTML tables) via standard input to the python script:
     ```bash
     cat << 'EOF' | python3 /Users/matt/projects/ai-os/scripts/gen_conversation_md.py <conv-id> --title "Thread Title" --save-turn
     # [Agent response title]
     [Agent response body...]
     EOF
     ```
  2. The script auto-reads the transcript for user messages, writes your turn_N.md, and generates the full HTML-table `conversation_response.md`.
  3. In chat: output ONLY the single-line link `[conversation_response.md](file://...)`.
- **Exchange Table Format** — each turn (user + agent) uses one table:
  ```html
  <table width="100%" border="0" frame="void" rules="none">
    <tr>
      <td width="1%" align="right">
        <br>
  <h3><strong>🧔 You</strong></h3>
  [H:MMam/pm]
    <small>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</small>
    <br>
    <br>
  </td>
      <td width="99%" colspan="3">
        <br>
        <h4>[Full user prompt text — no truncation unless extremely long]</h4>
        <br>
        <br>
      </td>
    </tr>
    <tr>
      <td width="99%" colspan="3">
      <br>

  # <strong>[Agent response title]</strong>
  [Agent response body — full markdown, # and ## headings, lists, code, etc.]

  <br>
  <br>
      </td>
      <td width="1%" align="left">
      <br>
      <br>
        <h3><strong>🤖 Agent</strong></h3>
  [H:MMam/pm]
        <small>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</small>
      </td>
    </tr>
  </table>
  ```
- **Thread Header**: Begin the file with `# <strong>Thread: [Descriptive Title]</strong>`
- **Steer messages**: Include ALL user messages from the conversation, including steers sent while the agent was working. Mark pure steers with `*(steer — [brief context])*` in the agent cell.
- **Artifact Metadata Parameters**: ALWAYS set `UserFacing: true` and `RequestFeedback: true` in `ArtifactMetadata`.
- **Pure Artifact Output**: The entire substantive content of the turn MUST live inside `conversation_response.md`. The chat response should contain ONLY a single line link/pointer to `[conversation_response.md](file://...)`. NO response text outside the artifact.
- **Token note**: Antigravity does NOT auto-inject the artifact into context on every turn. The agent reads it only when writing the next turn (bounded cost). Users highlighting/commenting injects only the excerpt — not the full file.

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
