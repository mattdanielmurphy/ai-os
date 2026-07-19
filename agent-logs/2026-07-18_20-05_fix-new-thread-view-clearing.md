## Goal
Fix the new thread view clearing race condition and stuck thinking indicator in active/historic threads.

## User Feedback & Decisions
None.

## Changes Made
- Modified [main.ts](file:///Users/matt/projects/ai-os/tauri-gui/src/main.ts) to fetch current threads before setting `activeThreadId = null` and `isWaitingForNewThread = true`, preventing the 1s thread list polling loop from misidentifying the last existing thread as the new one.
- Reset `lastRenderedThreadId`, `lastRenderedThreadLog`, and `lastRenderedThinking` when starting a new thread or switching projects.
- Passed engine running status (`isRunning`) to `renderCustomTuiLog` so it can force `isThinking = false` when the engine is not actually running.
- Monitored engine running state changes in the active thread polling loop to clean up the thinking indicator immediately on process exit.

## What Worked
- Rebuilt frontend with `bun run build` successfully (unsandboxed).
- Committing changes via housekeeping.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- The 1s thread polling loop was intercepting the new thread state because `isWaitingForNewThread` was set to `true` synchronously while the list of existing threads was still being fetched asynchronously, leaving `waitingExistingThreadIds` empty during that window.
- Checking `is_engine_running` periodically allows the UI to clear the "Agent is thinking & working..." indicator instantly when the engine exits.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity/brain/0b42f81f-c235-4655-b367-6b76585cefe0/.system_generated/logs/transcript.jsonl)
