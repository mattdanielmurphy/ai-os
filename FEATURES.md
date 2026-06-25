# Features & Operations Ledger

*This ledger tracks confirmed capabilities, implemented features, and resolved structural bugs within the workspace.*

### [2026-06-24] Phase 1: Declarative Guardrails Initialization
* Established project boundaries and `~` directory isolation.
* Enforced absolute `rm` bans and `~/.Trash/` relocation protocols.
* Configured Obsidian `.md` routing to iCloud directory.
* Bootstrapped `AG_CONTEXT.md` and `.agent-logs/` structural constraints.

### [2026-06-24] Phase 2: Level 2 Global Harness Architecture
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