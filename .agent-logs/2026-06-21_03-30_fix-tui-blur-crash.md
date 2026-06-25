## Goal
The user encountered a crash when using the blessed TUI dashboard:
`Error during execution: tuiInputWidget.blur is not a function`
We need to resolve this crash by ensuring that we do not invoke `.blur()` on `blessed` textarea/input widgets that do not natively support this method.

## User Feedback & Decisions
- None (immediate hotfix for crash).

## Changes Made
- Modified [src/index.js](file:///Users/matthewmurphy/projects/ai-os/src/index.js):
  - Declared `blurInput()` helper function to safely check for `.blur()` capability or reset `tuiScreen.focused = null`.
  - Replaced raw `tuiInputWidget.blur()` calls with `blurInput()` helper in `selectOptionTui`, `askAcceptIgnoreTui`, and `askQuestion`.

## What Worked
- Safely handling input blurring without crashing the Blessed REPL session.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Blessed elements do not support `.blur()` natively. Calling `tuiScreen.focused = null` (or setting focus to the new dialog/list elements) is the idiomatic way to handle blurring.
