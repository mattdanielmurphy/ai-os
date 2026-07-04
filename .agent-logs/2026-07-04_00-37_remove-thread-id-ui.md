## Goal
Remove the thread IDs (UUIDs) that appear on thread names in the UI.

## Changes Made
- Modified `src/main.ts` to remove the `<span class="thread-id">...</span>` element from the thread list item rendering.
- Modified `src/styles.css` to remove the corresponding `.thread-id` CSS class.

## What Worked
Successfully removed the thread ID from both the HTML template and the CSS.

## What Didn't Work / Known Issues
None.

## Architecture Notes
None.
