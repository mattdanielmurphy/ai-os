## Goal
Update the `src/web/index.html` in the `qwerty-midi-hammerspoon` project to dynamically toggle and render keypad visual labels when Shift Mode is activated or deactivated, including applying a CSS class `.shift-active-labels`.

## User Feedback & Decisions
Followed the explicit user instructions to implement a label-swapping mechanism based on the `shiftModeActive` state across `toggleShiftMode`, `assignActionToKey`, `swapKeyBindings`, and layout loading callbacks.

## Changes Made
- Modified `/Users/matt/projects/qwerty-midi-hammerspoon/src/web/index.html` using `precision_edit.py`.
- Added `updateAllKeyLabels()` function to iterate over `currentWorkingLayout` and update `.key-note` texts to either `binding.shiftName`/`shiftAction` or `binding.name` based on `shiftModeActive`.
- Hooked `updateAllKeyLabels()` into `toggleShiftMode()` and `window.onLayoutConfigLoaded()`.
- Updated `assignActionToKey()` to correctly set the active text content immediately if the mode currently matches the `isShift` flag.
- Updated `swapKeyBindings()` and layout snapshot restoration to respect `shiftModeActive` when re-rendering labels.
- Bundled the layout changes into Lua using `bundle_and_reload.sh`.

## What Worked
- Precision edits applied successfully without breaking HTML structure.
- State is properly decoupled from DOM presentation, fetching right from `currentWorkingLayout` or updated in sync.

## What Didn't Work / Known Issues
None.

## Architecture Notes
The `qwerty-midi-hammerspoon` web interface manages its state via a `currentWorkingLayout` object that syncs back and forth with Hammerspoon through a webkit bridge (`window.webkit.messageHandlers.midiControllerUC.postMessage`). State mutations (like swapping) need to update both the DOM and the object.
