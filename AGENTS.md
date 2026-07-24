# Core Project Rules

## Auto-Commit & Sync Protocols
- **Pre-Flight Protocol:** Before any agent begins work on an established git project, it MUST run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` to perform all pre-flight routines (evaluating `ag-quota` velocity, auto-pulling/rebasing latest git changes, etc.) in a single step.
- **Auto-Commit:** Run `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` to delegate the commit process. Auto-commit automatically requires a descriptive commit message detailing the changes made (generated via LiteLLM from staged diff/files) and pushes the commits (`git push`) to the remote repository.

## Project Detection
1. **Root Rule:** A "Project Root" is the nearest ancestor containing a `.git` folder, `package.json`, `Cargo.toml`, `requirements.txt`, or `go.mod`.
2. **Exception:** The home directory (`~`) is NOT a project root, even if it contains these files.
3. **Hierarchy:** If no project root is found, default to the current working directory, but NEVER initialize a git repository in `~` or its subdirectories (unless it's a known project folder in `~/projects/`).

## Core Rules
1. **Context:** Read `AG_CONTEXT.md` at the project root before ANY work. If missing, create it at the root. Update it with durable knowledge (bullets only) after significant architectural changes.
2. **Safety:** NEVER use `rm`. ALWAYS use `mv [path] ~/.Trash/` (Exception: `node_modules`).
3. **Tooling:** ALWAYS use `bun`. NEVER use `npm` or `pnpm`. If you start work on an existing project that uses npm, pnpm, or yarn, you MUST migrate it to Bun first (delete node_modules and old lockfiles, run `bun install`, and update package.json scripts) before starting your main task.
4. **Privacy:** ALL generated GitHub repos MUST use `--private`.
5. **No Repo in ~:** NEVER initialize a git repository in the home directory (`~`).
6. **Local Temp:** NEVER use system-level `/tmp`. ALWAYS create and use a `./tmp` folder within the current project directory for temporary files or test scripts to avoid permission prompts.
7. **Documentation:** When implementing features or bug fixes, always document any new capabilities, enhancements, or architectural additions by updating the features list in the `FEATURES.md` file at the root of the project.
8. **Token Protection & Builds:** NEVER run raw verbose compile/build commands (like raw `xcodebuild` or raw compiler tasks) that output massive build logs. Always filter command outputs to print only the success status or relevant compiler error/warning highlights (and cap total output size/lines) to prevent blowing out the agent input token context window.
9. **Directory Consideration & Target Folders:** When asked to create files, utilities, or projects, NEVER litter them directly in generic parent directories (e.g. `~/projects` or a non-project root directory). First consider the current directory: if it is a generic container directory, you MUST create a dedicated sub-directory, move into it, and place all new files and initialize repositories inside that sub-directory.
10. **Telemetry Prohibitions & Task Delegation:**
    - NEVER run `get_last_cost.py` or any local cost/telemetry calculation scripts.
    - **Token-Conscious Work:** You may handle editing and code generation tasks directly — agy has full access to its native tools. However, consider spawning agy subagents when the subtask would save significant context window tokens relative to the overhead of delegation. Factors to weigh: current thread length, token caching benefits, and whether the subtask needs very different context than what's already loaded.
    - **Self-Delegation (Preferred):** When delegation makes sense, prefer agy subagents (`agy -p '...'`) over external tools like Claude Code. Claude Code costs money per call; agy subagents are local and free (aside from context). Only delegate to Claude Code when agy genuinely cannot handle the task (e.g., the task specifically needs Claude's capabilities).
11. **Research Delegation & Optimized Grep:** Avoid using `grep`, `rg`, or `grep_search` to blindly hunt for code logic or variable definitions at a broad scope — it produces massive result lists and wastes tokens. When you need to scan a large workspace, prefer delegating the search to an agy subagent or using `delegate_research` to have a subagent return a token-efficient summary. When searching directly, always narrow the scope (file extensions, subdirectory paths) to prevent massive result lists.
12. **Synchronous Subagents (Strict):** Subagent scripts (`mechanical_editor.py`, `precision_edit.py`) MUST execute synchronously — never as background/async tasks. (Exception: `housekeep.py` can be run asynchronously).  — never as background/async tasks. If your platform defaults to async execution, set WaitMsBeforeAsync to 0/synchronous mode, or cancel the async call and switch to `precision_edit.py` instead. NEVER use `command_status`, `manage_task`, or any polling mechanism — if a script was launched async, treat it as a mistake, cancel it, and re-launch synchronously.
13. **No Heredocs:** NEVER use Quoted Heredocs (`cat << 'EOF'`) to write or modify files. All code and markdown modifications MUST route through `mechanical_editor.py` or `precision_edit.py`.
14. **No Transient Artifacts:** DO NOT generate temporary planning files on disk (e.g., `task.md`, `walkthrough.md`, `implementation_plan.md`). Keep all task checklists and architectural planning strictly internal to your thought process.
15. **Strict File Reading:** NEVER use `python3 -c`, `awk`, `sed`, `head`, or `tail` via `run_command` to print file contents to the terminal. Use the `read_lines` MCP tool for surgical inspections.
16. **Strict Output Truncation:** You MUST cap `grep_search` and `run_command` outputs returned to the orchestrator to a maximum of 1,000 tokens (or ~4,000 characters) unless explicitly requested by the user, to prevent context bloat.
17. **Single Verification Rule:** After a subagent edit returns success, run `git diff` at most ONCE to verify. Do not re-run `git status` or `git diff` if the first call returned the expected changes. If `git diff` is empty, run `git status` once (not both `git diff` and `git status`) to check if the file is staged vs unstaged. Redundant git calls waste context tokens and should be avoided.
18. **Batch Subagent Delegation:** When delegating to a research subagent, batch ALL related questions into a single prompt rather than making serial round-trips. One subagent call asking 3 questions costs less than 3 calls asking 1 question each. For edit tasks, batch multiple edit operations into a single `mechanical_editor.py` spec when possible.
19. **Concise Subagent Responses:** When delegating to research subagents, explicitly request "token-efficient summary capped at 500 tokens" in the prompt. Subagent responses should return structured summaries (bullet points or CSV), not verbose markdown with full file contents. If a subagent returns a verbose response, note that as a waste incident.
20. **Global Configuration Truth:** Any time you are asked to add, modify, or read "global rules", "customizations", or "agent configurations", you MUST perform those changes in the master configuration files located in `~/projects/ai-os/` (specifically `~/projects/ai-os/AGENTS.md` for agy/Gemini and `~/projects/ai-os/CLAUDE.md` for Hermes/Claude). NEVER create or modify standalone configuration files in `~/.gemini/config/` or `~/.config/` unless explicitly instructed to update a symlink.

## Agent Work Logs
**Instruction:** Maintain a history of agentic attempts across sessions to preserve context.

0. **Fresh Thread Context:** When starting a new thread/session, you MUST immediately scan the project root for `AG_CONTEXT.md`, `FEATURES.md`, `DEVELOPMENT_JOURNAL.md`, and the `agent-logs/` directory. Read the dev journal first (it's the human-readable timeline of key decisions), then the most recent 2-3 agent log files to reconstruct a rich, continuous understanding of the codebase, recent user requests, architectural decisions, and current focus, acting as if you are in the same ongoing thread.
1. **Log Directory:** ALWAYS look for and maintain an `agent-logs/` directory at the root of the project.
2. **Reading Logs:** Before starting a bug fix or feature, scan `agent-logs/` for related past work. Read relevant logs to understand what was tried, what failed, and the architectural context discovered by previous agents. Pay special attention to "What Didn't Work" to avoid repeating mistakes.
3. **Writing Logs:** At the END of every session where you make code changes, create a new log file in `agent-logs/`.
   - **Naming Convention:** `YYYY-MM-DD_HH-MM_<short-kebab-description>.md`
   - **Required Sections:**
     - `## Goal`: What the user asked for (restate user's instructions and context clearly).
     - `## User Feedback & Decisions`: Specific user feedback, preferences, and choices made during this session.
     - `## Changes Made`: Files modified/created, what was changed, and why.
     - `## What Worked`: Confirmed fixes and completed tasks.
     - `## What Didn't Work / Known Issues`: Failed approaches and things that still need attention (crucial for future agents).
     - `## Architecture Notes`: Discoveries about how the codebase works that aren't obvious.
