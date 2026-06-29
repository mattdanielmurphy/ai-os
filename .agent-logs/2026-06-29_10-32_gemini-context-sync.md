## Goal
Update userscripts and sync backend for Gemini context syncing to save to project root, use proper thread names, deduplicate payloads, and extract markdown formatting along with absolute timestamps.

## Changes Made
- Modified `gemini.js` in `userscript-bundler` to add a `data-timestamp` attribute with the absolute timestamp to the `gm-timestamp` span.
- Modified `ai-os-context-sync.user.js` in `userscript-bundler` to:
  - Deduplicate payloads by caching `window._lastSentContextSync` and aborting if unchanged.
  - Parse `document.title` to generate a sensible `thread_id`.
  - Extract the `data-timestamp` attribute to grab the absolute timestamp.
  - Convert `user-query` and `model-response` HTML content into basic markdown (handling `pre`, `code`, `b`/`strong`, `i`/`em`).
- Modified `src-tauri/src/main.rs` in `ai-os`:
  - Updated `handle_sync` and `handle_gemini_sync` to save to `gemini-history` at the project root instead of `.gemini` inside `src-tauri`.
  - Updated the context sync to save files with a `.md` extension.
  - Added logic to correctly detect the project root if the server is running from inside the `src-tauri` directory.

## What Worked
All changes successfully implemented according to user requirements. I verified file structures and properly utilized the requested logic.

## What Didn't Work / Known Issues
Nothing noted; the system successfully handles these updates.

## Architecture Notes
The `ai-os-context-sync.user.js` makes `window._lastSentContextSync` stateful per page load.
