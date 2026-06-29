# Features & Operations Ledger

*This ledger tracks confirmed capabilities, implemented features, and resolved structural bugs within the workspace.*


### [2026-06-28] Bug Fixes: Engine Run Detection and UI Context Controls
* **Fresh Agent Client Spawning:** Enhanced backend `ensure_engine_pty` and added a new `spawn_fresh_engine` Tauri command to verify if target engine processes (especially `agy`) are actively running inside tmux PTY sessions. If a client is dead or not found, it automatically terminates the stale tmux session and spawns a fresh, clean interactive instance. Updated the frontend prompt handler to dynamically detect missing engine clients and invoke `spawn_fresh_engine` before transmitting prompt inputs.
* **Terminal Layout & UTF-8 Corruption Fix:** Resolved visual artifacts in embedded tmux sessions during vertical scrolling by forcing tmux UTF-8 mode via the `-u` flag, enforcing strict `LANG=en_US.UTF-8` and `LC_ALL=en_US.UTF-8` environment locales, and implementing a trailing byte accumulator in the Rust backend PTY reader to correctly handle multi-byte UTF-8 sequences split across chunks.
* **Debounced Grid Resizing:** Debounced frontend window and dragging splitter resize event callbacks to 50ms, eliminating redundant rapid IPC resize requests to prevent tmux layout desync.
* **Robust Engine Running Detection:** Improved `is_engine_running` and `ensure_engine_pty` in the Rust backend to check tmux session state and direct process state (`kill -0`) instead of relying solely on the process tree of the client process, fixing command routing issues when running inside a tmux session.
* **Auto-Clear (/clear) UI Toggle:** Added an "Auto-Clear (/clear)" toggle checkbox to the bottom input breadcrumbs bar in the UI. Toggling the checkbox persists its state to `localStorage` and dynamically updates the prompt input's placeholder to clearly indicate whether `/clear` will be executed before the prompt is sent, allowing users to easily continue threads.
* **Shift+Enter Multi-line Support:** Explicitly intercepted Shift+Enter in the prompt input to insert a newline and adjust textarea height, bypassing browser focus and webview issues.
* **TUI Text Selection & Copy/Paste:** Added custom event listeners for clipboard copying (`Cmd+C`/`Ctrl+C`) and pasting (`Cmd+V`/`Ctrl+V`) that target xterm.js selections and write directly to PTY standard input.
* **Premium Auto-Clear Toggle UI:** Redesigned the auto-clear context toggle to sit prominently on the left side of the bottom panel with a dynamic, stylized badge indicating active status (`Auto-Clear: ACTIVE` in emerald vs `Auto-Clear: OFF` in gray). Enabled automatic self-reactivation of the toggle after a prompt is sent.
* **PTY Status Bar Removal:** Spawns background tmux status modifiers to disable the bottom status line (`status off`) for newly launched tmux/PTY engine sessions to prevent visual cutoff issues.

### [2026-06-27] Phase 5: GUI-by-Default and Working Directory Workspace Loading
* **PTY Startup Optimization:** Optimized engine PTY startup by launching `claude` and `agy` directly inside the backend tmux/PTY processes, bypassing slow zsh configuration loading (e.g. `nvm`, `.zshrc`) and reducing launch time from 12s to under 2s. Removed frontend startup command injections to prevent command text pollution.
* **GUI-by-Default:** Configured `bin/ai-os` to launch the Tauri GUI app by default when executed.
* **Non-GUI / Terminal Mode:** Added support for `--cli`, `--terminal`, `--no-gui` parameters (as well as direct `--agy` / `--claude`) to bypass the GUI and run the agents directly in the current terminal.
* **Working Directory Passing:** Programmed `bin/ai-os` to capture the invocation directory (`$ORIGINAL_PWD`) and pass it to either:
  - The Tauri GUI app via the `AIOS_INITIAL_PROJECT` environment variable, where the frontend automatically switches to or imports it.
  - The CLI agents (Claude/Agy) by performing `cd "$ORIGINAL_PWD"` prior to command execution.
* **Tauri initial project loader:** Added `get_initial_project` Tauri command in Rust backend and hooked it up in the frontend's initialization lifecycle to seamlessly switch or append the working directory to the workspace project list.

### [2026-06-24] Phase 1: Declarative Guardrails Initialization
* Established project boundaries and `~` directory isolation.
* Enforced absolute `rm` bans and `~/.Trash/` relocation protocols.
* Configured Obsidian `.md` routing to iCloud directory.
* Bootstrapped `AG_CONTEXT.md` and `.agent-logs/` structural constraints.

