## Goal
Fix visual flickering in the sidebar thread list where threads disappear and reappear, and reduce unnecessary sidebar re-renders during background polling.

## Changes Made
- **[src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts)**:
  - Updated `renderProjectThreads` to accept an optional `preFetchedThreads` array to prevent executing a duplicate `get_project_threads` IPC request.
  - Deferred clearing the thread list container (`listEl.innerHTML = ''`) until after the threads have been successfully loaded, eliminating the blank layout gap during the async IPC wait.
  - Modified `pollThreadsList` to supply the pre-fetched threads directly to `renderProjectThreads` when changes are detected.
- **[src-tauri/src/main.rs](file:///Users/matthewmurphy/projects/ai-os/src-tauri/src/main.rs)**:
  - Updated sorting logic in `get_project_threads` and `get_all_agy_threads` to sort by `mtime` descending and then fallback to alphabetical sorting by `id` ascending. This ensures the output vector is completely deterministic.
  - Refactored sorting of thread chain `members` to use a deterministic sort using both their `mtime` and `id`.
- **[FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md)**: Updated features ledger to document the sidebar thread list rendering optimizations.

## What Worked
- Threads list order is now stable and deterministic, matching accurately on stringified comparisons.
- Redundant calls to `get_project_threads` are eliminated during polling transitions.
- The sidebar threads list swaps and updates seamlessly without any visible flickering or empty gaps.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Directory operations via `std::fs::read_dir` return nodes in an arbitrary filesystem-defined order. Because Rust's `HashMap` has a randomized seed, traversing `groups` (which was grouped by root thread ID) yielded randomized sequences of threads. Combined with standard sorting which is stable, threads with matching `mtimes` (e.g. `0`) would frequently swap positions, causing `JSON.stringify` comparison mismatch and triggering a redraw of the entire list container every second. Enforcing a fallback deterministic key (`id`) fully stabilizes the JSON output.
