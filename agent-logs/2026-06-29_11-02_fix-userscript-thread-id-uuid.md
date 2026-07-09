## Goal
Fix an issue where Gemini context sync threads were still being saved as UUIDs instead of their readable thread names.

## Changes Made
- Modified `/Users/matthewmurphy/projects/userscript-bundler/userscripts/ai-os-context-sync.user.js` to prioritize grabbing the thread title from the `h1` tag before falling back to parsing the UUID from the URL `window.location.pathname`. The previous logic only tried to parse the title if the URL ended with "app" (no thread id in URL), causing existing threads to incorrectly use their URL UUID.

## What Worked
Successfully updated the `getThreadId` function. Now the thread title takes precedence over the URL UUID.

## What Didn't Work / Known Issues
None.

## Architecture Notes
The `ai-os-context-sync.user.js` script in the `ai-os` repo is a symlink pointing to `/Users/matthewmurphy/projects/userscript-bundler/userscripts/ai-os-context-sync.user.js`.