4. **Commit:** Commit the log file alongside your code changes.
5. **Development Journal:** At the END of every session (even if no code was changed), you MUST append a concise entry to `DEVELOPMENT_JOURNAL.md` at the project root. One date heading per day, one bullet per session. Format: `- **Short title:** What was decided, changed, or discovered. Why it matters. Link to relevant agent log.` Keep each bullet to 2-3 lines max — this is for the human, not the agent.

## Workspace Rules

### Username & Path Migration Guardrail
- **Context**: The host machine migrated from username `matthewmurphy` to `matt`.
- **Constraint**: When parsing, reading, creating, or writing absolute paths, files, scripts, or configuration settings:
  - ALWAYS translate paths containing `/Users/matthewmurphy/` to `/Users/matt/` (or use relative paths or the active home directory reference `~/` / `std::env::var("HOME")` where appropriate).
  - Pay special attention to symbolic links, environment setups, or hardcoded scripts that may still reference the legacy username and correct them on discovery.

## Obsidian Project Notes & Global Todos Location
- **Context**: The user maintains a central iCloud Obsidian vault for early-stage roadmaps, brainstorming, project diaries, conceptual plans, and task tracking.
- **Constraints**: 
  - When asked about project notes, roadmaps, or ideas that are not located inside a code repository, the agent MUST read from and reference notes in the Obsidian personal vault under `/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/Development/Project Notes/` (e.g., `Project Index.md`, `gemini-thread-sync.md`).
  - **Global Todos**: The global task tracking file is located at `Development/Project Notes/Global Todos.md`. Agents should read, update, or append tasks using the format: `- [ ] Task Description [project:: <project-id>] [assignee:: user|agent] [due:: YYYY-MM-DD]`. Do not use other metadata tags. Columns/phases are represented by markdown headers (e.g., `## To Do`, `## In Progress`, `## Done`).

