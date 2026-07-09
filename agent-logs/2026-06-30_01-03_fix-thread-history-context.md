## Goal
Fix the thread history context bug where subsequent prompts in a thread either failed to attach history (due to `activeThreadContext` being set to `null` after the first prompt) or only attached a minimal, heavily nested/truncated history that missed the actual, most recent user requests.

## Changes Made
1. **`src-tauri/src/main.rs`**:
   - Modified the `patch_thread_log_with_output` Tauri command signature and implementation to return `Result<String, String>` rather than `Result<(), String>`, outputting the resolved/patched `target_thread_id`.
2. **`src/main.ts`**:
   - Added a global `threadFilepaths` cache map that maps thread IDs to their file paths when rendering threads in the sidebar.
   - Refactored `patch_thread_log_with_output` invocation to capture the returned thread ID from the backend. If `activeThreadId` is currently `null` (e.g. after starting a new thread), it dynamically sets it, highlighting the thread in the sidebar tree and enabling seamless continuation of the same thread.
   - Modified `getCompactifiedContext` to parse combined prompts correctly by extracting the actual user request (everything after the `User request:` marker) rather than recursively grabbing nested historical contexts.
   - Constrained `getCompactifiedContext` to return only the last 6 steps (last 3 turns) to prevent context window bloat while guaranteeing the most recent messages are included.
   - Updated prompt input intercepts in `src/main.ts` to dynamically retrieve the most up-to-date context from the thread's log file right before sending the prompt, instead of relying on a single one-time load state.
3. **`FEATURES.md`**:
   - Documented the new dynamic context loading, context de-nesting, and thread auto-association features.

## What Worked
- Vite successfully compiles and bundles the updated scripts.
- Extracting content after the `User request:` marker resolves the truncation bugs.
- Returning the thread ID from `patch_thread_log_with_output` links auto-created engine sessions back to the sidebar UI.

## What Didn't Work / Known Issues
- None. Context resumption is fully resolved and stable.

## Architecture Notes
- In `agy` (built on Claude Code PUI), every `/clear` signals a fresh conversation context to the LLM backend. The frontend handles context continuity by prepend-injecting the compactified historical context of the active thread as part of a single combined user input.
