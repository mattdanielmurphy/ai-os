## Goal
Update `GEMINI.md` to remove custom tool execution constraints (like `qr`, `read_lines`, `memory_search`, `ingest_codebase`) and the `get_last_cost.py` telemetry rule.

## Changes Made
- Modified `/Users/matthewmurphy/.gemini/GEMINI.md`.
- Removed `Quiet Run Wrapper` rule.
- Removed `TOKEN_MANAGEMENT` section (`read_lines`/`grep -n` rules).
- Removed `Memory Constraint` (`memory_search.sh` / `memory_diff.sh`).
- Removed `Read Constraint` (`ingest_codebase`).
- Removed `TELEMETRY RULE` (`get_last_cost.py`).

## What Worked
- Successfully surgically replaced the chunks in `GEMINI.md` to strip out obsolete script constraints.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- We are migrating fully away from forcing the LLM to use custom local scripts for basic tasks. Instead, we use native `zsh` interception to transparently optimize standard shell interactions (like `npm install` and `git commit`), reducing prompt complexity and aligning with natural agent muscle memory.
