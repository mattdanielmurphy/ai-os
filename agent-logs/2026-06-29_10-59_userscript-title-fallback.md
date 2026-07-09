## Goal
Update the Gemini context sync userscript to correctly fall back to using the thread title (from the `h1` tag) when saving threads, and reduce console spam by only triggering the mutation observer on actual node additions (specifically `model-response` or `user-query` elements).

## Changes Made
- Modified `/Users/matthewmurphy/projects/userscript-bundler/userscripts/ai-os-context-sync.user.js` (linked in `userscripts/`) to:
  - Find `h1` containing the thread title and fall back to it inside `getThreadId()`.
  - Rewrite the `MutationObserver` to only trigger if the changed target is within or adds a `model-response` or `user-query` element.
  - Remove unnecessary `console.log` spam.

## What Worked
Successfully updated the userscript with the new logic, minimizing unnecessary `500ms` debounce executions and appropriately resolving the thread title. The changes were committed to the `userscript-bundler` repo.

## What Didn't Work / Known Issues
None.

## Architecture Notes
The userscript in the AI-OS repo is a symlink pointing to `/Users/matthewmurphy/projects/userscript-bundler/userscripts/ai-os-context-sync.user.js`. Thus, modifying the file in `ai-os` actually alters the `userscript-bundler` repo directly.
