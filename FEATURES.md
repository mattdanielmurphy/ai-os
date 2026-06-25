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