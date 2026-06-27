## Goal
Replace prompt-mode terminal mode with a dedicated, resizable, scrollable mini terminal pane. Persist and restore tab-specific settings and UI elements (engine setting, text terminal history, text drafts) when switching projects/tabs.

## Changes Made
- **`src-tauri/src/main.rs`**:
  - Refactored `ProjectSession` to support two distinct PTY shells: `engine` (for the TUI engine) and `mini` (for the mini terminal shell).
  - Created a helper `spawn_single_pty` to avoid duplicate code.
  - Refactored Tauri commands `write_to_pty` and `resize_pty` to accept a `terminal_type` argument (`"engine"` or `"mini"`) and route process control calls to the correct channels.
- **`index.html`**:
  - Replaced the single `#terminal-container` area with a `#panes-container` split into `#terminal-container` (Engine TUI), `#pane-splitter` (resize divider), and `#mini-terminal-container` (Mini Terminal shell).
  - Removed obsolete `#mode-badge` elements and updated placeholders.
- **`src/main.ts`**:
  - Initialized two independent xterm.js terminals (`term` and `miniTerm`).
  - Added drag-resizing mouse event listeners to `#pane-splitter` to resize the mini terminal pane dynamically and synchronize dimensions.
  - Added tab-specific state persistence tracking (`engine` selection and `promptDraft` input) in `Project` interface.
  - Updated `switchToProject` to save the active draft/engine setting, and reload/restore them, including separate screen buffer histories for both terminals.
- **`src/styles.css`**:
  - Added CSS rules for terminal containers, viewport overflow, and proper height scaling.
- **`FEATURES.md`**:
  - Appended features ledger documentation for split terminal layout and tab state persistence.

## What Worked
- Tauri compilation and cargo check succeeded.
- Dual-terminal output routing via backend `Payload` `terminal_type` works cleanly.
- Mouse event drag-resizing controls resize both PTY layers synchronously.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Using distinct tmux sessions `ai_os_mini_*` preserves mini shell states across app reload cycles.
