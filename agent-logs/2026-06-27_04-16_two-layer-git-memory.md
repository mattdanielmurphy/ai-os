## Goal
Build Two-Layer Git Memory tools (B) and use the Context Manager tool to formally inject system constraints into `~/.gemini/GEMINI.md`.

## Changes Made
- Created `scripts/memory_search.sh` to search repository commits using both message (`--grep`) and diff contents (`-S`) and print a bulleted list formatted as `[hash] - message`.
- Created `scripts/memory_diff.sh` to validate the hash using `git cat-file` and print the exact code diff via `git show`.
- Made both scripts executable using `chmod +x`.
- Executed `scripts/append_system_rule.py` commands to enforce system rules for:
  - `global` (deletion ban, memory constraint)
  - `agy` (read constraint, write constraint)
  - `claude` (cost telemetry)
- Updated `FEATURES.md` to document the scripts and rules enforcement.

## What Worked
- Confirmed that `scripts/memory_search.sh` correctly locates commits based on message keywords and content keywords.
- Confirmed that `scripts/memory_diff.sh` successfully validates hashes and outputs git diffs.
- Appended rules correctly into `~/.gemini/GEMINI.md` using the python helper.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The two-layer memory model prevents context window bloat by avoiding massive `git log` dumps, separating overview queries from deep dives.
