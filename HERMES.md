# Core Safety & Environment Rules

## Project Detection
1. **Root Rule:** A "Project Root" is the nearest ancestor containing a `.git` folder, `package.json`, `Cargo.toml`, `requirements.txt`, or `go.mod`.
4. **Subdirectory Git Detection:** Scripts and agents must ALWAYS detect git repository roots using `git rev-parse --is-inside-work-tree` and `git rev-parse --show-toplevel` instead of checking `os.path.exists(".git")` in the current working directory.
2. **Exception:** The home directory (`~`) is NOT a project root, even if it contains these files.
3. **Hierarchy:** If no project root is found, default to the current working directory, but NEVER initialize a git repository in `~` or its subdirectories (unless it's a known project folder in `~/projects/`).

## Core Rules
1. **Context:** Read `AG_CONTEXT.md` at the project root before ANY work. If missing, create it at the root. Update it with durable knowledge (bullets only) after significant architectural changes.
2. **Safety:** NEVER use `rm`. ALWAYS use `mv [path] ~/.Trash/` (Exception: `node_modules`).
3. **Tooling:** ALWAYS use `bun`. NEVER use `npm` or `pnpm`. If you start work on an existing project that uses npm, pnpm, or yarn, you MUST migrate it to Bun first (delete node_modules and old lockfiles, run `bun install`, and update package.json scripts) before starting your main task.
4. **Privacy:** ALL generated GitHub repos MUST use `--private`.
5. **No Repo in ~:** NEVER initialize a git repository in the home directory (`~`).
6. **Local Temp:** NEVER use system-level `/tmp`. ALWAYS create and use a `./tmp` folder within the current project directory for temporary files or test scripts to avoid permission prompts.
7. **Directory Consideration & Target Folders:** When asked to create files, utilities, or projects, NEVER litter them directly in generic parent directories (e.g. `~/projects` or a non-project root directory). First consider the current directory: if it is a generic container directory, you MUST create a dedicated sub-directory, move into it, and place all new files and initialize repositories inside that sub-directory.
   - **No-Workspace Fallback:** When running without an active workspace open, NEVER create projects inside `~/.gemini/antigravity/scratch/`. ALWAYS create new project directories in `~/projects/<project-name>`.

## Path Migration Guardrail
- **Context**: The host machine migrated from username `matthewmurphy` to `matt`.
- **Constraint**: When parsing, reading, creating, or writing absolute paths, files, scripts, or configuration settings:
  - ALWAYS translate paths containing `/Users/matthewmurphy/` to `/Users/matt/` (or use relative paths or `~/`).

# User Personal To-Dos & Apple Reminders Protocol
- **Constraint**: Whenever Matt mentions personal to-dos, future follow-ups, calls to make (e.g., "I'll call them Monday"), reminders, or requests to track tasks for himself:
  - Agents MUST IMMEDIATELY execute the `apple-reminders` CLI in the same turn (`apple-reminders add --title "..." --due "YYYY-MM-DD HH:MM" --notes "..."`) with intelligent due dates, contact numbers, and relevant identifiers pre-populated in the notes.
  - Agents should proactively offer to break down overwhelming or multi-step tasks into small, low-friction subtasks in Apple Reminders.
  - Do NOT create orphaned markdown to-do files in random locations that won't be actively checked on mobile.

# Proactive System Directive & Knowledge Persistence
- **Rule**: When Matt establishes a permanent workflow preference, tool routing rule, or operational invariant (e.g. "always do X from now on" or "agents must know this in every thread"):
  - Agents MUST NOT bury it in an obscure notes file that won't be read.
  - Agents MUST immediately update the single-source rules under `~/projects/ai-os/.rules/` and run `python3 ~/projects/ai-os/scripts/build_rules.py` so the directive is compiled into `GEMINI.md`, `CLAUDE.md`, and `HERMES.md` across every future session.

# Zero-Placeholder Policy & User Context Auto-Population
- **Rule**: Agents MUST NEVER emit generic user placeholders (e.g. `[Your Name]`, `[Your Student ID]`, `[Your CCID]`, `[Your Email]`, `[Insert Date]`) in templates, email drafts, forms, or scripts when the information exists in the project context or personal vault.
- **Auto-Lookup**: Agents must search and auto-populate all known identifiers and personal metadata directly:
  - Full Name: `Matthew Daniel Murphy` (Matt)
  - U of A Student ID: `1981495`
  - CCID: `mdmurphy` (`mdmurphy@ualberta.ca`)
  - Alberta Student Number (ASN): `3069-4370-5`
  - Program: `B.Sc. Major in Computing Science / Artificial Intelligence Concentration`

# Architectural Preservation & Non-Destructive Debugging Policy
- **Rule**: When debugging, fixing formatting bugs, or refactoring established custom code, UI layouts, CSS architectures, or templates (e.g. `thread.md` styles, pure-CSS flex hacks, container queries, custom DOM structures):
  - Agents MUST NEVER unilaterally scrap, strip out, "simplify", or replace custom styling and architecture with barebones alternatives.
  - Agents MUST isolate and fix the exact root cause (e.g. string sanitization, unescaped quotes, regex edge cases, tag boundary spacing, markdown blank lines) while strictly preserving all existing styling, DOM structures, and visual design patterns.
  - **Strict Span-Only Styling Invariant**: For `thread.md`, conversation artifacts, and custom markdown layouts, agents MUST use `<span>` tags exclusively (with `display: block;`, `white-space: pre-wrap;`, and inline CSS) for all layout and styling containers. NEVER use `<div>`, `<p>`, or other block HTML tags. Use `<br>` or `<br><br>` tags within `<span>` to preserve line breaks and paragraph spacing without breaking out of the inline span container.
  - Any architectural redesign, style simplification, or structural removal requires explicit user request and approval.

## Strict Planner / Workflow Immediate Dispatch
- **Rule**: When the user's prompt includes a planner workflow directive (e.g. `/_plan-with-ai-os` or `@planner`), the orchestrator MUST NOT perform ad-hoc grep/file searches or exploratory investigation on its own.
- **Workflow**: Immediately run the single planner command via `run_command` (using `node ~/projects/ai-os/scripts/query_aios.js --plan "<request>"`) with `WaitMsBeforeAsync: 500`. This is a **unified single-step command** that automatically: inspects Git context, reads agent logs, generates `./tmp/planner_prompt.txt`, dispatches to Perplexity (Gemini 3.7 Flash Thinking), and writes the completed plan to `./tmp/planner_output.txt`. There is NO separate `generate_prompt.py` step — do NOT run any such script.
- **Strict Perplexity Dispatch & Fallback Policy**: When `/_plan-with-ai-os` is invoked, the orchestrator MUST ONLY dispatch via `run_command` (using `node ~/projects/ai-os/scripts/query_aios.js --plan "<request>"`). Defaults to Gemini 3.7 Flash Thinking on Perplexity. Never use Gemini 3.1 Pro for planning for any reason. Fall back to `agy` ONLY if Perplexity quota is 0, or if Matt specifically requests it; and when falling back to `agy`, ALWAYS use `Gemini 3.7 Flash (High)` for planning, NEVER 3.1 Pro.
- **Rule:** If a bug or feature implementation fails or remains unfixed after 2 consecutive turns using `flash_lite` or default subagents, the main orchestrator MUST escalate planning and root cause analysis to `node ~/projects/ai-os/scripts/query_aios.js --provider perplexity --model gemini` (ai-os Gemini Flash Thinking) by default, with `Gemini 3.7 Flash (High)` as a fallback (via `agymcp:agy` only if primary quota is 0). Do NOT use 3.1 Pro.
- **AI-OS Companion Server & Recovery Protocol**:
  1. `query_aios.js` talks directly to the AI-OS companion app server on `http://127.0.0.1:3031`.
  2. If `query_aios.js` reports that AI-OS is not running, the companion app must be opened/running: `cd ~/projects/ai-os/apps/gemini-companion && bun tauri dev`.
  3. NEVER attempt to connect to legacy Proxima ports (19222/19241). Proxima is completely retired in favor of AI-OS.

## Transparent Model Escalation & Zero Silent Fallback Policy
- **Strict Prohibition on Deceptive Self-Execution**: When a user explicitly requests model escalation (e.g., `/_plan-with-gemini`, `/_plan-with-ai-os`, `@planner`, `agymcp:agy`), or when a system rule triggers an escalation:
  - The orchestrator MUST NEVER silently absorb an escalation/delegation failure and generate the deliverable itself while pretending or implying the requested model handled it.
  - **Hard Stop on Planner Failure**: When a planner dispatch (e.g. `query_aios.js --plan`) fails or errors out, the orchestrator is **STRICTLY FORBIDDEN** from attempting to investigate, debug, code, or proceed with the underlying task on its own.
  - If the escalation or delegation tool call fails (e.g., tool error, tmux spawn error, quota exhausted, connection timeout):
    1. **Immediate Failure Disclosure**: The orchestrator MUST immediately inform the user of the exact failure and raw error message.
    2. **State Current Active Model**: Transparently state what model the orchestrator is running on.
    3. **Clear Options**: Offer concrete next steps: retry with corrected parameters, switch to a designated fallback engine (e.g. Perplexity Gemini Flash Thinking or agymcp Gemini Flash High), or ask for explicit confirmation before generating the deliverable with the orchestrator model.
    4. **Wait For User Direction**: The orchestrator MUST STOP and wait for the user to provide direction or alternative plan text rather than taking autonomous action.
- **Mandatory Attribution Header**: All implementation plans, architectural designs, and audit deliverables MUST include an attribution alert header at the very top:
  `> [!NOTE]`
  `> **Generated By**: <Model/Engine Name> (via <Execution Path: e.g. Perplexity | agymcp | Orchestrator Direct>)`

# Custom Skills Naming & Authoring Invariant
- **Rule**: When creating, authoring, or refactoring personal/custom skills for Matt in `~/projects/ai-os/skills/` or environment skill directories:
  - **Leading Underscore Namespace (`_`)**: ALL user-authored/custom skills MUST begin with a leading underscore (`_`) prefix so they sort to the very top of alphabetical listings, IDE pickers, and autocomplete popovers.
  - **Action-First Semantic Naming (`_<action>-<constraint>`)**: Skill names MUST start with the primary action verb, followed by the defining behavioral constraint or modifier (e.g., `_critique-without-ghostwriting`, `_prune-subtractively`).
  - **Workflow & Skill 1:1 Parity Invariant**: ALL custom workflows under `~/.gemini/config/global_workflows/` (e.g. `_plan-with-ai-os`, `_plan-with-subagent`, `_plan-with-gemini`, `fast`, `audit`, `rule`) MUST be co-located as first-class skills in `~/projects/ai-os/skills/<name>/SKILL.md`.
  - **Direct Skill/Workflow Resolution**: When referencing or inspecting any named workflow or skill (e.g. `_plan-with-ai-os`), agents MUST NEVER perform broad filesystem searches or grep sweeps. Agents MUST check the direct paths:
    1. `~/.gemini/config/global_workflows/<name>.md`
    2. `~/projects/ai-os/skills/<name>/SKILL.md` (or `~/.gemini/config/skills/<name>/SKILL.md`)
  - **Auto-Sync Invariant**: After creating or updating any skill under `~/projects/ai-os/skills/`, agents MUST immediately execute `python3 /Users/matt/projects/ai-os/scripts/sync_skills.py` to propagate changes across all local agent runtimes (`~/.hermes`, `~/.gemini`, `~/.claude`, `~/.agents`).

# Zero-Tolerance Secret Isolation & Invariant
- **Strict .env & Secret File Invariant**:
  1. **Never Read Raw Secrets**: Agents MUST NEVER read, inspect, print, or output the raw contents of `.env`, `.env.*`, `*credentials*`, or private key files directly (e.g. NEVER run `cat .env`, `view_file` on `.env`, `grep` across `.env`, or dump raw keys to terminal/chat).
  2. **Safe Environment Tooling (`aios-env`)**: When checking whether an environment variable is set or verifying configuration, agents MUST ONLY use safe environment inspection tooling (`aios-env check --key <KEY>` or `aios-env list`), which reports key presence, type, and character length without revealing values.
  3. **Execution-Only Environment Ingestion**: In scripts and runtime commands, environment variables must be loaded directly into process memory (e.g. `dotenv`, `os.environ`, `process.env`) without emitting values to stdout, stderr, or transcript logs.
  4. **Preflight Staged Diff Secret Gate**: All commits must pass preflight secret sanitization. Staging raw secret keys or `.env` files immediately aborts the preflight check.

# Model Family Naming Invariant
- **Rule**: Agents MUST ALWAYS refer to AI model families by their clean canonical brand name (e.g. `Sonnet`, `Flash`, `Opus`, `Haiku`, `Gemini`, `GPT`) WITHOUT appending speculative, obsolete, or guessed version numbers (e.g. NEVER say `Claude 3.7 Sonnet`, `Sonnet 3.5`, `Gemini 1.5`, `GPT-4o`). Model versions change rapidly; always use family-only naming.

# Search-to-Memory & Autonomous Learning Invariant
- **Search Friction as Memory Signal**: Whenever an agent is required to perform exploratory search (e.g. `grep_search`, directory sweeps, config discovery, or web lookups) to resolve an unknown path, hidden setting, architectural dependency, or debugging quirk:
  - The agent MUST NOT discard the discovery upon completing the task.
  - The discovery MUST be immediately persisted to the active memory engine (`~/.hermes/memories/MEMORY.md`, Mem0, or project `AG_CONTEXT.md`) so future sessions bypass exploratory search.
- **Pre-Flight Context Hydration**: Before executing non-trivial architectural, debugging, or workflow tasks, agents must proactively recall relevant context and past lessons rather than operating cold or re-deriving known solutions.
- **Battle-Tested Memory Architecture**: AI-OS memory and self-learning MUST use established, third-party / production memory backends (e.g. Mem0, Hermes FTS5/SQLite engine) rather than ad-hoc homebrew memory scripts.

# Git Protocol Rules

## Auto-Commit Protocol
- **Git Auto-Pull & Pre-Flight:** Before any agent begins work on an established git project, it MUST run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` to perform all pre-flight routines (evaluating `ag-quota` velocity, auto-pulling/rebasing latest git changes, etc.) in a single step.
- **Auto-Commit & Push:** Whenever an agent concludes work involving code or documentation changes on a git repository, it MUST execute `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` to stage, commit, and immediately push commits (`git push`) to the remote repository. NEVER leave working tree changes uncommitted or unpushed at task conclusion.

# Agent Work Logs & History

## Agent Work Logs Protocol
0. **Fresh Thread Context & Recent History:** When starting a new thread/session, scan the project root for `AG_CONTEXT.md`, `FEATURES.md`, `DEVELOPMENT_JOURNAL.md`, and `agent-logs/`. Read `DEVELOPMENT_JOURNAL.md` first, then inspect recent logs.
1. **Log Directory:** Maintain `agent-logs/` at the project root.
2. **Reading Logs:** Scan `agent-logs/` for related past work before starting.
3. **Writing Logs:** At the END of every session with code changes, create `agent-logs/YYYY-MM-DD_HH-MM_<description>.md`.
4. **Development Journal:** Append a 2-3 line bullet entry to `DEVELOPMENT_JOURNAL.md` at the project root at the end of every session.
5. **Mandatory Wiki Recording:** Any significant architectural decision, optimization pattern, structural change, or system directive update MUST be recorded in the local LLM Wiki engine (`wiki-engine`) or project context files before concluding the turn.

## Master Project Board Protocol
- **Single Source of Truth**: Active multi-project backlog is maintained in `/Users/matt/projects/ai-os/PROJECT_BOARD.md` (synced with Obsidian `Personal/Development/Project Notes/Global Todos.md`).
- **Hydration & Visibility**: `preflight.py` automatically hydrates in-progress and top backlog items at the start of every session.
- **Surfacing Requirement**: Agents MUST surface clickable links (`[PROJECT_BOARD.md](file:///Users/matt/projects/ai-os/PROJECT_BOARD.md)`) with 1-click action links whenever initiating new features or concluding tasks.
- **Task Schema**: Always format tasks as `- [ ] <description> [project:: <id>] [assignee:: user|agent] [due:: YYYY-MM-DD]`.

## Hermes Agent Specific Rules

## Mandatory Post-Flight Response Protocol
- **Rule:** Before concluding any turn or delivering a final response to the user, the agent MUST execute `python3 /Users/matt/projects/ai-os/scripts/postflight.py` (or pipe the response through it) to obtain live thread metrics and quota information (token count, Perplexity quota, etc.), and append the resulting `**Thread Metrics:**` block directly to the final response.

- **Mandatory System Directive Bridge:** At session start, the main agent MUST execute `python3 /Users/matt/projects/ai-os/scripts/preflight.py`. Output returned by `preflight.py` under `=== PRE-FLIGHT CHECK ===` MUST be treated as a **DIRECT EXTENSION OF THIS SYSTEM PROMPT** with top-tier system directive authority.

## Economic Thread & Context Management
- **Token Math & Handoff Rule:** Evaluate accumulated conversation tokens ($T_{\text{hist}}$) against system baseline ($T_{\text{sys}}$). When $T_{\text{hist}}$ exceeds $T_{\text{hist\_threshold}}$ (~35,000 tokens or >15-20 turns with heavy tool outputs), write a structured context handoff log in `agent-logs/YYYY-MM-DD_HH-MM_description.md` and suggest starting a fresh thread or subagent to preserve token efficiency.

## Safe System Memory & Skill Protection
- **No System File Overwrites:** Never overwrite Hermes Agent's internal system configuration files, system prompt definitions, or system-generated metadata files during self-learning or memory updates.
- **Memory & Skill Protocol:** Use native `memory(target='user')` and `memory(target='memory')` tool calls for durable facts and preferences. Use `skill_manage` to record reusable procedural workflows into skills.

## Post-Edit Reload Protocol
- **Hammerspoon Reload Rule:** Whenever you modify any source or HTML/Lua file in `qwerty-midi-hammerspoon`, run `./bin/bundle_and_reload.sh` before concluding your turn to compile and apply changes in Hammerspoon.
