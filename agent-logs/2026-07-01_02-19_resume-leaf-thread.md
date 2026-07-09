## Goal
Fix a bug where clicking a thread in the TUI resumed the root thread instead of the latest leaf thread (the one most recently in progress).

## Changes Made
- Updated `src/main.ts` to include `latest_leaf_id` on the `ThreadLog` interface.
- Created a global `threadLatestLeafIds` map that is populated when `renderProjectThreads` fetches the threads list.
- Changed the resume behavior in `renderProjectThreads` (clicking a thread) to invoke `/resume ${thread.latest_leaf_id}` instead of `/resume ${thread.id}`.
- Changed the active thread re-init behavior (on engine switch or fresh spawn) to query `threadLatestLeafIds.get(activeThreadId)` and resume that `leafId` instead of the root `activeThreadId`.

## What Worked
- Replaced instances of resuming the root thread ID with resuming its latest leaf thread ID.

## What Didn't Work / Known Issues
- N/A
