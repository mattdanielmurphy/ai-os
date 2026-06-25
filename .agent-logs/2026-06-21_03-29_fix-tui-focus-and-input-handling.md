## Goal
Fix TUI issue where user was unable to select options in the Clarification Option Select modal because the prompt input textarea retained keyboard focus and consumed inputs.

## User Feedback & Decisions
- User reported being unable to respond to a question.

## Changes Made
- Modified [src/index.js](file:///Users/matthewmurphy/projects/ai-os/src/index.js):
  - Added logic in `selectOptionTui`, `askAcceptIgnoreTui`, and `askQuestion` (TUI branch) to call `tuiInputWidget.blur()` upon opening a prompt to release input grab.
  - Added logic to restore focus with `tuiInputWidget.focus()` upon closing the prompt widgets.
  - Enhanced `selectOptionTui` list selection handler to listen for numeric keypresses ('1'-'9') and automatically select the corresponding option to match natural user behavior when typing selection numbers.

## What Worked
- Releasing focus prevents the prompt textbox from capturing keyboard inputs while option selections or other interactive prompts are on screen.
- Adding direct numeric hotkeys allows users to select list items by pressing their corresponding keys.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- In `neo-blessed`, textareas with `inputOnFocus: true` must be explicitly blurred to allow child list elements and other interactive prompt boxes to receive key events.
