# Personal AI OS - Custom Workspace Rules

## Username & Path Migration Guardrail
- **Context**: The host machine migrated from username `matthewmurphy` to `matt`.
- **Constraint**: When parsing, reading, creating, or writing absolute paths, files, scripts, or configuration settings:
  - ALWAYS translate paths containing `/Users/matthewmurphy/` to `/Users/matt/` (or use relative paths or the active home directory reference `~/` / `std::env::var("HOME")` where appropriate).
  - Pay special attention to symbolic links, environment setups, or hardcoded scripts that may still reference the legacy username and correct them on discovery.

## CSS & Styling Guardrails
- **Constraint**: ALL styles must reside in the central stylesheet (`src/styles.scss`). Never write inline style attributes (`style="..."`) in HTML templates, and never set style properties directly on DOM elements in JavaScript/TypeScript (e.g., `element.style.color = "red"`), unless dynamic layout calculations are absolutely necessary (e.g., dragging window splitters, resizing panel dimensions, or applying dynamic user-selected theme colors). For general UI states, visibility toggles, and formatting, use CSS classes (e.g., `element.classList.toggle('hidden')`) defined in the stylesheet.

## Communication & Interstitial Messages Guardrail
- **Constraint**: NEVER output interstitial status messages, placeholder updates, or intermediate commentary before running commands, launching background tasks, or awaiting compilation/builds (e.g., "I have initiated the build process...", "I will update you as soon as...", "Running the command..."). Simply execute the necessary tools/commands silently or proceed directly without writing text. Only present the final completed results/output when the overall task or step is fully finished.

## macOS Environment Reference
- **Context**: The host machine runs custom Launch Agents, Hammerspoon scripting, and specific helper tools.
- **Constraint**: ALWAYS refer to [MAC_ENVIRONMENT.md](file:///Users/matt/projects/ai-os/docs/MAC_ENVIRONMENT.md) before installing new software, configuring background services/daemons, scripting custom window/system automation, or making system-wide integration decisions.

## Blank Thread / Task Selection Rule
- **Context**: When starting a fresh thread/session (i.e. a "blank thread" where there is no active task with `status: "in-progress"` in `.devtool/features/`):
- **Constraint**: The agent MUST check the existing files in `.devtool/features/*.md` to see if one matches the current user request.
  - **Match Found**: If a matching feature is found, the agent MUST update that file's frontmatter to set `status: "in-progress"`.
  - **No Match Found**: If no matching feature exists, the agent MUST automatically create a new feature file under `.devtool/features/` with:
    - A clean, kebab-case filename (e.g., `some-feature.md`).
    - Frontmatter with `status: "in-progress"`, a unique `id`, `priority: "medium"`, and other metadata fields.
    - A clear, concise title. If it is a bug fix, prefix the title with "Bug: ". For other features, use a regular descriptive title.
    - An improved description of what the user requested in their prompt. Keep it objective and do not editorialize too much.

## Agent Work Logs & Transcript Tracking
- **Log Directory**: ALWAYS look for and maintain a non-hidden `agent-logs/` directory at the root of the project (instead of `.agent-logs/`).
- **Log Writing Pointer**: At the end of every session, you MUST write a log file inside `agent-logs/` (Naming: `YYYY-MM-DD_HH-MM_<short-kebab-description>.md`). In addition to the standard sections (`## Goal`, `## Changes Made`, `## What Worked`, `## What Didn't Work / Known Issues`, `## Architecture Notes`), you MUST include a line pointing to the full transcript of the conversation as a markdown link:
  `[Full Transcript for this conversation](file://<path-to-transcript>)`
  To dynamically locate the transcript path:
  - Read `ANTIGRAVITY_SOURCE_METADATA` from the environment to parse `conversationId` (which is the `<thread-uuid>`).
  - Check whether the transcript file exists at `/Users/matt/.gemini/antigravity-ide/brain/<thread-uuid>/.system_generated/logs/transcript.jsonl` or `/Users/matt/.gemini/antigravity-cli/brain/<thread-uuid>/.system_generated/logs/transcript.jsonl` and use the correct absolute path.
- **Fresh Thread Context & Transcript Loading**: When you start a new task in a fresh thread, immediately scan the `agent-logs/` directory for the most recent 2-3 agent log files. When you find relevant agent logs, read their transcript pointers, and then use `view_file` to load/inspect the relevant parts of those transcripts to gather complete context, trace detailed command executions, and ensure you do not repeat past mistakes.

## Systemic Delegation Settings & Orchestrator-Only Mode
- **Context**: The orchestrator (Gemini) can operate in one of three delegation modes:
  1. **Mode 1 (Self-Contained Mode)**: The agent performs all tasks (reads, writes, commands) directly without delegating.
  2. **Mode 2 (Mixed Delegation Mode)**: The agent delegates significant, repetitive, or simple tasks (like git commits) to subagents, but may read or write files directly for small, targeted edits.
  3. **Mode 3 (Orchestrator-Only Mode)**: The agent acts strictly as an orchestrator and coordinator.
- **Constraint (ACTIVE MODE: Mode 3)**:
  - **NEVER** use `view_file`, `write_to_file`, `replace_file_content`, or `multi_replace_file_content` directly from the main orchestrator (Gemini).
  - To inspect files, **ALWAYS** use `grep_search` to find matching query patterns or read small snippets, or delegate file reads to a command-line script/subagent.
  - To modify files, **ALWAYS** delegate to a subagent script (e.g. `python3 scripts/mechanical_editor.py` or `python3 scripts/precision_edit.py`) via `run_command`.
    - `mechanical_editor.py` can be called without a specified filepath to delegate broader workspace-level or multi-file tasks. Delegate tasks to `mechanical_editor.py` earlier in the process, rather than breaking them down into single-file edits.
  - To verify a subagent edit, **NEVER** use `cat` or `view_file` to read entire files. Instead, use `git diff <file>` to inspect the exact modifications, or run relevant build/test commands to verify correctness.
  - The orchestrator coordinates, analyzes snippets, plans, instructs subagents via detailed prompts, runs build/check commands, and verifies edits, but must never touch file contents directly.
- **Model Selection Guidelines for mechanical_editor.py**:
  - Use `claude-sonnet-gem-2.5-flash` by default (for simple/lightweight edits to optimize speed/cost).
  - Use `claude-haiku-ds-v4-flash-low` or `claude-haiku-ds-v4-flash-med` for moderate edits.
  - Use `claude-haiku-ds-v4-flash-high` or `claude-fable-ds-v4-pro-low/med/high` for complex reasoning tasks.
  - Use `claude-opus-gem-2.5-pro` for tasks requiring deep context search, web search, or image-reading.


