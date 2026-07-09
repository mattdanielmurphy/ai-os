## Goal
Fix the project threads list displaying multiple fragmented project iterations (like `ai-os)`) and threads failing to associate with the current `ai-os` project.

## Changes Made
1. **Rust Backend (`src-tauri/src/main.rs`)**:
   - Fixed a character boundary vs. byte indexing bug in `get_project_threads` and `patch_thread_log_with_output` where a byte index position was used directly in `.chars().nth()` (which takes char-level offsets), causing incorrect exact matching on project paths.
   - Updated `detect_project_path` to handle and strip trailing markdown styling and formatting characters (`*`, `` ` ``, parentheses, brackets, commas, colons, etc.) that get appended during transcript references, preventing fragmented project entries like `ai-os)` or `ai-os`.`.
2. **Features Log (`FEATURES.md`)**:
   - Documented the fixes in the features ledger under `[2026-06-30]`.

## What Worked
- Tauri backend compiles cleanly.
- Direct character slicing safely verifies exact boundary matching.
- Stripping formatting suffixes cleans up project pathnames and resolves thread association.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Working on character/string boundary detection must avoid mixing byte indices directly with char positions in Rust. Using substring slices and `.chars().next()` prevents indexing mismatch issues.
