## Goal
Implement the `dispatch_to_gemini` command to spawn the Gemini UI and inject browser context.

## Changes Made
- Modified `src-tauri/src/main.rs`: Added the `dispatch_to_gemini` Tauri command which takes a prompt and optional `BrowserContext`.
- Used `tauri::WindowBuilder` to spawn a new window pointing to `https://gemini.google.com` if one named "gemini_mode" does not already exist.
- Included an `initialization_script` that sets up a listener for `populate-gemini-prompt` to inject the user's prompt and browser context into Gemini's `rich-textarea` and click the send button.
- Registered the new command in `tauri::generate_handler!`.

## What Worked
- Successfully wired up the dispatch command to open the Gemini UI and execute the JavaScript injection logic.

## What Didn't Work / Known Issues
- None so far.

## Architecture Notes
- The injection script relies on `window.__TAURI__.event.listen` and DOM polling to find the correct `rich-textarea` or `contenteditable` div and the send button since the DOM structure might load asynchronously.
