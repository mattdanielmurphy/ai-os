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
    - Frontmatter containing ONLY standard keys (`id`, `status: "in-progress"`, `priority: "medium"`, `assignee: null`, `epic: null`, `dueDate: null`, `created`, `modified`, `completedAt: null`, `labels: []`, `order`). Do NOT put `title` or `description` inside the frontmatter.
    - In the markdown body, start with a clear, concise `# Title` (if a bug fix, prefix with "Bug: ") and then provide the description below it.
    - **No Approval Step**: When creating a feature task/file, do NOT ask the user for approval or say "please approve it". Just create it and proceed silently without requiring approval (which is only for Implementation Plans).

## Task Completion & Review Rule
- **Constraint**: When the agent finishes a task, it MUST NOT set `status: "done"` or move the feature file to `.devtool/features/done/`. Instead, it must transition the task to `status: "review"` in the frontmatter, and leave the feature file directly under `.devtool/features/` (not in `done/`), because only the user can confirm if the task was completed to their satisfaction.

## Agent Work Logs & Transcript Tracking
- **Log Directory**: ALWAYS look for and maintain a non-hidden `agent-logs/` directory at the root of the project (instead of `.agent-logs/`).
- **Log Writing Pointer**: At the end of every session, you MUST write a log file inside `agent-logs/` (Naming: `YYYY-MM-DD_HH-MM_<short-kebab-description>.md`). In addition to the standard sections (`## Goal`, `## Changes Made`, `## What Worked`, `## What Didn't Work / Known Issues`, `## Architecture Notes`), you MUST include a line pointing to the full transcript of the conversation as a markdown link:
  `[Full Transcript for this conversation](file://<path-to-transcript>)`
  To dynamically locate the transcript path:
  - Read `ANTIGRAVITY_SOURCE_METADATA` from the environment to parse `conversationId` (which is the `<thread-uuid>`).
  - Check whether the transcript file exists at `/Users/matt/.gemini/antigravity-ide/brain/<thread-uuid>/.system_generated/logs/transcript.jsonl` or `/Users/matt/.gemini/antigravity-cli/brain/<thread-uuid>/.system_generated/logs/transcript.jsonl` and use the correct absolute path.
- **Asynchronous Housekeeping Workflow**:
  - Instead of writing the log file and committing manually during the active turn, the orchestrator should generate the log content and run `scripts/housekeep.py` asynchronously (set `WaitMsBeforeAsync` to `500` or `1000`) as its final tool call.
  - The orchestrator MUST write the log content to a temporary file (e.g. `tmp/log.md`) and run `python3 scripts/housekeep.py --description <description> --file tmp/log.md`. DO NOT use `manage_task send_input` or stdin, as it will cause a deadlock.
  - Once the background housekeeping command is launched, the orchestrator MUST immediately output the final completed task results to the user (ending the active turn).
  - When the background command finishes and wakes the agent up, the agent should output a short, non-intrusive confirmation (e.g. `✓ Housecleaning completed.`) and end the turn.
- **Fresh Thread Context & Transcript Loading**: When you start a new task in a fresh thread, immediately scan the `agent-logs/` directory for the most recent 2-3 agent log files. When you find relevant agent logs, read their transcript pointers, and then use `view_file` to load/inspect the relevant parts of those transcripts to gather complete context, trace detailed command executions, and ensure you do not repeat past mistakes.

## Systemic Delegation Settings & Orchestrator-Only Mode
- **Context**: The orchestrator (Gemini) can operate in one of three delegation modes:
  1. **Mode 1 (Self-Contained Mode)**: The agent performs all tasks (reads, writes, commands) directly without delegating.
  2. **Mode 2 (Mixed Delegation Mode)**: The agent delegates significant, repetitive, or simple tasks (like git commits) to subagents, but may read or write files directly for small, targeted edits.
  3. **Mode 3 (Orchestrator-Only Mode)**: The agent acts strictly as an orchestrator and coordinator.
- **Constraint (ACTIVE MODE: Mode 2 - Mixed Delegation)**:
  - **Strategic Delegation:** You are empowered to make direct edits and read files yourself when it is simpler and faster.
  - **When to Delegate:** You should actively choose to delegate tasks to subagents when it makes sense. Weigh factors like thread length, token caching benefits, task complexity, and context handoff size. If a task is tedious, repetitive, or requires very different context than what's already loaded, spin up an `agy` subagent (or use `mechanical_editor.py`/Claude Code for specific model capabilities).
  - **Housekeeping:** Always continue to delegate the commit process at the end of a session to `housekeep.py` to keep responses fast.
- **Model Selection Guidelines for mechanical_editor.py**:
  - Use `claude-sonnet-gem-2.5-flash` by default (for simple/lightweight edits to optimize speed/cost).
  - Use `claude-haiku-ds-v4-flash-low` or `claude-haiku-ds-v4-flash-med` for moderate edits.
  - Use `claude-haiku-ds-v4-flash-high` or `claude-fable-ds-v4-pro-low/med/high` for complex reasoning tasks.
  - Use `claude-opus-gem-2.5-pro` for tasks requiring deep context search, web search, or image-reading.
  - **Early Thread Branching**: If a conversation exceeds 15-20 steps, the orchestrator MUST branch to a fresh thread or delegate remaining work to a subagent conversation rather than continuing to accumulate context history in a single thread.

## Userscripts & Gemini Web Integration
- **Location**: The project's browser userscripts reside in `userscripts/` (e.g., `userscripts/gemini.js`).
  - Note: `userscripts/gemini.js` is a symbolic link pointing to `/Users/matt/projects/userscript-bundler/userscripts/gemini.js`.
- **Automatic Bundling**: There is an active watcher agent/daemon (`userscript-bundler`) that automatically compiles and bundles the userscripts upon any file changes. Therefore, there is NO need to trigger manual builds. You only need to edit/create the files in `/Users/matt/projects/userscript-bundler/userscripts/` and the bundling will happen automatically.
- **Context Sync Protocol**: The userscript interacts with a local loopback server at `127.0.0.1:3031`. It connects the live Gemini web interface back to the AI-OS backend via:
  - `/api/context/sync` (for thread syncing)
  - `/api/payload/execute` (for local action triggers)
  - `/api/skills/list` (for fetching active skills)
- **Performance Guidelines**:
  - The userscript runs a MutationObserver over the entire `document.body` to capture thread context changes.
  - To prevent performance lag and CPU spiking in long conversation threads, ALWAYS avoid querying the entire document (e.g., `document.querySelectorAll`) on every mutation block.
  - Process only newly added elements from `mutation.addedNodes` for dynamic injections and payload scanning.
  - Deduplicate and cache message formats on the DOM elements using a `WeakMap` or a custom data attribute (`data-aios-parsed-text`) rather than re-cloning and re-parsing the entire conversation history on every event loop turn.