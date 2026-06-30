## Goal
Consolidate continued threads under their root thread ID in the sidebar so that continuation steps (turns run in a fresh backend session via `/clear`) do not spawn new separate threads in the UI, and display the entire timeline history stitched together.

## Changes Made
- **[src-tauri/src/main.rs](file:///Users/matthewmurphy/projects/ai-os/src-tauri/src/main.rs)**:
  - Added helper `scan_brain_threads` to read the first 4096 bytes of all threads in `brain/` to parse parent thread ID associations.
  - Added helper `get_root_thread_id` to recursively traverse parent pointers to find the original root thread.
  - Added helper `get_thread_chain` to retrieve and sort (by `mtime` ascending) all segments belonging to a given root thread.
  - Refactored `get_project_threads` and `get_all_agy_threads` to group all project threads by their root thread ID. They now return a single consolidated `ThreadLog` representing the root ID with the title, snippet, and `mtime` of the latest segment in the chain.
  - Updated `read_thread_log` to seamlessly stitch and concatenate the JSONL logs of all chain segments in chronological order when requested.
  - Updated `patch_thread_log_with_output` to write tool patches/outputs to the latest leaf segment of the chain.
- **[FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md)**: Updated features ledger to document the consolidated threads mechanism.

## What Worked
- Chains of continued threads are successfully grouped and represented by their root thread ID.
- Selecting/clicking a thread loaded all segments of the conversation, stitching the full timeline dynamically.
- Sending a message inside a thread correctly appends new inputs/outputs to the latest segment in the chain while preserving the parent linkage.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Each continuation message triggers `/clear` which spawns a new directory with a new UUID on the backend. By linking them with a parent pointer `Continuing conversation from history (Thread ID: <root_id>)`, we form a tree/chain that the Rust backend resolves transparently.
