## Goal
Implement Terminal Output Attachment for the Run Command feature, including adding the backend endpoint, polling loop, and UI. Fix issue with `sudo` hanging.

## User Feedback & Decisions
- The user reported that the terminal output UI was not appearing and `sudo` was silently hanging.
- We discovered that the UI was broken due to a syntax error (`\` escaping backticks in JS string templates) which broke the Tampermonkey script.
- The `sudo` hang was because the detached tmux session couldn't receive user input.
- We added a "Send" input field to the UI to pipe keystrokes directly into tmux.
- We discovered the userscript watcher was dead, so we had to run `node bundler.js` manually to actually compile the `userscripts/gemini.js` into the `userscript_bundle.js`.

## Changes Made
- Modified `gemini-thread-saver-v1.0.1.ts` to add `GET /session-output` (to retrieve tmux pane contents) and `POST /send-input` (to send keystrokes).
- Modified `userscripts/gemini.js` to add the `terminalUi` object, handling UI, polling, and sending input.
- Fixed the JS string template syntax error so the script runs properly.
- Built the new userscript bundle.

## What Worked
- `tmux capture-pane -p -t <session>` successfully gets output.
- `tmux send-keys -t <session> "text" Enter` successfully pipes input.
- DevTools MCP was used to test the actual browser tab and verified the UI appeared, the endpoints returned correctly, and the button interactions worked flawlessly.

## What Didn't Work / Known Issues
- The userscript bundler watcher (`watch-and-bundle.js`) seems to have been terminated and was not compiling changes in the background automatically. Manual compilation is required if the watcher is not restarted.

## Architecture Notes
- The `userscript-bundler` repo compiles scripts in `userscripts/` into a single `userscript_bundle.js`. If you modify a file in `userscripts/`, you must ensure the bundler compiles it before refreshing the browser.
- Tampermonkey will silently fall back to its previous working state (or break) if the newly injected JS bundle contains syntax errors.
