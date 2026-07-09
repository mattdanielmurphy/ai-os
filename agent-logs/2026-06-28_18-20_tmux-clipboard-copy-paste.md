## Goal
Resolve tmux mouse selection clear issues on release, and enable copy to macOS system pasteboard when dragging to select or typing Cmd+C/Ctrl+C inside the terminal view.

## Changes Made
- **[src-tauri/src/main.rs](file:///Users/matthewmurphy/projects/ai-os/src-tauri/src/main.rs)**:
  - Added tmux key bindings to `MouseDragEnd1Pane` in both `copy-mode` and `copy-mode-vi` to run `copy-pipe-and-cancel "pbcopy"` when a new session is created.
  - Implemented a new Tauri command `copy_tmux_selection` that tells tmux to copy the current active selection in copy-mode to the pasteboard via `pbcopy`.
- **[src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts)**:
  - Updated the frontend `keydown` event listener for `Cmd+C`/`Ctrl+C` to fall back to invoking `copy_tmux_selection` when no native xterm.js selection is present but the user is focused on the terminal container.
- **[FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md)**: Updated capabilities logs.

## What Worked
- Automatically piping the tmux selection to the macOS system pasteboard on mouse release via `copy-pipe-and-cancel "pbcopy"`.
- Programmatic fallback trigger to grab the tmux copy-mode selection when using keyboard shortcuts `Cmd+C` or `Ctrl+C`.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- In tmux, if mouse mode is enabled (`set -g mouse on`), mouse drag events are intercepted by tmux. This creates a yellow tmux-specific selection instead of a standard local xterm.js/window selection.
- Binding `MouseDragEnd1Pane` ensures that mouse-up events pipe the tmux copy buffer directly to `pbcopy` and exit copy mode, providing immediate drag-and-copy.
- Calling `tmux send-keys -X copy-pipe-and-cancel "pbcopy"` programmatically via Tauri allows copying selections made via keyboard-based copy modes.
