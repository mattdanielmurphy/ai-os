## Goal
Modify the behavior of the app so that system instructions are only injected into brand new threads (when auto-clear is enabled), and omitted when continuing a thread (auto-clear is off).

## Changes Made
- `src/main.ts`: Moved the evaluation of `clearCheckbox.checked` (which determines if auto-clear is enabled) above the prompt processing logic.
- `src/main.ts`: Wrapped the system instructions string append (`processedInput += \n\n${systemDirectives}`) in an `if (shouldClear)` block so it only injects when auto-clear is on.

## What Worked
The logic now correctly checks the auto-clear checkbox state and conditionally injects the system instructions only if the user wants a new, cleared context thread.

## What Didn't Work / Known Issues
None.

## Architecture Notes
The `shouldClear` boolean is used seamlessly as it's the exact same toggle that controls `auto-clear` mode from the UI.
