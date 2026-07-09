## Goal
Fix an issue where pressing `Cmd-K` to open the Action Bar does not move the browser focus to the action bar's input field.

## Changes Made
- Edited `src/ActionBar/ActionBar.ts`. Wrapped the `this.input.focus()` and `this.input.select()` calls inside a `setTimeout` with a 10ms delay in the `open()` method. 

## What Worked
- Deferring the focus logic gives the browser enough time to process the CSS transitions (`visibility: hidden` -> `visibility: visible` and the scale transform) so the input is interactively available when `.focus()` is invoked.

## What Didn't Work / Known Issues
- None so far. The input successfully regains focus.

## Architecture Notes
- The ActionBar overlay uses a `visibility` and `transform` CSS transition rather than `display: none`. This means during the synchronous execution of `classList.add(styles.active)`, the input might technically remain non-focusable until the next paint or frame, making `setTimeout` necessary.
