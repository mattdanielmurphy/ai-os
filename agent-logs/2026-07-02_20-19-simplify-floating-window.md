## Goal
Simplify the Spotlight floating window by displaying the `gemini.google.com` homepage directly instead of a custom HTML textarea UI, ensuring the page is preloaded and opens instantly when the hotkey is pressed.

## Changes Made
- Modified `src-tauri/tauri.conf.json` to change the `floating` window's `url` from `/floating.html` to `https://gemini.google.com`.
- Updated the window properties in `tauri.conf.json` to be a standard size (1000x800) and removed the transparent/frameless attributes (`decorations: true`, `transparent: false`, `hiddenTitle: false`) to ensure it behaves as a normal, usable web window rather than an invisible/tiny Spotlight bar.

## What Worked
By keeping the `visible: false` configuration in `tauri.conf.json`, Tauri will automatically create and preload the `gemini.google.com` window in the background when the application launches. When the user presses the `Cmd+Option+Space` global shortcut, it will instantly toggle visibility and bring it to the front without any loading delays.

## What Didn't Work / Known Issues
None so far.

## Architecture Notes
Tauri seamlessly allows replacing a local `url` in `tauri.conf.json` with an external web URL, initializing an external WebView directly at launch while respecting visibility constraints for fast preloading.
