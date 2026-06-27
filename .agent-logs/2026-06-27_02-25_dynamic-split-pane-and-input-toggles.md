## Goal
Implement dynamic toggle behavior for the split pane: in Prompt Mode, the bottom mini shell and splitter are hidden, showing only the TUI and prompt input textfield. Typing `!` in the input textfield toggles Terminal Mode (hides prompt input, shows splitter and mini terminal shell, and shifts focus to it). Pressing Escape or typing `exit` inside the mini terminal reverts to Prompt Mode. Save this state per project tab.

## Changes Made
- **`index.html`**:
  - Added `id="bottom-input-area"` to the wrapper container of the prompt input and breadcrumbs to ease toggle display actions.
- **`src/main.ts`**:
  - Restructured terminal view logic to toggle Splitter and Mini Terminal visibility dynamically under `applyTerminalModeUI()` based on `isTerminalMode` state.
  - Configured input listener on `textarea` to intercept a single typed `!` and instantly toggle Terminal Mode.
  - Linked `miniTerm.onData` key and command buffers to transition back to Prompt Mode on receiving `Escape` (code `\x1b`) or checking for input commands matching `exit`/`exit()`.
  - Stored `isTerminalMode` state per project tab within `projects` array and updated tab restoring steps.

## What Worked
- Vite production build and Rust cargo checks compiled cleanly.
- Instant toggle transitions feel snappy and focus is routed correctly to the respective inputs.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Hiding the entire bottom input wrapper preserves layout alignment and optimizes vertical workspace space for both modes.
