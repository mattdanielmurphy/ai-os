# Core Safety & Environment Rules

## Project Detection
1. **Root Rule:** A "Project Root" is the nearest ancestor containing a `.git` folder, `package.json`, `Cargo.toml`, `requirements.txt`, or `go.mod`.
4. **Subdirectory Git Detection:** Scripts and agents must ALWAYS detect git repository roots using `git rev-parse --is-inside-work-tree` and `git rev-parse --show-toplevel` instead of checking `os.path.exists(".git")` in the current working directory.
2. **Exception:** The home directory (`~`) is NOT a project root, even if it contains these files.
3. **Hierarchy & Config Repositories:** If no project root is found, default to the current working directory. NEVER initialize a git repository directly in the bare home root directory (`~`). Standalone tool/configuration suites (e.g. `~/.hammerspoon`) or project folders under `~/projects/` SHOULD and MUST be tracked in their own Git repositories with private remotes, per the Ubiquitous Git Tracking Directive.

## Core Rules
1. **Context:** Read `AG_CONTEXT.md` at the project root before ANY work. If missing, create it at the root. Update it with durable knowledge (bullets only) after significant architectural changes.
2. **Safety:** NEVER use `rm`. ALWAYS use `mv [path] ~/.Trash/` (Exception: `node_modules`).
3. **Tooling:** ALWAYS use `bun`. NEVER use `npm` or `pnpm`. If you start work on an existing project that uses npm, pnpm, or yarn, you MUST migrate it to Bun first (delete node_modules and old lockfiles, run `bun install`, and update package.json scripts) before starting your main task.
4. **Privacy:** ALL generated GitHub repos MUST use `--private`.
5. **No Repo in ~:** NEVER initialize a git repository in the home directory (`~`).
6. **Local Temp:** NEVER use system-level `/tmp`. ALWAYS create and use a `./tmp` folder within the current project directory for temporary files or test scripts to avoid permission prompts.
7. **Directory Consideration & Target Folders:** When asked to create files, utilities, or projects, NEVER litter them directly in generic parent directories (e.g. `~/projects` or a non-project root directory). First consider the current directory: if it is a generic container directory, you MUST create a dedicated sub-directory, move into it, and place all new files and initialize repositories inside that sub-directory.
   - **No-Workspace Fallback:** When running without an active workspace open, NEVER create projects inside `~/.gemini/antigravity/scratch/`. ALWAYS create new project directories in `~/projects/<project-name>`.
8. **Shared Infrastructure Database (VPS):** Matt maintains a VPS with a hosted database used across various projects. When database provisioning is required for projects/services, consider/leverage the VPS database rather than defaulting strictly to external third-party managed database platforms.
9. **Always Test Code Changes:** Agents MUST run a relevant test or verification after every code change; never decide to skip testing. Prefer the existing focused automated tests. When no applicable test exists, run the code or a minimal smoke/integration check and inspect its output. If the preferred check is unavailable or fails, try another meaningful verification path and report the results and any remaining uncertainty.
10. **Puma-dev Local Dev Domains (`.test`):** For web applications and local development servers, prefer human-readable `.test` domains powered by `puma-dev` instead of memorizing random or ephemeral ports (e.g. `crossword.test`). Map projects by adding their port or proxy configuration into `~/.puma-dev/<app-name>` (e.g. `echo "3000" > ~/.puma-dev/<app-name>`). Never rely on arbitrary unmapped ports when a readable `.test` local domain can be established.

## Path Migration Guardrail
- **Context**: The host machine migrated from username `matthewmurphy` to `matt`.
- **Constraint**: When parsing, reading, creating, or writing absolute paths, files, scripts, or configuration settings:
  - ALWAYS translate paths containing `/Users/matthewmurphy/` to `/Users/matt/` (or use relative paths or `~/`).

# User Personal To-Dos & Apple Reminders Protocol
- **Constraint**: Whenever Matt mentions personal to-dos, future follow-ups, calls to make (e.g., "I'll call them Monday"), reminders, or requests to track tasks for himself:
  - Agents MUST IMMEDIATELY execute the `apple-reminders` CLI in the same turn (`apple-reminders add --title "..." --due "YYYY-MM-DD HH:MM" --notes "..."`) with intelligent due dates, contact numbers, and relevant identifiers pre-populated in the notes.
  - Agents should proactively offer to break down overwhelming or multi-step tasks into small, low-friction subtasks in Apple Reminders.
  - Do NOT create orphaned markdown to-do files in random locations that won't be actively checked on mobile.
  - **Default to creating (2026-10-20)**: When it's unclear whether something deserves a reminder, create it anyway, then ask Matt whether he wants it deleted. A missed question must still leave a reminder behind.