### [2026-06-24] Phase 3: Background Auto-Commit Protocol
* **Section 7 in CLAUDE.md:** Added "Background Auto-Commit Protocol" requiring immediate background `git add . && git commit -m "[Auto-Commit] ..."` after any file modifications.
* **Visible Terminal Confirmation:** Mandatory `[ai-os] ✓ Changes successfully committed to background log.` printed to terminal after every auto-commit.
* The protocol fires AFTER the user receives the text breakdown of changes — no additional waiting for user instructions is permitted.
* **`bin/triage` Compiler Log Slicer:** Created at `/Users/matthewmurphy/projects/ai-os/bin/triage`. Context-saving wrapper that captures stdout/stderr to temp files, slices on error keywords (error/failed/exception/severe), succeeds with `tail -5`. Shell-escapes `!` characters.
* **`bin/ai-os` CLI Wrapper:** Created at `/Users/matthewmurphy/projects/ai-os/bin/ai-os`. Exports `$AI_OS_HOME` to the absolute project root. Captures `pwd` at invocation. Safety guardrail: when run from `$HOME`, creates `~/CLAUDE.md` symlink if missing. Forwards all arguments to native `claude` via `exec`.
* **Absolute Path Routing:** All knowledge files (`CLAUDE.md`, `AG_CONTEXT.md`, `FEATURES.md`) rewritten to use absolute paths exclusively:
  - Project root: `/Users/matthewmurphy/projects/ai-os`
  - Context verification: `/Users/matthewmurphy/projects/ai-os/AG_CONTEXT.md`
  - Features ledger: `/Users/matthewmurphy/projects/ai-os/FEATURES.md`
  - Agent work logs: `/Users/matthewmurphy/projects/ai-os/.agent-logs/`
  - Scratch sandbox: `/Users/matthewmurphy/projects/ai-os/tmp/`
  - Obsidian vault: `/Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`
* **Global pnpm Binary Link:** `package.json` defines `ai-os` binary → `./bin/ai-os`, `private: true`, `packageManager: pnpm@11.2.2`. Registered system-wide via `pnpm link --global`.
* **`~/.current_web_state.md`:** Browser state mirror created at home directory root, ready for Tampermonkey WebSocket feed.

### [2026-06-24] Phase 4: Native Memory Keyword Override
* **Section 3 in CLAUDE.md:** Added "Keyword Hijack Override (Native Memory Bypass)" guardrail under Knowledge Routing & Context.
* Forces all "my notes" / "personal notes" / "saved notes" queries to bypass Claude Code's native `MEMORY.md` and session memory entirely.
* Routes all note-related lookups exclusively to the iCloud Obsidian vault at `/Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`.

### [2026-06-24] Phase 2.5: Global Home Anchoring & Symlink Architecture
* **4-way home-directory symlink tree established:** All four core project pointers now symlinked from `~/projects/ai-os/` directly into `~`:
  - `~/CLAUDE.md` → `projects/ai-os/CLAUDE.md`
  - `~/AG_CONTEXT.md` → `projects/ai-os/AG_CONTEXT.md`
  - `~/FEATURES.md` → `projects/ai-os/FEATURES.md`
  - `~/.agent-logs` → `projects/ai-os/.agent-logs`
* **AG_CONTEXT.md §Phase Constraints:** "Global Home Anchoring (Level 2.5)" documents that all future config extensions and operational databases must recognize `~` as the active execution anchor so they survive traversal into downstream project subdirectories.
* **CLAUDE.md §0.1:** "Home-Origin Execution Contract" added — defines that the agent may be launched from `$HOME`, must resolve all scaffolding against the canonical project root, and must treat `~` as a valid entry point (not a sandbox violation).

### [2026-06-26] Phase 1 & 2: Tauri PTY Debugging, Global Anchoring, & Engine Toggle
* **Visual Bug Fix (White Box):** Imported `@xterm/xterm/css/xterm.css` directly at the top of `src/main.ts` to solve the Vite bundling issue hiding the xterm textarea helper.
* **Functional Bug Fix (Pty Commands):** Enabled `disableStdin: true` in frontend Terminal config. Wrapped commands with `\r\n` carriage returns to correctly signal command execution to the `zsh` process.
* **Global Home Anchoring Bootloader:** Created `/Users/matthewmurphy/projects/ai-os/bin/ai-os` wrapper script executing the standard home symlink tree (`~/CLAUDE.md`, `~/MEMORY.md`, `~/memory`) before launching `pnpm tauri dev`.
* **Engine Toggle UI & Routing:** Implemented visual switch between `Claude (Native)` and `Agy (Orchestrated)` in `index.html`. Added state management in `src/main.ts` that dynamically prefixes inputs with `agy "[command]"` when routing to the Orchestrator, executing as-is for Claude.

