## Goal
Fix the bug where starting a "New Thread" (via the "+" button or by sending a prompt from an empty session) would incorrectly auto-select the previous newest thread instead of waiting for the newly created thread to appear in the sidebar/threads list.

## Changes Made
- **Frontend TypeScript (`src/main.ts`)**:
  - Declared `waitingExistingThreadIds` of type `Set<string>` globally.
  - Modified the "+" (Start New Thread) button click handler to fetch all currently existing thread IDs for the active project and save them to `waitingExistingThreadIds`, while setting `isWaitingForNewThread = true`.
  - Modified the textarea Enter key handler (when starting a new session with no active thread ID) to fetch existing thread IDs and populate `waitingExistingThreadIds` before setting `isWaitingForNewThread = true`.
  - Cleared `waitingExistingThreadIds` when switching projects.
  - Modified the background threads polling loop `pollThreadsList` to ensure that it only auto-selects a thread if the newest thread's ID is *not* found in `waitingExistingThreadIds`. This prevents it from prematurely auto-selecting an old thread before the new session's log file is written to disk by the engine.

## What Worked
- TypeScript compiled successfully using `pnpm tsc --noEmit`.
- Setting `isWaitingForNewThread = true` and querying current thread IDs beforehand successfully isolates the newly spawned thread.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The engine (`agy`) creates the session log file asynchronously. Thus, there is a short latency between initiating a new thread/sending a prompt and the file `transcript.jsonl` appearing on disk. Tracking existing thread IDs allows the frontend to wait reliably for the next new file creation.
