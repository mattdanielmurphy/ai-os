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
- **Rule**: When the user's prompt includes a planner workflow directive (e.g. `/proxima-planner` or `@planner`), the orchestrator MUST NOT perform ad-hoc grep/file searches or exploratory investigation on its own.
- **Workflow**: Immediately run the prompt generation script, query the planner (Perplexity via `proxima:ask_perplexity`), and present the resulting implementation plan without intermediate manual codebase rummaging.
- **Strict Perplexity Dispatch & Fallback Policy**: When `/proxima-planner` is invoked, the orchestrator MUST ONLY dispatch to Perplexity via `run_command` (using `node ~/projects/ai-os/scripts/query_proxima.js --provider perplexity --input ./tmp/planner_prompt.txt --output ./tmp/planner_output.txt --timeout 600`) with `WaitMsBeforeAsync: 500`. Never use Gemini 3.1 Pro for planning for any reason. Fall back to `agy` ONLY if Perplexity quota is 0, or if Matt specifically requests it; and when falling back to `agy`, ALWAYS use `Gemini 3.7 Flash (High)` for planning, NEVER 3.1 Pro.
- **Connection Recovery**: If the `query_proxima.js` script fails, ensure Proxima is running (`cd ~/projects/external/Proxima && bun start &`) and retry.

# Custom Skills Naming & Authoring Invariant
- **Rule**: When creating, authoring, or refactoring personal/custom skills for Matt in `~/projects/ai-os/skills/` or environment skill directories:
  - **Leading Underscore Namespace (`_`)**: ALL user-authored/custom skills MUST begin with a leading underscore (`_`) prefix so they sort to the very top of alphabetical listings, IDE pickers, and autocomplete popovers.
  - **Action-First Semantic Naming (`_<action>-<constraint>`)**: Skill names MUST start with the primary action verb, followed by the defining behavioral constraint or modifier (e.g., `_critique-without-ghostwriting`, `_prune-subtractively`).
  - **Auto-Sync Invariant**: After creating or updating any skill under `~/projects/ai-os/skills/`, agents MUST immediately execute `python3 /Users/matt/projects/ai-os/scripts/sync_skills.py` to propagate changes across all local agent runtimes (`~/.hermes`, `~/.gemini`, `~/.claude`, `~/.agents`).

# Git Protocol Rules

## Auto-Commit Protocol
- **Git Auto-Pull & Pre-Flight:** Before any agent begins work on an established git project, it MUST run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` to perform all pre-flight routines (evaluating `ag-quota` velocity, auto-pulling/rebasing latest git changes, etc.) in a single step.
- **Auto-Commit:** Run `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` to delegate the commit process. Auto-commit automatically requires a descriptive commit message detailing the changes made (generated via LiteLLM from staged diff/files) and pushes the commits (`git push`) to the remote repository.

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

## Claude Code / Hermes Agent Specific Rules

## Mandatory Post-Flight Response Protocol
- **Rule:** Before concluding any turn or delivering a final response to the user, the agent MUST execute `python3 /Users/matt/projects/ai-os/scripts/postflight.py` (or pipe the response through it) to obtain live thread metrics and quota information (token count, Perplexity quota, etc.), and append the resulting `**Thread Metrics:**` block directly to the final response.

## Auto-Commit Protocol
- **Git Auto-Pull & Pre-Flight:** Before any agent begins work on an established git project, it MUST run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` to perform all pre-flight routines (evaluating `ag-quota` velocity, auto-pulling/rebasing latest git changes, etc.) in a single step.
- **Auto-Commit:** Run `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` to delegate the commit process. Auto-commit automatically requires a descriptive commit message detailing the changes made (generated via LiteLLM from staged diff/files) and pushes the commits (`git push`) to the remote repository.
- **Post-Flight:** Before concluding any turn or committing, agents MUST run `python3 /Users/matt/projects/ai-os/scripts/postflight.py` to retrieve and append live thread metrics and token counts to their responses.

- **Interactive Handoff & Spawn**: Never run agents blind (do not use `--non-interactive`, `--print`, or background execution without attachment). Handoffs must be run interactively to allow the user to review the plan and steering instructions. The handoff command MUST execute the `handover.py` script, which replaces the current process (`os.execvp("agy", ...)`) to attach the interactive `agy` CLI session directly to your terminal. Execute the handoff by running:
  `python3 /Users/matt/projects/ai-os/scripts/handover.py --to-model pro --completed "<what you analyzed/researched>" --next-steps "<what needs to be done next>"`
- **Exclusively Use agy for Subagents**: When agy quota is high/abundant, use agy exclusively. If a prompt goes to Hermes (default), use the MCP tool to spawn a tmux-bound `agy` CLI instance as a subagent, or if already in agy, have agy spin up its own subagent natively. Do not spawn external API agents or run subagents without attaching/steering capabilities.