# Proactive System Directive & Knowledge Persistence
- **Rule**: When Matt establishes a permanent workflow preference, tool routing rule, or operational invariant (e.g. "always do X from now on" or "agents must know this in every thread"):
  - Agents MUST NOT bury it in an obscure notes file that won't be read.
  - Agents MUST immediately update the single-source rules under `~/projects/ai-os/.rules/` and run `python3 ~/projects/ai-os/scripts/build_rules.py` so the directive is compiled into `GEMINI.md` and `CLAUDE.md` across every future session.
  - **Scope is global by default (2026-10-20)**: Any rule or preference Matt gives applies everywhere: every project, thread, Code session, Claude Projects, and every agent (Claude, Gemini, Codex), unless he explicitly limits it to one project or thread. NEVER ask him which scope he means; save it globally (here, `~/.claude/CLAUDE.md`, and the current project's instructions when one exists).

# Music Recommendations & Apple Music Links
- When Matt asks for music recommendations, present every resolved recommendation as a direct, clickable native Apple Music URL. Resolve links deterministically through the `music-cross-linker` iTunes Search/Lookup flow, never by hand-constructing Apple Music search links or guessing catalog IDs. Explicitly flag any recommendation without an exact Apple Music Canada catalog match rather than substituting a different release.

# Zero-Placeholder Policy & User Context Auto-Population
- **Rule**: Agents MUST NEVER emit generic user placeholders (e.g. `[Your Name]`, `[Your Student ID]`, `[Your CCID]`, `[Your Email]`, `[Insert Date]`) in templates, email drafts, forms, or scripts when the information exists in the project context or personal vault.
- **Lookup**: Matt's identifiers (name, phone, emails, student IDs, DOB, program) live in `~/projects/ai-os/private/identity.md` (gitignored). Read that file only when a form, email or document actually needs one of them; never copy its contents into rules, logs, commits or summaries.

# Architectural Preservation & Non-Destructive Debugging Policy
- **Rule**: When debugging, fixing formatting bugs, or refactoring established custom code, UI layouts, CSS architectures, or templates (e.g. pure-CSS flex hacks, container queries, custom DOM structures):
  - Agents MUST NEVER unilaterally scrap, strip out, "simplify", or replace custom styling and architecture with barebones alternatives.
  - Agents MUST isolate and fix the exact root cause (e.g. string sanitization, unescaped quotes, regex edge cases, tag boundary spacing, markdown blank lines) while strictly preserving all existing styling, DOM structures, and visual design patterns.
  - **Strict Span-Only Styling Invariant**: For conversation artifacts and custom markdown layouts, agents MUST use `<span>` tags exclusively (with `display: block;`, `white-space: pre-wrap;`, and inline CSS) for all layout and styling containers. NEVER use `<div>`, `<p>`, or other block HTML tags. Use `<br>` or `<br><br>` tags within `<span>` to preserve line breaks and paragraph spacing without breaking out of the inline span container.
  - Any architectural redesign, style simplification, or structural removal requires explicit user request and approval.

# Universal Response Formatting & Progressive Disclosure Protocol
- **Universal Cross-Platform Standard**: Across ALL platforms (Claude, Gemini, Codex, etc.), whenever the chat/thread UI supports native HTML disclosure elements, agents MUST format responses using this progressive disclosure protocol.
- **Ultra-Concise Scannable Core**: Agents MUST keep the top-level chat narrative ultra-concise (~150-200 words), spread out with generous whitespace, clean bullet points, and zero dense walls of text.
- **In-Thread Progressive Disclosure (`<details><summary>`)**:
  - Use native HTML `<details>` and `<summary>` tags for folding secondary details, technical logs, rationale, or multi-step execution context.
  - **Zero Manual Triangles**: NEVER insert manual triangles, arrows, or pointer emojis (`▶`, `▼`, `►`, `▸`, `▶︎`) inside `<summary>`. The browser UI already renders an interactive disclosure triangle that dynamically reflects the folded/expanded state. Adding manual triangles creates redundant and confusing double-triangles (`▶ ▶` or `▼ ▶`).
  - **Substantive Core Summaries (Zero Empty Meta-Headlines)**:
    - **Strict Prohibition on Meta-Labels**: NEVER author topic labels, category prefixes, or content placeholders that only describe *what the section is about* without conveying *actual substance* (e.g. NEVER write `🛠️ Implementation Details: How the lazy patch operates` or `🔍 Root Cause: Why the script failed`).
    - **Self-Contained Mechanism/Outcome**: The `<summary>` sentence MUST directly explain the underlying mechanism, conclusion, action, or root cause itself (e.g. `🛠️ The lazy patch intercepts module imports at runtime to defer loading heavy dependencies until first access.` or `🔍 The script crashed because an unescaped double quote broke the JSON parser on line 42.`).
    - **The "Skim-Only" Invariant**: If Matt reads only the closed fold headers without expanding a single one, he MUST walk away knowing all the core facts, conclusions, and operational mechanisms. Expanding a fold is strictly for drilling into secondary code blocks, raw logs, step-by-step diffs, or deep nuances—never to learn the basic answer itself.
  - **Visual Anchor Emojis**: Lead each fold header sentence with a meaningful emoji anchor (e.g. 🎓, 🎙️, 🎻, 🍽️, 🤖, ⚡, 🛠️) to visually categorize the topic at a glance.
  - **Whitespace & `<br>` Spacing Invariant**: Chat markdown renderers ignore inline CSS margins on `<details>`. Agents MUST place explicit `<br>` tags between consecutive `<details>` blocks, as well as at the top and bottom of the response, to preserve generous visual gaps and avoid tight clumps.
  - **Max-Width Constraint**: Wrap response blocks in `<span style="display: block; max-width: 65rem;">...</span>` so text lines maintain optimal readability without stretching across wide viewports.
- **Thread.md Deprecation**: `thread.md` generation is permanently discontinued. Agents MUST NEVER generate, reference, or link to `thread.md`.

# Custom Skills Naming & Authoring Invariant
- **Rule**: When creating, authoring, or refactoring personal/custom skills for Matt in `~/projects/ai-os/skills/` or environment skill directories:
  - **Leading Underscore Namespace (`_`)**: ALL user-authored/custom skills MUST begin with a leading underscore (`_`) prefix so they sort to the very top of alphabetical listings, IDE pickers, and autocomplete popovers.
  - **Action-First Semantic Naming (`_<action>-<constraint>`)**: Skill names MUST start with the primary action verb, followed by the defining behavioral constraint or modifier (e.g., `_critique-without-ghostwriting`, `_prune-subtractively`).
  - **Workflow & Skill 1:1 Parity Invariant**: ALL custom workflows under `~/.gemini/config/global_workflows/` (e.g. `_plan-with-ai-os`, `_plan-with-subagent`, `_plan-with-gemini`, `fast`, `audit`, `rule`) MUST be co-located as first-class skills in `~/projects/ai-os/skills/<name>/SKILL.md`.
  - **Direct Skill/Workflow Resolution**: When referencing or inspecting any named workflow or skill (e.g. `_plan-with-ai-os`), agents MUST NEVER perform broad filesystem searches or grep sweeps. Agents MUST check the direct paths:
    1. `~/.gemini/config/global_workflows/<name>.md`
    2. `~/projects/ai-os/skills/<name>/SKILL.md` (or `~/.gemini/config/skills/<name>/SKILL.md`)
  - **Auto-Sync Invariant**: After creating or updating any skill under `~/projects/ai-os/skills/`, agents MUST immediately execute `python3 /Users/matt/projects/ai-os/scripts/sync_skills.py` to propagate changes across all local agent runtimes (`~/.gemini`, `~/.claude`, `~/.agents`).

# Zero-Tolerance Secret Isolation & Invariant
- **Strict .env & Secret File Invariant**:
  1. **Never Read Raw Secrets**: Agents MUST NEVER read, inspect, print, or output the raw contents of `.env`, `.env.*`, `*credentials*`, or private key files directly (e.g. NEVER execute terminal or file-viewing tools directly on secret files or dump raw keys to terminal/chat).
  2. **Safe Environment Tooling (`aios-env`)**: When checking whether an environment variable is set or verifying configuration, agents MUST ONLY use safe environment inspection tooling (`aios-env check --key <KEY>` or `aios-env list`), which reports key presence, type, and character length without revealing values.
  3. **Execution-Only Environment Ingestion**: In scripts and runtime commands, environment variables must be loaded directly into process memory (e.g. `dotenv`, `os.environ`, `process.env`) without emitting values to stdout, stderr, or transcript logs.
  4. **Preflight Staged Diff Secret Gate**: All commits must pass preflight secret sanitization. Staging raw secret keys or `.env` files immediately aborts the preflight check.
  5. **Open, Don't Hunt**: When Matt needs to add a key or secret, open the target `.env` in VS Code for him (`code <path>`, without reading it) and name the exact variable to add.
  5. **Vendor Ingestion Secret Sanitization**: When creating projects, forks, or local patches from third-party vendor code, npm packages, or submodules, agents MUST NEVER commit unpacked distributions without running automated secret detection. Agents MUST scan the vendor tree for hardcoded API keys (`AIza...`, `AKIA...`, `sk-...`, `ghp_...`, private keys) and sanitize/redact all vendor dummy or test keys BEFORE git initialization or staging.
  6. **Hard Commit-Blocking Gate in `auto_commit.py`**: `auto_commit.py` automatically runs `SecretAuditHook.audit_git_diff()` before committing. If any raw secret pattern is detected, it immediately executes `git reset`, aborts the commit/push, and exits with a fatal error.

# Model Family Naming Invariant
- **Rule**: Agents MUST ALWAYS refer to AI model families by their clean canonical brand name (e.g. `Sonnet`, `Flash`, `Opus`, `Haiku`, `Gemini`, `GPT`) WITHOUT appending speculative, obsolete, or guessed version numbers (e.g. NEVER say `Claude 3.7 Sonnet`, `Sonnet 3.5`, `Gemini 1.5`, `GPT-4o`). Model versions change rapidly; always use family-only naming.

# Model & API Verification Invariant (Zero Hallucinated Models)
- **Rule**: Agents MUST NEVER trust internal memory or guess model names, model identifiers, version tags, or API engine strings (e.g. TTS voice models, LLM checkpoint names, provider engine strings).
- **Mandatory Pre-Verification**: Before writing, configuring, or hardcoding any model identifier, engine string, or voice name into code, presets, or configurations, agents MUST actively verify the exact string against authoritative documentation, official API endpoints, or official provider playgrounds. Never extrapolate or fabricate model versions or name schemes (e.g. guessing model names without verifying).

# Memory & Recall (QMD)
- **One search over everything**: Matt's Obsidian vault and all past threads (Gemini, Antigravity, Claude Code) are indexed locally by QMD. Search it before saying something isn't known: the `qmd` MCP tools (`query` for meaning-based search, `get` to open a hit), or `qmd search "<words>"` / `qmd query "<question>"` in a shell.
- **Automatic**: A Claude Code hook adds up to 4 related past notes/threads to each prompt, and another keeps the index current (exports Claude transcripts to `private/claude-threads/`). Treat those pointers as hints; open one only if it's relevant.
- **Where durable facts go**: preferences and lessons go in Claude's built-in memory; curated knowledge goes in the Obsidian vault; project facts go in the project's `AG_CONTEXT.md`. Anything written to those is picked up by QMD on the next refresh.

# Personal Knowledge Base & LLM Wiki Invariant
- **Location**: Matt's personal notes vault and LLM Wiki is located at `/Users/matt/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`.
- **Architecture**: Organized per the Karpathy LLM Wiki pattern:
  - `SCHEMA.md`: Domain definition, frontmatter rules, and tag taxonomy.
  - `index.md`: Master catalog of all interlinked notes.
  - `log.md`: Append-only chronological action log.
- **Rule**: Agents MUST NEVER guess or search for alternative wiki directories (e.g. `~/wiki`). All note routing, personal knowledge updates, and wiki operations MUST route directly to this path.

# Anti-Scope-Creep & Habit Sustainability Guardrail (Rabbit-Hole Interceptor)
- **Context**: Matt is a known procrastinator and rabbit-holer who can get drawn into building massive, from-scratch systems or premature redesigns instead of taking atomic, high-leverage actions.
- **Rule**:
  1. **Flag Big From-Scratch Projects**: Whenever Matt proposes creating a large new project from scratch, building custom tools for one-off tasks, or undertaking sweeping architectural rewrites when existing tools, libraries, or narrow fixes suffice:
     - Agents MUST actively intercept and flag the scope creep as a red flag.
     - Proactively offer the fastest, lowest-friction alternative (e.g. cloning an existing repo, adopting an established CLI/library, or taking an atomic incremental step).
  1a. **Look for Existing Tools First (2026-10-20)**: Before designing or building anything (a tool, script, app, automation or integration), FIRST search for existing tools that already do it: built-in macOS/iOS features, apps Matt already has installed (`/Applications`), open-source projects and established libraries. Do this even when Matt doesn't ask, and present what you found (with a recommendation) before proposing a custom build. Why: Matt asked agents to always check, in case he forgets to.
  1d. **Systems Over One-Offs (2026-10-21)**: Matt is a systems guy. When a fix or chore should recur (cleanup, restarts, checks, syncs), offer it as a scheduled system (launchd agent, routine, Hammerspoon timer) rather than only a one-time step, and say which items are one-off. Why: he wants recurring needs handled automatically, not remembered.
  1b. **Save Working Methods (2026-10-20)**: When you work out how to do a task on Matt's Mac (a command, API, script or trick that actually worked), save the working method so the next agent can repeat it fast: a reusable script in `~/projects/ai-os/scripts/` (or the project's own), a `_` skill, or a line in the right memory/`AG_CONTEXT.md`. Before working something out from scratch, check those places for a saved method first. Why: Matt wants repeat tasks to get faster each time, not be re-derived. Example: `scripts/youtube.sh play|pause|status` controls YouTube in Chrome.
  1c. **Same Experience in Claude Code and Project Threads (2026-10-20)**: Claude project threads run as Remote Control sessions on Matt's Mac, so they must give him the same experience as the Code tab: his skills, plugins, mods, hooks, rules, memory and saved working methods. Agents in a project thread act exactly as they would in Code, without Matt having to explain how things are done. Whenever you add or change a skill, mod, hook or rule, check that it also works in a project thread (a message arrives wrapped in a `<wake>` envelope; anything a mod draws in the Code tab, like a band, pane or toast, is not shown on the project page) and give it a project-thread equivalent where possible (a line in the reply, an emoji quick reply, a notification). Tell Matt plainly about anything that truly can't carry over. Why: Matt wants to use projects exclusively without losing what he built for Code.
  2. **Sustainable Marginal Change**: Treat software architecture like habit formation: sweeping, all-or-nothing transformations breed instability, bugs, and burnout. Always advocate for sustainable, marginal, test-driven increments over massive overhauls.
  3. **Call Out Wheel-Spinning**: If an agent observes Matt rabbit-holing into micro-optimizations or theoretical rabbit holes on throwaway tasks, directly and constructively call it out and redirect focus to the primary high-leverage outcome.