### [2026-06-26] Phase 2: PTY Geometry Sync & Carriage Return Fix
* **Carriage Return Correction:** Changed command execution suffix in `src/main.ts` from `\r\n` to `\r` to prevent PTY duplicate empty prompts.
* **PTY Geometry Synchronization:** Implemented `resize_pty` command in Rust backend (`src-tauri/src/main.rs`) and hooked it up to `FitAddon`'s resize trigger in frontend `src/main.ts` to dynamic adjust `zsh` size, enabling correct terminal scrolling behaviour.

### [2026-06-26] Phase 3: Agy Orchestrator Integration
* **Terminal Layout Fix:** Swapped terminal-container classes to `flex-grow bg-black overflow-hidden min-h-0 relative p-2` in `index.html` to prevent bottom-row obscuration.
* **Agy Binary Registration:** Registered `agy` global binary in `package.json` and ran `pnpm link --global .` to update system mapping.
* **Orchestrator Core Script:** Created the executable `bin/agy` bash orchestrator which routes user prompts to the local OpenRouter proxy (LiteLLM on port 4000) requesting strict unified diffs and applies them surgically using native `patch`.

### [2026-06-26] Phase 4: Context Integration, Cost Telemetry, & Engine Routing
* **Engine Label Update:** Updated `index.html` toggle text to explicitly show `DeepSeek V4 Flash (Claude Code)` and `Agy (Orchestrated)`.
* **Knowledge Routing Hook:** Added automatic inline prompt injection in `src/main.ts` that enforces Obsidian path constraint (`/Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`) whenever the query contains the keyword "notes".
* **Fixed Engine Routing:** Configured `src/main.ts` to route to Claude Code (`claude -p "[prompt]"`) or Orchestrated Agy (`agy --add-dir=$PWD --prompt "[prompt]" --dangerously-skip-permissions`).
* **Cost Telemetry Execution:** Chained the `/Users/matthewmurphy/projects/ai-os/scripts/get_last_cost.py` cost tracking script to PTY executions in `src/main.ts` via zsh sequential execution (`;`).
* **macOS Profiling on Boot:** Updated `bin/ai-os` to automatically generate a static system profile (`memory/macOS_profile.md`) containing SPStorageDataType and active LaunchAgents on app startup.

### [2026-06-27] UI Refactoring & Visual Clipping Fix
* **Engine Toggle Relocation:** Relocated the engine toggle radio button container from above the input textarea to a new slim, compact top header bar (`bg-gray-800`, `text-xs`, border separator) to optimize vertical workspace layout.
* **Terminal Container Padding:** Updated `#terminal-container` Tailwind classes to ensure `min-h-0` is present and added explicit bottom padding (`pb-6`) to prevent xterm.js visual clipping issues at the bottom of the terminal display.
* **Input Area Cleanup:** Cleaned up leftover borders and space in the bottom input area around the `#prompt-input` textarea.

### [2026-06-27] Auto-Expanding Input & Native File Drop Support
* **Auto-Expanding Input Area:** Updated `<textarea id="prompt-input">` in `index.html` to start at 2 lines (`min-h-[3rem]`, `rows="2"`) and dynamically grow up to ~10 lines (`max-h-40`, `overflow-y-auto`) on keystroke input.
* **PTY & Terminal Fit Synchronization:** Connected the textarea's dynamic resize triggers to automatically call `fitAddon.fit()` and sync terminal dimensions to the Rust backend PTY.
* **Native File Drop (Tauri):** Listens to `tauri://file-drop` events, maps over absolute dropped file paths, appends them to the input area separated by spaces, and triggers the input resize calculation automatically.

### [2026-06-27] Prompt Queuing & Auto-Clear Interception
* **PTY Auto-Clear Interception:** Intercepts `Enter` key presses to write `/clear\r` to the PTY, yielding control for a 450ms delay for Claude/Agy CLI context reset before sending the prompt.
* **Bypass Option:** Allows users to submit prompts immediately without clearing context by pressing `Cmd+Enter`, `Ctrl+Enter`, or `Alt+Enter`.