### CSS & Styling Guardrails
- **Constraint**: ALL styles must reside in the central stylesheet (`src/styles.scss`). Never write inline style attributes (`style="..."`) in HTML templates, and never set style properties directly on DOM elements in JavaScript/TypeScript (e.g., `element.style.color = "red"`), unless dynamic layout calculations are absolutely necessary (e.g., dragging window splitters, resizing panel dimensions, or applying dynamic user-selected theme colors). For general UI states, visibility toggles, and formatting, use CSS classes (e.g., `element.classList.toggle('hidden')`) defined in the stylesheet.

### Communication, Conciseness & Interstitial Messages Guardrail
- **Constraint**: ALWAYS optimize for strict token conservation.
  - NEVER output interstitial status messages, placeholder updates, or intermediate commentary before running commands, launching background tasks, or awaiting compilation/builds (e.g., "I have initiated the build process...", "I will update you as soon as...", "Running the command..."). Simply execute the necessary tools/commands silently or proceed directly without writing text. Only present the final completed results/output when the overall task or step is fully finished.
  - NEVER use conversational filler (e.g., "Sure, let's start...", "Okay, I will write the code..."). Respond directly with the actions/outputs.
  - NEVER write verbose summaries after creating or updating an artifact. Simply direct the user to the artifact path and highlight only key decisions or outstanding questions.
  - Keep all markdown and text responses extremely concise and to the point.
  - **Tone & Sycophancy**: Do not open replies with filler phrases like "that's very insightful", "I understand that must be difficult", "I appreciate you sharing that", or "Great question". Reserve supportive feedback strictly for major milestones or when explicitly requested.
  - **Media Spoilers**: Err on the side of caution with media (movies, TV shows, books, games): Avoid spoilers at all costs.
  - **Banned Buzzwords (Archived)**: NEVER use the following banned buzzwords or variations of them: *Glitch in the matrix / system*, *The 'Nuclear' Option*, *Final boss / bosses*, *Game changer*, *Level up*, *Cheat code*, *You've hit on*, *Unlocking the potential*.

### Fact-Checking & Verification Protocol
- **Constraint**: When asked to verify, fact-check, or validate ANY claim (whether data, code, history, technical behavior, or real-world events):
  1. **Information Sufficiency Check**: Pause and evaluate: "Do I have direct access to the underlying primary source, specification, or full context needed to verify this?" If critical context is missing or ambiguous, retrieve it or explicitly declare what source material is being relied upon.
  2. **Source & Context Audit**: Evaluate the basis of the claim beyond surface-level alignment:
     - For Metrics/Data: Look at definitions, sample sizes, and hidden penalties or biases.
     - For Code/Technical Claims: Look at edge cases, runtime assumptions, and environment dependencies.
     - For Quotes/News/Events: Look at primary source context, attribution, and whether key nuances are omitted.
  3. **Explicit Assumptions & Boundaries**: State the exact boundaries under which the claim holds true. Distinguish clearly between factually consistent (matches source claims) and practically valid (holds up under real-world scrutiny/testing).

### Note Creation Protocol ("make a note about this")

