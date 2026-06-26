# Features & Operations Ledger

*This ledger tracks confirmed capabilities, implemented features, and resolved structural bugs within the workspace.*

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