## Goal
Fix a bug where the TUI displayed "Agent is thinking & working..." even when the agent was idle/waiting for a prompt. Also fix the dark, hardcoded styling of the live stream pane on light mode.

## Changes Made
- Removed the erroneous `if (!isThinking && pauseStatus === 'Running') { isThinking = true; }` block from `src/main.ts`. This was forcing the loading indicator to always show unless the user explicitly paused the agent, which is incorrect since the agent can be running but idle.
- Replaced the inline styling (`style="..."`) for `#live-stream-pane` in `src/main.ts` with a new CSS class `.live-stream-pane`.
- Added the `.live-stream-pane` class to `src/styles.css`, using semantic variables `var(--panel-bg)` and `var(--text-muted)` instead of hardcoded dark rgba and hex colors. This ensures it displays beautifully and appropriately in both light and dark modes.

## What Worked
- Agent thinking state now accurately reflects when the MODEL is actually processing a non-DONE step.
- Live stream pane matches the active theme seamlessly.

## What Didn't Work / Known Issues
None.

## Architecture Notes
The TUI leverages semantic CSS variables from `styles.css`. We should avoid inline hardcoded colors when generating HTML for the TUI to ensure theme continuity.