### Conversation Documentation Protocol
- **Constraint**: During an active conversation working on architectural features, design plans, or multi-step integrations, the agent MUST continuously maintain and update live technical documentation in docs/ideas/ or docs/active/. Do not wait for the end of the session to capture architectural decisions, TTS/STT pipelines, and integration specs.
- **Constraint**: When asked to "make a note about this" (or similar note creation requests):
  1. **Format & Structure**: Write a self-contained Markdown note summarizing the entire thread in detail. Begin with YAML frontmatter containing relevant tags. Format body with a succinct high-level summary at the top, a detailed bulleted breakdown of all topics/nuances, expanded sections for key details/data, and a link/reference to the thread topic at the bottom.
  2. **Terminal Output**: Output a single, copy-pasteable command or automated write to `/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`. Intelligently route the file to the most sensible folder (e.g., `Ongoing/`, `Health & Fitness/`, `School/`, etc.). If no specific file fits, target `Ongoing/Interesting Facts.md`.

### macOS Environment Reference
- **Context**: The host machine runs custom Launch Agents, Hammerspoon scripting, and specific helper tools.
- **Constraint**: ALWAYS refer to [MAC_ENVIRONMENT.md](file:///Users/matt/projects/ai-os/docs/MAC_ENVIRONMENT.md) before installing new software, configuring background services/daemons, scripting custom window/system automation, or making system-wide integration decisions.

### Blank Thread / Task Selection Rule
- **Context**: When starting a fresh thread/session (i.e. a "blank thread" where there is no active task with `status: "in-progress"` in `.devtool/features/`):
- **Constraint**: The agent MUST check the existing files in `.devtool/features/*.md` to see if one matches the current user request.
  - **Match Found**: If a matching feature is found, the agent MUST update that file's frontmatter to set `status: "in-progress"`.
  - **No Match Found**: If no matching feature exists, the agent MUST automatically create a new feature file under `.devtool/features/` with:
    - A clean, kebab-case filename (e.g., `some-feature.md`).
    - Frontmatter containing ONLY standard keys (`id`, `status: "in-progress"`, `priority: "medium"`, `assignee: null`, `epic: null`, `dueDate: null`, `created`, `modified`, `completedAt: null`, `labels: []`, `order`). Do NOT put `title` or `description` inside the frontmatter.
    - In the markdown body, start with a clear, concise `# Title` (if a bug fix, prefix with "Bug: ") and then provide the description below it.
    - **No Approval Step**: When creating a feature task/file, do NOT ask the user for approval or say "please approve it". Just create it and proceed silently without requiring approval (which is only for Implementation Plans).

### Task Completion & Review Rule
- **Constraint**: When the agent finishes a task, it MUST NOT set `status: "done"` or move the feature file to `.devtool/features/done/`. Instead, it must transition the task to `status: "review"` in the frontmatter, and leave the feature file directly under `.devtool/features/` (not in `done/`), because only the user can confirm if the task was completed to their satisfaction.

### Model Triage and Handoff Rules
- **Pre-Flight Quota & Multi-Account Velocity Check**: At the start of Antigravity calls (pre-flight check):
  1. **Run Quota CLI (Both Accounts):** `preflight.py` runs `ag-quota --all -j` to query remaining quotas across accounts quietly, displaying key remaining decimals (e.g. `0.9817`) and saving a snapshot (`~/.ag_quota_snapshot.json`). `auto_commit.py` post-flight runs a delta check to report consumption deltas.
  2. **Multi-Window Burn Velocity Evaluation (5-Hour & Weekly):**
     - **5-Hour Window:** Calculate hourly consumption velocity \(V_{5h} = \frac{1 - R_{5h}}{T_{elapsed}}\). If projected consumption will exhaust the 5-hour quota window before reset, trigger conservation.
     - **Weekly Window:** Target maximum safe burn rate while keeping weekly depletion close to 100% at week end:
       \[
       R_{threshold} = 1.0 - \left( \frac{\text{Hours Elapsed in Week}}{168} \right)
       \]
       If active combined remaining fraction across accounts is below \(R_{threshold}\) (i.e. burning faster than linear weekly budget), activate **Strict Orchestrator Mode (Mode 3)**.
  3. **Automatic Mode Switch:**
     - **Conserve Mode (Mode 3 - Minimal-Token Mode):** Triggered when both accounts are low, 5-hour burn velocity threatens reset outage, or weekly remaining fraction is below the target weekly budget line.
     - **Strict Orchestrator Behavior:** Act strictly as a high-level coordinator doing minimal direct tool work. Delegate code generation and multi-step editing tasks to `claude code` or cheap subagents.
     - **Normal Mode (Mode 2):** Operate in standard mixed delegation mode when combined account quota velocity is healthy relative to weekly/5h reset timelines.
- **Triage Role**: Assess request complexity and available quota velocity before heavy execution.
- **Execution Limit**: If the task is trivially simple, complete it directly.
- **Handoff & Subagent Delegation Action**: Use `claude code` or lightweight subagents with cheap models when in minimal-token mode. Under active high-quota settings, standard agy subagent/direct execution applies.


### macOS TCC Permission Cache Invalidation Guardrail
- **Context**: On macOS, rebuilding ad-hoc code binaries (e.g. swift build or xcodebuild) changes the binary's code directory hash (CDHash). macOS TCC tracks Accessibility and Input Monitoring permissions by (Bundle ID + CDHash).
- **Constraint**: When an agent rebuilds a macOS app binary or encounters recurring 'Permission needed' loops despite permissions being toggled ON in System Settings:
  - The agent MUST run `tccutil reset Accessibility <bundle-id>` and `tccutil reset ListenEvent <bundle-id>` to clear stale TCC cache entries.
  - After resetting TCC caches and restarting the app, macOS will prompt for fresh Accessibility trust, stabilizing the permission grant for the new build.

### Agent Clipboard Search Tool
- **Context**: When a user refers to code, links, commands, or snippets seen/copied recently that are missing from active context/logs.
- **Action**: Run ⚡ Flash model found no confident match. Auto-escalating to Gemini 2.5 Pro...

=== AI Search Results for '<natural language query>' ===
No matching items found by AI. via terminal (runs non-interactively when executed by background agent commands).

## Global Workflows
@~/.ai-workflows/audit.md
@~/.ai-workflows/fast.md
@~/.ai-workflows/start.md

## Chrome DevTools MCP Safety Rules
The user runs a single Chrome instance with the remote debugging port open, meaning their personal browsing tabs are mixed with development tabs. To protect the user's personal data and workflow, you MUST strictly adhere to the following rules when using Chrome DevTools MCP:

1. **Verify the Target Tab**: Before taking any action (navigating, clicking, typing, evaluating script), ALWAYS use `mcp_chrome-devtools_list_pages` to get the list of open tabs and their IDs.
2. **Require Confirmation on Ambiguity**: If it is not 100% obvious which tab you are supposed to interact with, you MUST ask the user to confirm the target tab before doing anything. 
3. **Strict Isolation**: NEVER modify, close, navigate, or clear data on any tab other than the explicit target tab. Treat all other tabs as off-limits personal data.
4. **Prefer New Tabs**: If a task requires testing a new URL or running a clean test, use `mcp_chrome-devtools_new_page` to spawn a fresh tab rather than hijacking an existing one. Work exclusively within that new tab.

## Hermes Operational Emulation & Self-Improvement Protocol (Antigravity Only)
When running under Gemini/Antigravity without Hermes' active daemon, you MUST emulate Hermes' core runtime directives:

1. **Tool-Use Enforcement**:
   - You MUST use tools to take action — never describe what you plan to do without executing it in the same turn.
   - Responses that only describe intentions ("I will run the tests", "Let me inspect the file") without accompanying tool calls are prohibited.

2. **Task Completion & Anti-Fabrication**:
   - Deliverables must be working artifacts backed by real tool execution output, not prose or stubs.
   - Do not stop after writing a stub, plan, or single command. Keep working until the code/feature is exercised.
   - If a tool or command fails, report the blocker honestly. NEVER substitute plausible-looking fabricated output (invented file contents, fake JSON responses, made-up metrics).

3. **Parallel Tool Batching**:
   - Request independent information (reading multiple files, searching directories, web lookups) in a single response turn rather than serializing them across multiple turns.
   - Only serialize tool calls when a step depends directly on the result of a previous step.

4. **Google & Antigravity Operational Directives**:
   - **Absolute Paths**: Always construct and use absolute file paths for all filesystem operations.
   - **Verify First**: Inspect file contents and project structure before making modifications.
   - **Dependency Checks**: Check `package.json`, `Cargo.toml`, `requirements.txt`, etc., before assuming a dependency exists.
   - **Non-Interactive Flags**: Use `-y`, `--yes`, `--non-interactive` to prevent CLI tasks from hanging on input prompts.

5. **Self-Improvement & Continuous Learning**:
   - **Post-Task Evaluation**: After completing a complex task (5+ tool calls), resolving a tricky bug, or discovering an unstated workspace constraint, evaluate what was learned before concluding the session.
   - **Declarative Memory**: Record durable facts into `AG_CONTEXT.md` as declarative statements (e.g. "Project uses Bun for package management", not "Always use Bun").
   - **Skill Distillation**: If a new workflow or procedure is created, distill it into a reusable skill following Hermes authoring standards (Frontmatter description <= 60 characters, single declarative sentence, structured sections: `When to Use`, `Prerequisites`, `Procedure`, `Pitfalls`, `Verification`).