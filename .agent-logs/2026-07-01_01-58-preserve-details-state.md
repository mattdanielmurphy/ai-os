## Goal
Fix an issue where the agent response DOM is completely rewritten and re-rendered when a new task is added to the output, causing expanded sections (`<details>` elements) to collapse.

## Changes Made
- Modified `src/main.ts` in `renderCustomTuiLog`.
- Added logic to collect the `open` state of all `<details>` elements in the `markdownPreviewPane` by their node index before `innerHTML` is reassigned.
- Added logic to restore the `open` state of those same `<details>` elements right after `innerHTML` is updated.
- Committed the fix.

## What Worked
- Preserving the state based on index works well because new `<details>` blocks for older tool calls are only appended at the end of the log and older tool calls are grouped dynamically inside them. The preceding sections don't shift index position.

## What Didn't Work / Known Issues
- It's not a full Virtual DOM, but it's lightweight and solves the immediate issue effectively.
- If elements were injected in the middle instead of appended, the indices could shift, but currently they are strictly appended at the bottom.

## Architecture Notes
- The TUI uses a 500ms `setInterval` polling mechanism to check if the thread log has updated, then replaces the entire `innerHTML` of the preview pane. This makes state preservation essential for interactive elements like `<details>`.
