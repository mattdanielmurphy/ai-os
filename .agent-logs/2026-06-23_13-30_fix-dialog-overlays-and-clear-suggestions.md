## Goal
Fix the TUI dialog overlay text jumbling/overlapping bug and resolve the entire backlog of pending suggestions.

## Changes Made
- `src/index.js`:
  - Replaced the buggy built-in `blessed.question` dialog in `askAcceptIgnoreTui` with a custom `blessed.box` layout.
  - Dynamically calculates the dialogue heights based on text lines to prevent overlap.
  - Separates the text message and interactive buttons (`[Okay]`, `[Cancel]`) into distinct positioned children.
  - Supports keyboard shortcuts (`y`, `n`, `a`, `i`, `enter`, `escape`) and direct mouse clicks on buttons.
  - Automatically targets/focuses the `[Okay]` button upon opening.
- `~/.ai-os/suggestions.json`:
  - Marked all remaining `pending` suggestions (ID 4 through 13) as `resolved` since their recommendations (such as path declarations, link constraints, and rulebook updates) are already applied.

## What Worked
- Custom Blessed elements layout dynamically maps text sizing and keeps button actions aligned without overlapping characters.
- Resolving the suggestion backlog prevents repeated prompts for already-applied changes.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Custom dialogue boxes are much more stable and visually clean than standard Blessed widgets for dynamic, multi-line diagnostic rules and inputs.
