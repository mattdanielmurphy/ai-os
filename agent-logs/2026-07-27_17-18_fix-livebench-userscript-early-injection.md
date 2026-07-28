# LiveBench Userscript Early Injection Fix

## Problem
The LiveBench userscript (`livebench-frontier.js`) was failing to execute because it ran too early. The script attempted to configure a `MutationObserver` on `document.body` directly. When injected at the beginning of document loading, `document.body` was `null`, leading to a `TypeError` and stopping the script from running.

## Fix
1. Updated metadata header to explicitly specify `@run-at document-idle`.
2. Modified the MutationObserver targets to fall back to `document.documentElement` (which is always defined immediately) if `document.body` is not yet available.
3. Wrapped the observer startup inside a self-retrying `startObserver()` function to handle edge cases where elements are not yet initialized.

## Files Modified
- [livebench-frontier.js](file:///Users/matt/projects/ai-os/userscripts/livebench-frontier.js)