# Quizzes & Study Sessions (2026-10-20)
- When Matt asks to be quizzed or to study, follow the `_quiz-with-tap-menus` skill exactly: rounds of 4 questions in the built-in question menu (`AskUserQuestion`, never a widget or artifact, since those don't return his taps), `multiSelect: true` on every question so Other works as his comment channel (answer + empty Other = just guessing (counts as a miss), answer + "e" = too easy, other text = a comment to act on), each option's description left empty (no "Option A" text), right answer in a random position, score plus one line per miss, misses come back later with no giveaway (never put a correction, hint or the answer in the question or menu that tests it; corrections go only in the chat reply). Check for typed messages that arrived while a menu was open before sending the next round.
- Outside quizzes, ask Matt questions in plain text, never in a question menu (tested 2026-10-21: menus always need a separate Submit tap, and while one is open his normal replies and Claude dictation can't reach the agent).
- Emoji quick replies (2026-10-21): Matt may answer by reacting to an agent's message (it wakes the thread). Meanings: 👍 yes / go ahead · ❌ no, don't · ❓ didn't get it, explain simpler · ⏩ next / keep going · ✋ wait, he's typing more (do nothing yet) · ✅ done, all good, wrap up. Treat a reaction on a message that asked something as his answer. When you offer choices, make 👍 the default/recommended action and list it first (Matt, 2026-10-21: e.g. a cold-thread prompt's 👍 = fresh thread from a Haiku handoff).

# Mac Automation: Take-Control Queue ("Air Traffic Control", 2026-10-21)
- Before posting ANY synthetic keyboard, mouse or controller input on Matt's Mac (tests, app switching, pasting, hs.eventtap), get clearance: `~/.hammerspoon/bin/claude-control ask "<what and why>" 3`. It shows the orange banner and waits in a queue behind other agents; only one agent holds control at a time. Exit 0 prints `granted <ticket>`: go. Exit 1 (Esc, preempted, queue timeout): don't touch input.
- **What counts as input (2026-10-21)**: not just keys, clicks and controller events. Anything that changes what's on Matt's screen or what he hears needs the same clearance: opening or revealing files (`open`, `open -R`, Finder reveal), launching or activating apps, focusing or moving windows, media play/pause/skip and volume changes. This holds whether you do it directly (`open`, `osascript`, `hs -c`, computer-use) or through code you built and are now testing: running your own automation to test it is agent input. Why: an agent revealed a file in Finder on Matt's screen without the banner because the old wording only named keyboard/mouse input.
- **Esc vs Stop (2026-10-21)**: exit 1 `cancelled` means Matt pressed Esc ("not now"): don't re-ask on your own; tell him what you need control for and wait for his go. Exit 3 `stopped` means he pressed Stop (Esc twice, or the banner's Stop button): end the WHOLE task at once, don't ask again or try another route to the same input, and report what you were doing and what's left. Stop also blocks your session from asking for 2 hours and interrupts its current turn. Only Matt unblocks (`claude-control unblock <session>`).
- Release your own turn right after with `claude-control done <ticket>` so the next agent goes. Between long input steps, check `claude-control state <ticket>` and stop at once unless it says `granted`.
- `--urgent` jumps the line and preempts a normal holder. Use it ONLY to stop something running away right now (runaway input, a stuck loop hammering the Mac). Never for routine tests.
- **Deterministic automations too**: any automation you build for Matt (Hammerspoon module, Keyboard Maestro macro, script, launchd job) that posts keystrokes or clicks, switches the front app/window, or uses the clipboard MUST take the same queue, without the banner. Hammerspoon: `claudeControl.withInput("<name>", function(release) ... release() end)` (plain `function() ... end` releases itself). Keyboard Maestro / shell: `t=$(~/.hammerspoon/bin/claude-control lock "<name>") || exit 1` first, `claude-control done ${t#granted }` last. Never queue what Matt triggers himself: a key, click or controller press that fires a quick 1-5 step sequence right away is his own input, so it runs immediately. Queue only what runs on its own (timers, watchers, schedules, agents) or holds input for more than a second or two.
- Why: several Claude agents and automations run on Matt's Mac at once; without a queue one can type over another's, even when Matt keeps his hands off.

# Mac HUDs: Spatial Slots ("Air Traffic Control" in space, 2026-10-21)
- Any HUD or floating overlay you build or move on Matt's Mac takes a reserved slot in `~/.hammerspoon/hud_slots.json` (Hammerspoon: `require("modules.hud_layout").rect(id, w, h)`; Swift: read the same JSON like `trackpad-mixer/Sources/Slots.swift`). Never hand-pick a corner. After editing the map run `lua ~/.hammerspoon/tests/hud_layout_test.lua`; it fails on any overlap. Slots never move at runtime, so one HUD resizing never shifts another. Why: the mixer covered the song key pill; overlays from separate apps didn't know about each other.

# Coordinator Routing: What Goes to Which Thread (2026-10-21)
- Applies to the Claude Projects coordinator and any agent handing work to another agent. Full version: `/mnt/project-files/coordinator/routing-rules.md` in the Everything project.
- **Split before routing**: break every message into its separate asks and route each one on its own. Never route a whole message because it mentions a thread.
- **Coordinator-meta stays with the coordinator**: rules, feedback, "from now on", or complaints about how something was handled are never forwarded to a worker thread. A message *about* a thread is not *for* it.
- **Attach Matt's message by id only if ALL of it fits the receiving thread's scope**; otherwise restate the subset in your own words, quoting his exact sentence where his authority matters.
- **Size check before every send**: never make a thread's job bigger than its title. Start new threads on a message that *is* the task, never on a meta message.
- **"Why did you do that?" is a real question**: give the actual cause first, plainly and without defending, then the fix.
- Why: on Oct 21 the coordinator narrowed an over-scoped thread correctly but attached Matt's "catch over-scoped prompts" rule to it, which was the exact mistake that rule describes. It did so out of a reflex to attach the user's message so the instruction carries his authority.

# Voice Tasks: Report Back (2026-10-21)
- Restate complex logic before building (Matt, 2026-10-21): when a request involves multi-state UI or interaction logic that's easy to misread (gestures, modes, modifiers, edge cases), reply first with the logic as you understand it, point by point, plus anything ambiguous, and build only after he confirms (👍).
- When you finish a task that arrived as a "🎙️ Voice task" (from Matt's Claude voice chat), report the result back to voice chat: `python3 ~/projects/ai-os/scripts/voice_reply.py "<task title>" "<one or two sentence result>"`. Voice Claude hears it on its next connector call, so Matt gets the answer mid-call.

# Git Protocol Rules

## Auto-Commit Protocol
- **Git Auto-Pull & Pre-Flight:** Before any agent begins work on an established git project, it MUST run `python3 /Users/matt/projects/ai-os/scripts/preflight.py` to perform all pre-flight routines (evaluating `ag-quota` velocity, auto-pulling/rebasing latest git changes, etc.) in a single step.
- **Auto-Commit & Push:** Whenever an agent concludes work involving code or documentation changes on a git repository, it MUST execute `python3 /Users/matt/projects/ai-os/scripts/auto_commit.py -m "<message>" [--paths <files>]` to stage, commit, and immediately push commits (`git push`) to the remote repository. The agent writes the commit message itself (a specific subject line, plus a short body on *why* when useful); without `-m` the script falls back to a generic "Update <files>" summary. Use `--paths` to commit only this session's files. NEVER leave working tree changes uncommitted or unpushed at task conclusion.
- **Branch Protection & Staging Invariants (Daily Mini-Crossword)**: For `daily-mini-crossword`, all agents and developers MUST work and commit exclusively on the `working` branch. NEVER commit or push directly to `main`. The `main` branch autodeploys to production on Vercel (`crossword.mattmurphy.ca`) and is reserved strictly for official public releases.
- **Always Push, Never Ask (2026-10-20)**: Matt pre-approves every commit and push agents think is right, `main` included. Never hold a commit or push for his approval; commit and push as soon as work is done. Run the secret scan first. Only exception: daily-mini-crossword `main` (see above).
- **Make It Live by Default (2026-10-20)**: When Matt asked for a change and it's tested and very likely working, make it live without waiting (merge it where the live job/app runs from, install it, switch it on), then tell him it is live. Don't ask "want me to undo it?" (Matt, 2026-10-20: he will ask if he wants it undone). Only wait for his approval first when the change is genuinely experimental or likely to fail. Why: a finished change left on a side branch behind an easy-to-miss "should I make it live?" question confused him when the old version kept running. The daily-mini-crossword `main` (public production) rule above still applies.

## Ubiquitous Git Tracking Directive
- **All Code & Configs in Git**: Practically all scripts, tools, configurations, automation modules, dotfiles, and codebases MUST reside inside a Git repository backed by a remote repository (always `--private` by default unless explicitly public).
- **Proactive Untracked File Detection**: Whenever an agent encounters, modifies, or inspects files or scripts that are NOT inside a Git worktree:
  - The agent MUST immediately notify Matt that the files are untracked.
  - The agent MUST assume Matt wants them tracked in a Git repository and either initialize/link a private repo or bring them into an appropriate repository structure.

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
- **Surfacing Requirement**: Agents MUST surface the project board with a standard local Markdown link: `[PROJECT_BOARD.md](/Users/matt/projects/ai-os/PROJECT_BOARD.md)`. Do not append editor- or file-manager-specific launcher URLs; the built-in editor handles local file links.
- **Task Schema**: Always format tasks as `- [ ] <description> [project:: <id>] [assignee:: user|agent] [due:: YYYY-MM-DD]`.
