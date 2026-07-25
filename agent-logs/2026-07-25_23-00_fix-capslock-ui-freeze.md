## Goal
Fix the UI freezing and unresponsiveness to keys when Caps Lock is active on macOS.

## User Feedback & Decisions
- User noted that having Caps Lock on causes the application UI to freeze and stop responding to key inputs because modified key events are intercepted/swallowed.

## Changes Made
- Modified `src/init.lua` to include `flags.capslock` in the pass-through condition, ensuring that events with Caps Lock active do not get erroneously swallowed by the macOS eventtap.

## What Worked
- Adding `flags.capslock` to the condition successfully prevented the eventtap from swallowing modified keys when Caps Lock is on, resolving the UI freeze.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- macOS eventtap needs to explicitly account for `flags.capslock` alongside other modifier flags to prevent key interception bugs when Caps Lock is enabled.
