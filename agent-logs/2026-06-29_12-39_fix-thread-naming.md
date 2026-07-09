## Goal
Update the Gemini Context Sync userscript's thread naming logic so it extracts the real thread names rather than defaulting to random values or URL IDs.

## Changes Made
- Modified `/Users/matthewmurphy/projects/ai-os/userscripts/ai-os-context-sync.user.js` to replace the old `getThreadId()` implementation with one provided by the user.
- The new implementation prioritizes extracting the name from `document.title`, followed by the active sidebar item, then the first user message, before falling back to the URL or a random string.

## What Worked
- Replaced the implementation successfully.

## What Didn't Work / Known Issues
- None so far. Wait to see if the new logic fully resolves the naming issue in Gemini.

## Architecture Notes
- The userscript now relies on the `document.title` and `aria-current="page"` selector to robustly grab context names that Gemini assigns.