### [2026-06-27] Two-Layer Git Memory Architecture
* **Two-Layer Memory Protocol:** Implemented a token-conservation strategy utilizing commit message and content indexing.
* **Layer 1 (Overview Query):** Implemented `scripts/memory_search.sh` which filters git log message history (`--grep`) and diff contents (`-S`) matching a keyword, formatted as a bulleted list: `[hash] - message`.
* **Layer 2 (Detail Lookup):** Implemented `scripts/memory_diff.sh` which validates the commit hash and outputs the exact commit message and code diff using `git show`.
* **System Rules Enforced:** Used `scripts/append_system_rule.py` to write system rule constraints for Global, Antigravity, and Claude agents into `~/.gemini/GEMINI.md`.

### [2026-06-27] Foreground Process Interception
* **Active CLI Detection:** Added a Rust command `is_engine_running` to check if any active descendant process of the shell PTY matches the target engine.
* **Nested Execution Prevention:** Intercepts prompt submission in `src/main.ts` to check if the target CLI is already active. If so, routes the raw user input directly to the running process's stdin instead of spawning a new nested command.

### [2026-06-27] Sidebar Project Swapping & Terminal Command Mode
* **Left Sidebar for Projects:** Added a left navigation panel in `index.html` mapping active development folders as tab elements. Each project is assigned a distinct color indicator, sorted by recency of focus.
* **PTY Session Multiplexing:** Refactored Rust backend (`src-tauri/src/main.rs`) and typescript frontend to maintain independent cached shell PTY sessions per project folder. Switching between projects instantly resets and restores the corresponding xterm console screen buffer.
* **Terminal Mode Toggle ('!'):** Implemented inline mode switching. Typing `!` at the beginning of the prompt input switches focus to a raw shell wrapper mode (Visual badge status: `Terminal Mode`), bypassing LLM orchestrators and piping user key inputs directly into the active PTY shell instance. Typing `exit` or pressing `Escape` resets input state back to Prompt Mode.
* **Context Thread Resumption:** Displays project-specific startup logs showing current repository history to quickly describe how the developer left off when swapping active tabs.
* **Split Terminal Pane Layout & Tab State Persistence:** Split the workspace screen into two distinct PTY terminal views: a top pane for the interactive Engine TUI (Claude/Agy) and a bottom pane for a Mini Terminal shell. Added a row-resize handler between the TUI and Mini Terminal views, allowing fluid resizing of the panes with automatic fit alignment and geometry synchronization to the underlying Rust PTY processes. Updated tab swapping to persist and restore the selected Engine (Claude/Agy), current prompt drafts, and separate scrollback history caches for both the Engine TUI and Mini Terminal instances when switching between projects.

### [2026-06-27] Phase 2: System Instructions & Orchestration Tools
* **System Rules Append Script:** Implemented `scripts/append_system_rule.py` to programmatically insert rules into `~/.gemini/GEMINI.md` under global or agent-specific headers (`### GLOBAL RULES`, `### ANTIGRAVITY (PREMIUM) RULES`, `### CLAUDE (ECONOMY) RULES`).
* **Ingest Codebase Tool:** Ensured `scripts/ingest_codebase` is properly registered and executable, skeletonizing code structures to minimize tokens.
* **Mechanical Editor:** Implemented `scripts/mechanical_editor.py` to automate unified `.patch` execution with deepseek model via LiteLLM proxy, with a fallback programmatic JSON search-and-replace mechanism if patching fails.

### [2026-06-27] Phase 5: Context Architecture Cleanup & Routing Fixes
* **Context Manager Routing Update:** Updated `scripts/append_system_rule.py` to support multi-file target routing: `--agent global` writes rules to both `~/.gemini/GEMINI.md` and `CLAUDE.md`, `--agent agy` writes to `~/.gemini/GEMINI.md` under `### ANTIGRAVITY (PREMIUM) RULES`, and `--agent claude` writes to `CLAUDE.md` under `## CLAUDE-SPECIFIC RULES`.
* **Rules Ledger Cleanup:** Cleaned up `~/.gemini/GEMINI.md` by stripping out Claude-specific rules and established a clean, dedicated `/Users/matthewmurphy/projects/ai-os/CLAUDE.md` containing global rules and Claude-specific cost telemetry guidelines.
* **PTY Terminal `rm` Hook:** Created `.zshrc_aios` and `.zshrc` in the project root to intercept the `rm` command, redirecting users to use `mv <file> ~/.Trash/` instead, and exported `ZDOTDIR` in the bootloader `bin/ai-os` to load these custom hooks.
* **Advanced macOS Profiling:** Enhanced the system profiling in the `bin/ai-os` bootloader to collect connected display specifications (`system_profiler SPDisplaysDataType`) and active Hammerspoon configuration entries (`~/.hammerspoon/init.lua`) into the generated `memory/macOS_profile.md` log.

