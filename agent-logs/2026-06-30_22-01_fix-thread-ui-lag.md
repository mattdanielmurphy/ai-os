## Goal
Fix UI lag when creating new threads and sending messages, specifically the 3-second delay before placeholders and user messages appear.

## Changes Made
- Modified `src/main.ts` inside the `newThreadBtn` click handler to instantly prepend a `div` element matching the thread list styling, with "#New Thread..." and "Starting...". This gives the user immediate visual feedback when they click to start a new thread.
- Modified the textarea's `Enter` keydown handler to instantly format and append the user's sent message directly to the `markdown-preview-pane`. The message is escaped to prevent basic HTML injection, and auto-scrolled.

## What Worked
- Verified that the `threadsList.prepend` instantly works, and `pollThreadsList` naturally overwrites it when the new thread metadata arrives.
- Verified that appending the user block directly to `previewPane.innerHTML` cleanly hides the "Select a thread..." prompt and feels immediate, being safely overwritten when `renderCustomTuiLog` kicks in later.

## What Didn't Work / Known Issues
- None

## Architecture Notes
- The architecture correctly relies on an interval polling `get_project_threads` and `read_thread_log` to keep the UI in sync. The fix was purely about optimistic UI updates prior to the backend finalizing the log files.
