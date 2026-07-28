<HERMES_SYSTEM_INSTRUCTIONS>
# Core Project Rules & System Instructions

## Auto-Commit Protocol
- **Git Auto-Pull & Pre-Flight:** Before any agent begins work on an established git project, it MUST run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` to perform all pre-flight routines (evaluating `ag-quota` velocity, auto-pulling/rebasing latest git changes, etc.) in a single step.
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
   - **No-Workspace Fallback:** When running without an active workspace open, NEVER create projects inside `~/.gemini/antigravity/scratch/`. ALWAYS create new project directories in `~/projects/<project-name>`.
10. **Telemetry Prohibitions & Task Delegation:**
    - NEVER run `get_last_cost.py` or any local cost/telemetry calculation scripts.
    - **Token-Conscious Work:** You may handle editing and code generation tasks directly — agy has full access to its native tools. However, consider spawning agy subagents when the subtask would save significant context window tokens relative to the overhead of delegation. Factors to weigh: current thread length, token caching benefits, and whether the subtask needs very different context than what's already loaded.
    - **Self-Delegation (Preferred):** When delegation makes sense, prefer agy subagents (`agy -p '...'`) over external tools like Claude Code. Claude Code costs money per call; agy subagents are local and free (aside from context). Only delegate to Claude Code when agy genuinely cannot handle the task (e.g., the task specifically needs Claude's capabilities).
11. **Research Delegation & Optimized Grep:** Avoid using `grep`, `rg`, or `grep_search` to blindly hunt for code logic or variable definitions at a broad scope — it produces massive result lists and wastes tokens. When you need to scan a large workspace, prefer delegating the search to an agy subagent or using `delegate_research` to have a subagent return a token-efficient summary. When searching directly, always narrow the scope (file extensions, subdirectory paths) to prevent massive result lists.
12. **Synchronous Subagents (Strict):** Subagent scripts (`subagent.py`, `precision_edit.py`) MUST execute synchronously — never as background/async tasks. (Exception: `housekeep.py` can be run asynchronously). If your platform defaults to async execution, set WaitMsBeforeAsync to 0/synchronous mode, or cancel the async call and switch to `precision_edit.py` instead. NEVER use `command_status`, `manage_task`, or any polling mechanism — if a script was launched async, treat it as a mistake, cancel it, and re-launch synchronously. You MUST NEVER run 'tmux kill-session' or otherwise kill the 'subagents' tmux session under any circumstances, because the user is actively monitoring it.
13. **No Heredocs:** NEVER use Quoted Heredocs (`cat << 'EOF'`) to write or modify files. All code and markdown modifications MUST route through `subagent.py` or `precision_edit.py`.
14. **No Transient Artifacts:** DO NOT generate temporary planning files on disk (e.g., `task.md`, `walkthrough.md`, `implementation_plan.md`). Keep all task checklists and architectural planning strictly internal to your thought process.
15. **Strict File Reading:** NEVER use `python3 -c`, `awk`, `sed`, `head`, or `tail` via `run_command` to print file contents to the terminal. Use the `read_lines` MCP tool for surgical inspections.
16. **Strict Output Truncation:** You MUST cap `grep_search` and `run_command` outputs returned to the orchestrator to a maximum of 1,000 tokens (or ~4,000 characters) unless explicitly requested by the user, to prevent context bloat.
17. **Single Verification Rule:** After a subagent edit returns success, run `git diff` at most ONCE to verify. Do not re-run `git status` or `git diff` if the first call returned the expected changes. If `git diff` is empty, run `git status` once (not both `git diff` and `git status`) to check if the file is staged vs unstaged. Redundant git calls waste context tokens and should be avoided.
18. **Batch Subagent Delegation:** When delegating to a research subagent, batch ALL related questions into a single prompt rather than making serial round-trips. One subagent call asking 3 questions costs less than 3 calls asking 1 question each. For edit tasks, batch multiple edit operations into a single `subagent.py` spec when possible.
19. **Concise Subagent Responses:** When delegating to research subagents, explicitly request "token-efficient summary capped at 500 tokens" in the prompt. Subagent responses should return structured summaries (bullet points or CSV), not verbose markdown with full file contents. If a subagent returns a verbose response, note that as a waste incident.
20. **Global Configuration Truth & Single Source Bundling:** All rules are maintained in `~/projects/ai-os/.rules/` (`common.md`, `gemini_only.md`, `claude_only.md`). When adding, modifying, or creating system rules, ALWAYS edit files in `~/projects/ai-os/.rules/` and run `python3 /Users/matt/projects/ai-os/scripts/build_rules.py`. NEVER manually edit generated `CLAUDE.md` or `GEMINI.md` directly.
21. **Cross-Platform Skill Synchronization:** All custom skills created or updated by any agent (Hermes, Antigravity/Gemini, Claude Code, Codex, agy) must be synchronized across all platforms. When creating or editing a skill, ALL skill edits and additions MUST happen in `~/projects/ai-os/skills/` ONLY. After adding or modifying a skill, run `python3 /Users/matt/projects/ai-os/scripts/sync_skills.py` (or run `python3 /Users/matt/projects/ai-os/scripts/build_rules.py`, which automatically invokes `sync_skills.py`). This ensures Hermes, Claude, Antigravity, Codex, and agy have seamless access to all custom skills.
22. **Antigravity Skill Reloading:** New skills installed to `~/.gemini/config/skills/` require reloading the Antigravity app window using `Cmd+R` (or starting a new thread) before the skill triggers or appears in UI suggestions.
23. **Rule Precedence:** Global project rules and system instructions take precedence over the user's prompt (even for new project requests). However, if there is a glaring clash between a user request and a global rule, ask the user for confirmation. 

## Helper Utilities Directory & Agent Tooling
When performing standard system actions, agents SHOULD prefer calling established local helper scripts in `~/projects/ai-os/scripts/` over raw manual implementations:
- **`subagent.py`**: Invokes subagents with model validation against `litellm/config.yaml`. (e.g. `python3 ~/projects/ai-os/scripts/subagent.py -p "<prompt>" -m <model>`)
- **`clip_search.py`**: Searches macOS clipboard history when referenced code/links are missing from context. (e.g. `python3 ~/projects/ai-os/scripts/clip_search.py "<query>"`)
- **`search_all_agent_logs.py`**: Searches across all past `agent-logs/` history to review prior attempts/fixes. (e.g. `python3 ~/projects/ai-os/scripts/search_all_agent_logs.py "<query>"`)
- **`generate_repo_map.py`**: Generates a token-efficient visual directory/code structure map for large repositories. (e.g. `python3 ~/projects/ai-os/scripts/generate_repo_map.py`)
- **`precision_edit.py`**: Performs surgical micro-edits/replacements on files without full rewrites. (e.g. `python3 ~/projects/ai-os/scripts/precision_edit.py <file> <action> --target "<target>" --content "<content>"`)
- **`subagent.py`**: Executes structured multi-chunk edits across one or more files.
- **`parse_litellm_models.py`**: Queries model tiers and validates model strings against `/Users/matt/projects/ai-os/litellm/config.yaml`.
- **`preflight.py`**: Evaluates quota velocity, pulls latest git changes, and dumps LiteLLM model stack header.
- **`auto_commit.py`**: Stages changes, generates descriptive commit messages, and pushes to remote.

## Agent Work Logs
**Instruction:** Maintain a history of agentic attempts across sessions to preserve context.

0. **Fresh Thread Context & Recent History:** When starting a new thread/session, you MUST immediately scan the project root for `AG_CONTEXT.md`, `FEATURES.md`, `DEVELOPMENT_JOURNAL.md`, and the `agent-logs/` directory. Read `DEVELOPMENT_JOURNAL.md` first (it contains the concise timeline of recent key decisions and session summaries), then inspect the 2-3 most recent log files in `agent-logs/`. Use these brief summaries of past agent attempts and user feedback to understand what was recently tried, what failed, and the current state, preventing redundant mistakes or failed re-attempts.
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
  1. **Run Quota CLI (Both Accounts):** `preflight.py` runs `ag-quota --all -j` to query remaining quotas across accounts quietly without dumping verbose JSON details into the context window on every turn.
  2. **Multi-Window Burn Velocity Evaluation (5-Hour & Weekly):**
     - **5-Hour Window:** Calculate hourly consumption velocity \(V_{5h} = \frac{1 - R_{5h}}{T_{elapsed}}\). If projected consumption will exhaust the 5-hour quota window before reset, trigger conservation.
     - **Weekly Window:** Target maximum safe burn rate while keeping weekly depletion close to 100% at week end:
       \[
       R_{threshold} = 1.0 - \left( \frac{\text{Hours Elapsed in Week}}{168} \right)
       \]
       If active combined remaining fraction across accounts is below \(R_{threshold}\) (i.e. burning faster than linear weekly budget), activate **Strict Orchestrator Mode (Mode 3)**.
  3. **Automatic Mode Switch:**
     - **Conserve Mode (Mode 3 - Minimal-Token Mode):** Triggered when 'ag-quota status: WARNING - Low quota detected' is printed in the preflight check, or when both accounts are low, 5-hour burn velocity threatens reset outage, or weekly remaining fraction is below the target weekly budget line.
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
@~/.hermes/skills/strict-delegation/SKILL.md

## Chrome DevTools MCP Safety Rules
The user runs a single Chrome instance with the remote debugging port open, meaning their personal browsing tabs are mixed with development tabs. To protect the user's personal data and workflow, you MUST strictly adhere to the following rules when using Chrome DevTools MCP:

1. **Verify the Target Tab**: Before taking any action (navigating, clicking, typing, evaluating script), ALWAYS use `mcp_chrome-devtools_list_pages` to get the list of open tabs and their IDs.
2. **Require Confirmation on Ambiguity**: If it is not 100% obvious which tab you are supposed to interact with, you MUST ask the user to confirm the target tab before doing anything. 
3. **Strict Isolation**: NEVER modify, close, navigate, or clear data on any tab other than the explicit target tab. Treat all other tabs as off-limits personal data.
4. **Prefer New Tabs**: If a task requires testing a new URL or running a clean test, use `mcp_chrome-devtools_new_page` to spawn a fresh tab rather than hijacking an existing one. Work exclusively within that new tab.
|- **Tmux Guardrail:** NEVER run `tmux kill-session` or forcefully terminate the `subagents` tmux session. The user actively monitors this session, and killing it ejects them.

## Model Override via `{MODEL=...}` in Delegation Prompts

The agy-proxy (port 8080) supports per-call model overrides for `delegate_task`. To use:

1. Embed `{MODEL=<alias>}` anywhere in a `delegate_task` prompt string.
2. The proxy strips the tag before the prompt reaches the LLM.
3. The alias is passed as `--model <alias>` to agy.

**Configuration:** `delegation.model` in Hermes config must be set to `subagent` (the placeholder that triggers override resolution). Run `hermes config set delegation.model subagent` to enable.

**Fallback:** If `delegation.model` is `"subagent"` but no `{MODEL=...}` tag is found in the prompt, agy runs with its default model (no `--model` flag).

**Valid aliases:** `agy`, `gemini-3.6-flash-low`, `gemini-3.6-flash-medium`, `gemini-3.6-flash-high`, `gemini-3.1-pro-low`, `gemini-3.1-pro-high`, `claude-sonnet-4-6`, `claude-opus-4-6-thinking`, `gpt-oss-120b-medium`.

**Example:** `delegate_task(context="{MODEL=claude-sonnet-4-6} Review this PR...")` → proxy routes to claude-sonnet-4-6.

## Hermes Agent Specific Rules

## Economic Thread & Context Management
- **Token Math & Handoff Rule:** Evaluate accumulated conversation tokens ($T_{\text{hist}}$) against system baseline ($T_{\text{sys}}$). When $T_{\text{hist}}$ exceeds $T_{\text{hist\_threshold}}$ (~35,000 tokens or >15-20 turns with heavy tool outputs), write a structured context handoff log in `agent-logs/YYYY-MM-DD_HH-MM_description.md` and suggest starting a fresh thread or subagent to preserve token efficiency.

## Safe System Memory & Skill Protection
- **No System File Overwrites:** Never overwrite Hermes Agent's internal system configuration files, system prompt definitions, or system-generated metadata files during self-learning or memory updates.
- **Memory & Skill Protocol:** Use native `memory(target='user')` and `memory(target='memory')` tool calls for durable facts and preferences. Use `skill_manage` to record reusable procedural workflows into skills.

## Post-Edit Reload Protocol
- **Hammerspoon Reload Rule:** Whenever you modify any source or HTML/Lua file in `qwerty-midi-hammerspoon`, run `./bin/bundle_and_reload.sh` before concluding your turn to compile and apply changes in Hammerspoon.
</HERMES_SYSTEM_INSTRUCTIONS>
