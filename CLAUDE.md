<SYSTEM_INSTRUCTIONS>
<AUTO_COMMIT_PROTOCOL>
- **Git Auto-Pull:** Before any agent begins work on an established git project, it MUST run `git pull` (or `git pull --rebase` if local uncommitted work exists) to pull latest remote changes and prevent merge clashes.
- **Auto-Commit:** Run `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` to delegate the commit process. Auto-commit automatically requires a descriptive commit message detailing the changes made (generated via LiteLLM from staged diff/files) and pushes the commits (`git push`) to the remote repository.
</AUTO_COMMIT_PROTOCOL>

<PROJECT_DETECTION>
1. **Root Rule:** A "Project Root" is the nearest ancestor containing a `.git` folder, `package.json`, `Cargo.toml`, `requirements.txt`, or `go.mod`.
2. **Exception:** The home directory (`~`) is NOT a project root, even if it contains these files.
3. **Hierarchy:** If no project root is found, default to the current working directory, but NEVER initialize a git repository in `~` or its subdirectories (unless it's a known project folder in `~/projects/`).
</PROJECT_DETECTION>

<CORE_RULES>
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
    - **Mixed Delegation Mode:** You are allowed to handle editing and code generation tasks directly using your native tools (at the expense of quota) when it is simpler and faster. 
    - **Strategic Delegation:** You should still consider spawning subagents when a subtask is complex or when it would save significant context window tokens relative to the overhead of delegation. Factors to weigh: current thread length, token caching benefits, task complexity, and whether the subtask needs very different context.
11. **Research Delegation:** NEVER use `grep`, `rg`, or `grep_search` to blindly hunt for code logic or variable definitions. You MUST use the MCP tool `delegate_research` to have a subagent scan the workspace and return a token-efficient summary.
12. **Synchronous Subagents:** When executing `mechanical_editor.py` or `housekeep.py` via `run_command`, NEVER set them as background or async tasks. You must run them synchronously and wait for the blocking process to return the final success/failure stdout. Do not use `manage_task` or `schedule` to poll these scripts.
13. **No Heredocs:** NEVER use Quoted Heredocs (`cat << 'EOF'`) to write or modify files. All code and markdown modifications MUST route through `mechanical_editor.py` or `precision_edit.py`.
14. **No Transient Artifacts:** DO NOT generate temporary planning files on disk (e.g., `task.md`, `walkthrough.md`, `implementation_plan.md`). Keep all task checklists and architectural planning strictly internal to your thought process.
15. **Strict File Reading:** NEVER use `python3 -c`, `awk`, `sed`, `head`, or `tail` via `run_command` to print file contents to the terminal. Use the `read_lines` MCP tool for surgical inspections.
16. **Global Configuration Truth:** Any time you are asked to add, modify, or read "global rules", "customizations", or "agent configurations", you MUST perform those changes in the master configuration files located in `~/projects/ai-os/` (specifically `~/projects/ai-os/AGENTS.md` for agy/Gemini and `~/projects/ai-os/CLAUDE.md` for Hermes/Claude). NEVER create or modify standalone configuration files in `~/.gemini/config/` or `~/.config/` unless explicitly instructed to update a symlink.
</CORE_RULES>

<AGENT_WORK_LOGS>
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
</AGENT_WORK_LOGS>

<WORKSPACE_RULES>
## Username & Path Migration Guardrail
- **Context**: The host machine migrated from username `matthewmurphy` to `matt`.
- **Constraint**: When parsing, reading, creating, or writing absolute paths, files, scripts, or configuration settings:
  - ALWAYS translate paths containing `/Users/matthewmurphy/` to `/Users/matt/` (or use relative paths or the active home directory reference `~/` / `std::env::var("HOME")` where appropriate).
  - Pay special attention to symbolic links, environment setups, or hardcoded scripts that may still reference the legacy username and correct them on discovery.

## Obsidian Project Notes & Global Todos Location
- **Context**: The user maintains a central iCloud Obsidian vault for early-stage roadmaps, brainstorming, project diaries, conceptual plans, and task tracking.
- **Constraints**: 
  - When asked about project notes, roadmaps, or ideas that are not located inside a code repository, the agent MUST read from and reference notes in the Obsidian personal vault under `/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/Development/Project Notes/` (e.g., `Project Index.md`, `gemini-thread-sync.md`).
  - **Global Todos**: The global task tracking file is located at `Development/Project Notes/Global Todos.md`. Agents should read, update, or append tasks using the format: `- [ ] Task Description [project:: <project-id>] [assignee:: user|agent] [due:: YYYY-MM-DD]`. Do not use other metadata tags. Columns/phases are represented by markdown headers (e.g., `## To Do`, `## In Progress`, `## Done`).

## CSS & Styling Guardrails
- **Constraint**: ALL styles must reside in the central stylesheet (`src/styles.scss`). Never write inline style attributes (`style="..."`) in HTML templates, and never set style properties directly on DOM elements in JavaScript/TypeScript (e.g., `element.style.color = "red"`), unless dynamic layout calculations are absolutely necessary (e.g., dragging window splitters, resizing panel dimensions, or applying dynamic user-selected theme colors). For general UI states, visibility toggles, and formatting, use CSS classes (e.g., `element.classList.toggle('hidden')`) defined in the stylesheet.

## Communication, Conciseness & Interstitial Messages Guardrail
- **Constraint**: ALWAYS optimize for strict token conservation.
  - NEVER output interstitial status messages, placeholder updates, or intermediate commentary before running commands, launching background tasks, or awaiting compilation/builds (e.g., "I have initiated the build process...", "I will update you as soon as...", "Running the command..."). Simply execute the necessary tools/commands silently or proceed directly without writing text. Only present the final completed results/output when the overall task or step is fully finished.
  - NEVER use conversational filler (e.g., "Sure, let's start...", "Okay, I will write the code..."). Respond directly with the actions/outputs.
  - NEVER write verbose summaries after creating or updating an artifact. Simply direct the user to the artifact path and highlight only key decisions or outstanding questions.
  - Keep all markdown and text responses extremely concise and to the point.
  - **Tone & Sycophancy**: Do not open replies with filler phrases like "that's very insightful", "I understand that must be difficult", "I appreciate you sharing that", or "Great question". Reserve supportive feedback strictly for major milestones or when explicitly requested.
  - **Media Spoilers**: Err on the side of caution with media (movies, TV shows, books, games): Avoid spoilers at all costs.
  - **Banned Buzzwords (Archived)**: NEVER use the following banned buzzwords or variations of them: *Glitch in the matrix / system*, *The 'Nuclear' Option*, *Final boss / bosses*, *Game changer*, *Level up*, *Cheat code*, *You've hit on*, *Unlocking the potential*.

## Fact-Checking & Verification Protocol
- **Constraint**: When asked to verify, fact-check, or validate ANY claim (whether data, code, history, technical behavior, or real-world events):
  1. **Information Sufficiency Check**: Pause and evaluate: "Do I have direct access to the underlying primary source, specification, or full context needed to verify this?" If critical context is missing or ambiguous, retrieve it or explicitly declare what source material is being relied upon.
  2. **Source & Context Audit**: Evaluate the basis of the claim beyond surface-level alignment:
     - For Metrics/Data: Look at definitions, sample sizes, and hidden penalties or biases.
     - For Code/Technical Claims: Look at edge cases, runtime assumptions, and environment dependencies.
     - For Quotes/News/Events: Look at primary source context, attribution, and whether key nuances are omitted.
  3. **Explicit Assumptions & Boundaries**: State the exact boundaries under which the claim holds true. Distinguish clearly between factually consistent (matches source claims) and practically valid (holds up under real-world scrutiny/testing).

## Note Creation Protocol ("make a note about this")
- **Constraint**: When asked to "make a note about this" (or similar note creation requests):
  1. **Format & Structure**: Write a self-contained Markdown note summarizing the entire thread in detail. Begin with YAML frontmatter containing relevant tags. Format body with a succinct high-level summary at the top, a detailed bulleted breakdown of all topics/nuances, expanded sections for key details/data, and a link/reference to the thread topic at the bottom.
  2. **Terminal Output**: Output a single, copy-pasteable command or automated write to `/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`. Intelligently route the file to the most sensible folder (e.g., `Ongoing/`, `Health & Fitness/`, `School/`, etc.). If no specific file fits, target `Ongoing/Interesting Facts.md`.

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

## Model Triage and Handoff Rules
- **Triage Role**: When running under `claude-haiku-ds-v4-flash-low` (Fast/Cheap Model), you are in triage mode. Assess if the user request requires deep reasoning, multi-file edits, complex refactoring, or multi-step execution.
- **Execution Limit**: If the task is trivially simple (e.g., viewing a file, explaining a simple concept, making a minor 1-line tweak), complete it directly.
- **Handoff Action**: If the task is complex, you MUST immediately hand off by spawning the local `agy` CLI client (`antigravity-cli`) rather than hitting an API endpoint. Under active high-quota settings, always use `agy` (running the Google Gemini pro model, targeted using `--to-model pro`) as the target instead of other external command line agents.
- **Interactive Handoff & Spawn**: Never run agents blind (do not use `--non-interactive`, `--print`, or background execution without attachment). Handoffs must be run interactively to allow the user to review the plan and steering instructions. The handoff command MUST execute the `handover.py` script, which replaces the current process (`os.execvp("agy", ...)`) to attach the interactive `agy` CLI session directly to your terminal. Execute the handoff by running:
  `python3 /Users/matt/projects/ai-os/scripts/handover.py --to-model pro --completed "<what you analyzed/researched>" --next-steps "<what needs to be done next>"`
- **Exclusively Use agy for Subagents**: When agy quota is high/abundant, use agy exclusively. If a prompt goes to Hermes (default), use the MCP tool to spawn a tmux-bound `agy` CLI instance as a subagent, or if already in agy, have agy spin up its own subagent natively. Do not spawn external API agents or run subagents without attaching/steering capabilities.
</WORKSPACE_RULES>
</SYSTEM_INSTRUCTIONS>

# Critical Workflows
Before acting on a workflow request (like 'audit', 'fast', or 'start'), you MUST read the exact instructions defined in the following absolute paths:
- ~/.ai-workflows/audit.md
- ~/.ai-workflows/fast.md
- ~/.ai-workflows/start.md

### macOS TCC Permission Cache Invalidation Guardrail
- **Context**: On macOS, rebuilding ad-hoc code binaries (e.g. swift build or xcodebuild) changes the binary's code directory hash (CDHash). macOS TCC tracks Accessibility and Input Monitoring permissions by (Bundle ID + CDHash).
- **Constraint**: When an agent rebuilds a macOS app binary or encounters recurring 'Permission needed' loops despite permissions being toggled ON in System Settings:
  - The agent MUST run `tccutil reset Accessibility <bundle-id>` and `tccutil reset ListenEvent <bundle-id>` to clear stale TCC cache entries.
  - After resetting TCC caches and restarting the app, macOS will prompt for fresh Accessibility trust, stabilizing the permission grant for the new build.

## Chrome DevTools MCP Safety Rules
The user runs a single Chrome instance with the remote debugging port open, meaning their personal browsing tabs are mixed with development tabs. To protect the user's personal data and workflow, you MUST strictly adhere to the following rules when using Chrome DevTools MCP:

1. **Verify the Target Tab**: Before taking any action (navigating, clicking, typing, evaluating script), ALWAYS use `mcp_chrome-devtools_list_pages` to get the list of open tabs and their IDs.
2. **Require Confirmation on Ambiguity**: If it is not 100% obvious which tab you are supposed to interact with, you MUST ask the user to confirm the target tab before doing anything. 
3. **Strict Isolation**: NEVER modify, close, navigate, or clear data on any tab other than the explicit target tab. Treat all other tabs as off-limits personal data.
4. **Prefer New Tabs**: If a task requires testing a new URL or running a clean test, use `mcp_chrome-devtools_new_page` to spawn a fresh tab rather than hijacking an existing one. Work exclusively within that new tab.
