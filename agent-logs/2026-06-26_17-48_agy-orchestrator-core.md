## Goal
Implement terminal layout fixes in `index.html` to prevent bottom row obscuration, register the `agy` orchestrator binary in `package.json`, and implement the orchestration script in `bin/agy` mapping it globally.

## Changes Made
- Modified [index.html](file:///Users/matthewmurphy/projects/ai-os/index.html): Replaced classes of `#terminal-container` with `flex-grow bg-black overflow-hidden min-h-0 relative p-2`.
- Modified [package.json](file:///Users/matthewmurphy/projects/ai-os/package.json): Added `"agy": "./bin/agy"` to the `"bin"` map.
- Created [bin/agy](file:///Users/matthewmurphy/projects/ai-os/bin/agy): The orchestation bash script which formats prompts into JSON for the proxy, calls the proxy on port 4000, and applies the received unified diff.
- Modified [FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md): Added ledger entry for Phase 3: Agy Orchestrator Integration.

## What Worked
- Terminal container styling applied successfully.
- `pnpm link --global .` successfully linked `agy` and `ai-os` system-wide.
- Binary verification confirmed `agy` and `ai-os` paths on system.

## What Didn't Work / Known Issues
- Bare `pnpm link --global` fails on this version of pnpm; `pnpm link --global .` with `--yes` resolved module directory purge issues during CLI invocation.

## Architecture Notes
- The `agy` orchestrator runs locally, calling localhost:4000 (LiteLLM proxy) to request unified diffs from `deepseek/deepseek-coder` and applies them using native `patch`.
