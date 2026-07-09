## Goal
Fix an issue where pressing the Arrow Up key did not recall previously sent commands in the main prompt input.

## Changes Made
- Modified `/Users/matthewmurphy/projects/ai-os/src/main.ts` to implement command history recall for the prompt text area.
- Added a `commandHistory` array and a `historyIndex` pointer to track user inputs.
- Implemented a `keydown` listener for `ArrowUp` and `ArrowDown` that navigates the history array when the user is at the beginning of the text area (`textarea.selectionStart === 0`) or already navigating the history (`historyIndex !== -1`).
- Saved the user's `currentDraft` when they first trigger `ArrowUp` so they don't lose their unsubmitted input.
- Added logic in the `Enter` keydown handler to push `trimmedInput` to `commandHistory` and reset `historyIndex`.

## What Worked
- Confirmed that history can be tracked and recalled successfully using the up and down arrow keys without interfering with multi-line text editing when not at the top line.

## What Didn't Work / Known Issues
- No major known issues.

## Architecture Notes
- The history is maintained in-memory for the duration of the GUI session and is shared across all projects since the array is declared at the module level.
