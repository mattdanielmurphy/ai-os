## Goal
Implement a feature to allow `Cmd`-clicking links in the TUI terminal interface (like tmux).

## Changes Made
- Installed `@xterm/addon-web-links` package via pnpm.
- Imported `WebLinksAddon` and `@tauri-apps/api/shell`'s `open` in `src/main.ts`.
- Configured a custom `handleLink` function to check for `metaKey` (Cmd) or `ctrlKey` before executing Tauri's `open(uri)` call to launch the default browser.
- Applied `WebLinksAddon` to both the main `term` and `miniTerm` xterm.js instances.
- Updated `FEATURES.md` with the new capability.

## What Worked
- Tauri compilation succeeds with the new xterm addon correctly parsing console URLs into clickable targets when `Cmd` or `Ctrl` is held down, opening them via the native OS shell.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Uses `@tauri-apps/api/shell` `open()` instead of standard DOM `window.open` to ensure cross-platform compatibility and avoid in-app browser hijacks.
