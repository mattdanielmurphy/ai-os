## Goal
Map Cmd-N to start a new thread and automatically focus the prompt entry textarea so the user can begin typing immediately.

## Changes Made
- Added a global `keydown` event listener in `src/main.ts` that intercepts `Cmd+N` (metaKey + 'n'). It programmatically simulates a click on the `.new-thread-btn` associated with the active project in the sidebar.
- Modified the `.new-thread-btn` click event handler to call `textarea?.focus()` at the end, ensuring that regardless of how the new thread is created (click or shortcut), the textarea becomes focused.

## What Worked
The shortcut triggers the existing robust new thread flow. Focusing the textarea works efficiently and seamlessly.

## What Didn't Work / Known Issues
N/A

## Architecture Notes
- The `.new-thread-btn` only exists for the currently `isActive` project in the sidebar DOM structure, meaning `document.querySelector('.new-thread-btn')` reliably fetches the correct button for the active project.