### [2026-06-27] Phase 6: Accurate Telemetry, Quota Tracking, & Sub-Model Costing
* **Centralized Telemetry Database:** Implemented `scripts/telemetry_db.py` to record sub-model LiteLLM calls (with prompt/completion token details and DeepSeek-based pricing calculations) and track `agy` execution turns in a local database `~/.ai-os-telemetry.json`.
* **Orchestrator Cost Interception:** Modified `scripts/mechanical_editor.py` to intercept the `usage` block from the LiteLLM API response and log metrics to `telemetry_db.py` on success.
* **Smart Cost & Quota Reporter:** Rewrote `scripts/get_last_cost.py` to support `--agent claude` and `--agent agy` flags, outputting sub-model metrics for Claude, and logging turns while tracking rolling turn limits (50 turns/5hr and 200 turns/weekly) for Agy.
* **System Telemetry Rules:** Injected new agent rules using `append_system_rule.py` to require Agy and Claude to run `get_last_cost.py` at the end of every turn.

### [2026-06-27] Phase 8: Real-Time Quota Telemetry (Source of Truth)
* **Real-Time Quota API Integration:** Rewrote `scripts/get_last_cost.py` to fetch active Antigravity quotas directly from the internal gRPC endpoint (`https://daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota`) on `daily-cloudcode-pa.googleapis.com`.
* **Automated OAuth Token Refresh:** Implemented a robust token refresh mechanism using client ID `1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com` and client secret `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`. When the local token in `~/.gemini/antigravity-cli/antigravity-oauth-token` is expired or close to expiry, the script programmatically requests a refresh and persists the updated token back to disk.
* **Accurate Percentage Outputs:** Replaced the naive turn-counter approximation with actual server-side quota fractions. Formats remaining 5-hour and weekly quotas as real percentages (e.g. `81% (Real)` and `80% (Real)`) based on `gemini-2.5-pro` and `gemini-2.5-flash` bucket statuses.

### [2026-06-27] Phase 7: Mechanical Editor Silent Hang Fixes
* **Fix Subprocess Hang:** Passed `--batch` and `-f` flags to `subprocess.run` executing the Unix `patch` command to prevent user interaction prompt hangs and ensure fast failure.
* **API Request Timeouts:** Added a strict 60-second timeout to the `urllib.request.urlopen` call executing LLM requests to LiteLLM, preventing indefinite hangs on network dropouts.
* **Verbose Progress Logging:** Added immediate unbuffered `stdout` print statements logging key steps (reading file, requesting patch, attempting patch, falling back to substitutions) to keep users and agents fully informed.
* **Robust JSON Fallback & Prompts:** Strengthened instructions inside the fallback prompt to forbid markdown formatting or code blocks in JSON outputs. Updated fallback parser to dynamically support both direct JSON arrays and dictionary objects wrapping the `substitutions` list.

