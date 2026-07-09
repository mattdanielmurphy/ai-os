## Goal
Shift from the two-pane side-by-side terminal/preview layout into a unified custom vertical version of the TUI:
1. Top area displays a real-time parsed log viewer displaying what tools the agent is calling, its thinking status, list of edited files, and markdown responses, sourced directly from `transcript.jsonl` of the active thread.
2. Bottom area displays the actual `agy` TUI terminal, which starts in a space-saving collapsed view (64px) showing the terminal input field and expands to full screen upon clicking the divider toggle button.

## Changes Made
- Modified `index.html` to establish the new vertical split-pane layout under `#panes-container`. Deprecated splitters and the mini terminal wrapper, moving them into a hidden section to prevent legacy script errors. Added a `#tui-toggle-bar` element with an action button.
- Updated `src/main.ts` to implement real-time polling of `transcript.jsonl` every 500ms when an active thread is running. Created a `renderCustomTuiLog` timeline parser that maps JSONL steps into:
  - User requests.
  - Active tool call activities (e.g. searching directories, editing files, running commands).
  - Glowing, pulsating "thinking/working" banners.
  - Edited files summaries as clickable visual badges.
  - Proportional, beautiful prose for Assistant markdown responses.
- Registered an event listener for the expand/collapse terminal toggle button (`#toggle-tui-btn`) in `src/main.ts` that toggles heights and hides/shows panels, triggering terminal refitting in real-time.
- Updated `FEATURES.md` and `AG_CONTEXT.md` to document the new features and layout milestones.

## What Worked
- Real-time `transcript.jsonl` polling is extremely fast and robust, successfully parsing JSONL lines and displaying a live feed of tool activities and markdown responses.
- Pulsating thinking animations correctly trigger when the engine is actively executing tasks or when steps remain incomplete.
- The toggle button expands and collapses the terminal container instantly, calling `resizePty` to refit row sizes smoothly.

## What Didn't Work / Known Issues
- None. Build completes perfectly (`tsc && vite build`).
