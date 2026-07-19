## Goal
Get rid of thread-naming debug logs in the GUI app, disable automatic title generation completely (as it was costing money and causing loops), and prevent infinite re-reading/re-parsing loops by caching parsed thread info unconditionally.

## User Feedback & Decisions
None.

## Changes Made
- Modified [main.rs](file:///Users/matt/projects/ai-os/tauri-gui/src-tauri/src/main.rs):
  - Removed `ACTIVE_TITLE_GENERATIONS` and `IN_FLIGHT_TITLE_GENERATIONS` static variables.
  - Removed all `println!("[DEBUG thread-naming] ...")` logs.
  - Deleted the thread-spawning block that called `generate_title.py` to rewrite thread files.
  - Modified the caching block to unconditionally insert the thread info into `THREAD_INFO_CACHE` at the end of the parse run, rather than doing it only when `found_title` is true. This prevents constant file reads/parses for threads lacking a structured title tag.
  - Fixed a 3-tuple destructuring error where `ensure_engine_pty` returns `(u32, bool, u16)` but was destructured as a 2-tuple on line 951.

## What Worked
- Fixed the runaway thread naming loop and log floods.
- `cargo check` runs and compiles cleanly on the Tauri GUI app backend.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- Thread information is cached using a custom `THREAD_INFO_CACHE` keyed by thread ID, validating by `mtime` and `size`. Unconditional caching ensures cache hits are maximized, preventing disk reads on unchanged transcript files.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/568032ff-25fb-4f02-b448-58faea0dab36/.system_generated/logs/transcript.jsonl)