### [2026-06-27] Phases 9 & 10: Loop Prevention, Fast-Path Editing, & Automated Handoff
* **Loop Prevention Rule Update:** Replaced cost telemetry rules in `GEMINI.md` and `CLAUDE.md` to prevent internal telemetry command execution during tool polling and wait cycles, executing only when yielding control back to the user.
* **Precision Editor (`scripts/precision_edit.py`):** Created a robust, LLM-free direct file editing script supporting `replace`, `append`, and `insert_after_string` modes with strict error checking (fails if target matches 0 or >1 times in replace/insert modes).
* **Automated Context Handoff (`scripts/context_handoff.py`):** Built state handoff logging to create standardized context files in `.agent-logs/` and updated `GEMINI.md` system rules to allow spawning a fresh child `agy` process to resume work and prevent context window bloat.
* **Indexed Memory Architecture:** Upgraded context handoff system to separate succinct high-level summaries from granular details using `.agent-logs/details/step_<timestamp_or_id>.md` references, preventing handoff context bloat.
\n### [2026-06-27] Add Project Flow & Interactive Modal Dialog\n* **Add Project Flow Modal:** Created a beautiful, modern, dark-themed, glassmorphic interactive HTML modal that prompts the user to either open an existing folder or start a new project when clicking the '+' sidebar button.\n* **Open Existing Finder Dialog:** Created `select_directory` command in Rust backend integrating `tauri::api::dialog::blocking::FileDialogBuilder` to prompt macOS native Finder folder selector and import existing codebases.\n* **Start New Git & GitHub Repository:** Implemented `create_new_project` command in Rust backend that automatically structures new projects in `~/projects/<name>`, initializes a local git repository with an initial commit, creates a private GitHub repository using the `gh` CLI tool, and links the local and remote repositories.\n* **Git Repo Name Auto-generation:** Added real-time kebab-case transformation in the frontend project creation form to automatically propose a compliant git repository name based on the entered human-readable project name.\n
### [2026-06-27] Telemetry Hallucination Prevention
* **Telemetry Output Enforcement:** Modified `get_last_cost.py` to output the exact telemetry blocks matching `[AGY TELEMETRY]` with three terminating asterisks.
* **Strict Telemetry Instruction:** Updated global `GEMINI.md` system guidelines to strictly forbid manual hallucination of telemetry or quota numbers, forcing agents to call the script directly.

### [2026-06-27] Dynamic DeepSeek Delegation Toggle
* **Dynamic Toggle in `.zshrc_aios`:** Added `AIOS_DELEGATE` environment variable and `delegate_on`/`delegate_off` aliases.
* **Triage Editing System Rule Update:** Integrated rules checking delegation state (`echo $AIOS_DELEGATE`) in both `~/.gemini/GEMINI.md` and `/Users/matthewmurphy/projects/ai-os/CLAUDE.md`. Under Scenario A (delegate=true), agents delegate to `mechanical_editor.py`; under Scenario B (delegate=false), agents use Quoted Heredoc safely (with single quotes around `'EOF_SAFE'`) to directly write code files.

### [2026-06-27] Token-Saving Quiet Run wrapper
* **`qr` (Quiet Run) wrapper:** Added `qr` helper function to `~/.zshrc_aios` and `/Users/matthewmurphy/projects/ai-os/.zshrc_aios`. Pipes command stdout/stderr to `/tmp/aios_last_cmd.log`, outputting a compact success message on status 0, or printing the last 20 log lines on failure.
* **Instruction Rule Injected:** Added a system rule in `~/.gemini/GEMINI.md` instructing the agent to prefix noisy commands (like `pnpm install`, `pip install`, `cargo build`) with `qr` to avoid PTY token window bloat.
### [2026-06-27] Windowed File Reader
* **`read_lines` windowed file reader:** Added `read_lines` function to `~/.zshrc_aios` which takes a file path, start line, and end line, outputting only those lines prefixed with actual line numbers using `sed` to save tokens.
* **Token Management Section:** Added token management rule to `~/.gemini/GEMINI.md` forbidding `cat` for files larger than 100 lines and requiring `read_lines` or `grep -n` for surgical inspections.

### [2026-06-27] Default CLI Wrapper Mode & CLI Development Script
* **Default CLI execution:** Modified the global `bin/ai-os` wrapper to default to the native CLI terminal agent (`exec claude "$@"`) rather than Tauri GUI. Added a `--gui` flag to explicitly launch the Tauri GUI.
* **`pnpm cli` development command:** Registered a new `"cli": "./bin/ai-os --cli"` script in `package.json` to allow developers to run the terminal-based agent directly via `pnpm cli`.

### [2026-06-27] Default Agy CLI, Intercepted Help, and Parallelized PTYs
* **Default Agy CLI:** Modified the `ai-os` global wrapper to default to the Orchestrated `agy` CLI agent instead of Claude. Supports `--claude` flag to explicitly request Claude.
* **Intercepted `--help`:** Captured `-h` and `--help` flags in `bin/ai-os` to display custom CLI help text for `ai-os` itself, preventing it from forwarding to sub-agents.
* **Parallelized PTY Spawning:** Refactored Tauri Rust backend `switch_active_project` to concurrently spawn the mini-terminal PTY and active engine PTY in separate OS threads, cutting startup/tab loading latency in half. Cached `is_tmux_available` check via `OnceLock`.
