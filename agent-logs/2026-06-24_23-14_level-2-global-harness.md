## Goal
Implement the Level 2 global harness architecture: `bin/ai-os` CLI wrapper, `package.json` global binary definition, absolute path routing across all knowledge files, and `pnpm link --global` registration.

## Changes Made
- **`package.json`** (created): Defined `ai-os` as a global CLI tool (`"bin": {"ai-os": "./bin/ai-os"}`), pinned to `pnpm@11.2.2`, `private: true`.
- **`bin/ai-os`** (created): Bash wrapper that exports `$AI_OS_HOME`, captures `pwd`, symlinks `~/CLAUDE.md` if missing when run from `$HOME`, then `exec claude "$@"`.
- **`CLAUDE.md`** (rewritten): Added Section 0 (Global CLI Harness). Replaced all relative paths with absolute paths: `AG_CONTEXT.md` → `/Users/matthewmurphy/projects/ai-os/AG_CONTEXT.md`, `.agent-logs/` → `/Users/matthewmurphy/projects/ai-os/.agent-logs/`, `./tmp/` → `/Users/matthewmurphy/projects/ai-os/tmp/`, `./bin/triage` → `/Users/matthewmurphy/projects/ai-os/bin/triage`.
- **`AG_CONTEXT.md`** (rewritten): Documented Level 2 global harness in Durable Knowledge Map. All paths absolute.
- **`FEATURES.md`** (updated): Added Phase 2 entry detailing triage slicer, CLI wrapper, absolute path routing, global pnpm binary link, and browser state mirror.

## What Worked
- `pnpm link --global .` registered `ai-os` immediately at `/Users/matthewmurphy/Library/pnpm/bin/ai-os` (despite bare `pnpm link --global` failing without a directory arg).
- `which ai-os` resolves and `ai-os --help` delegates to native `claude` transparently.
- The `bin/triage` creation from the previous session step was already executable and correctly positioned.

## What Didn't Work / Known Issues
- `pnpm link --global` without a directory argument fails (`ERR_PNPM_LINK_BAD_PARAMS`). The correct invocation is `pnpm link --global .` — documented in `FEATURES.md`.
- The `ai-os` package does not appear in `pnpm ls --global` output (likely because it's linked from a local path rather than installed from a registry). The symlink exists and resolves correctly despite this display quirk.

## Architecture Notes
- `bin/ai-os` uses `exec claude "$@"` (not subprocess) to hand off PID and signals cleanly to the native Claude Code process.
- The home-directory symlink guardrail only fires when `pwd` equals `$HOME`, preventing accidental symlink creation in subdirectories.
- Using `"packageManager": "pnpm@11.2.2"` in `package.json` enforces pnpm via Corepack (`pnpm@11.2.2` matches the locally installed version).