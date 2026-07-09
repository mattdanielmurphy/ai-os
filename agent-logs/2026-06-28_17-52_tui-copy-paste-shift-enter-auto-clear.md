## Goal
Fix multi-line Shift+Enter prompts, selection copy/paste support for xterm.js TUI containers, redesign the auto-clear context checkbox to look premium, place it on the left side, make it auto-reactivate after message transmission, hide the cut-off tmux status bar, and disable AGY cost telemetry script executions temporarily.

## Changes Made
- **[index.html](file:///Users/matthewmurphy/projects/ai-os/index.html)**: Relocated and redesigned the auto-clear context container as a premium toggle badge placed on the left side of the bottom panel.
- **[src/styles.css](file:///Users/matthewmurphy/projects/ai-os/src/styles.css)**: Appended `user-select: text` and `-webkit-user-select: text` styles to terminal and xterm screen components to allow standard selections.
- **[src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts)**:
  - Added dedicated keyboard copy listener (`Cmd+C`/`Ctrl+C`) that grabs xterm.js selection (`term.getSelection()` / `miniTerm.getSelection()`) or fallbacks to standard selection and copies to clipboard.
  - Added terminal paste listener to send clipboard contents directly to active PTY when the user pastes while focused on the terminal pane.
  - Explicitly handled Shift+Enter in prompt keydown handler to manually insert `\n` at the cursor position and trigger layout height adjustments.
  - Consolidated duplicate auto-clear hooks and definitions into a single global location.
  - Enabled auto-clear to self-reactivate after each sent message.
  - Added dynamic classes to visually transition the auto-clear badge between `Auto-Clear: ACTIVE` (emerald) and `Auto-Clear: OFF` (dim gray border).
  - Disabled the cost telemetry python execution command hook inside prompt execution.
- **[src-tauri/src/main.rs](file:///Users/matthewmurphy/projects/ai-os/src-tauri/src/main.rs)**: Spawned background thread modifiers on session creation to run `tmux set-option -t <session> status off` to completely hide the cut-off tmux status line from xterm.js views.
- **[FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md)** & **[AG_CONTEXT.md](file:///Users/matthewmurphy/projects/ai-os/AG_CONTEXT.md)**: Updated capabilities logs and architectural status.

## What Worked
- Keyboard-based selection copies (`Cmd+C`) and pastes (`Cmd+V`) inside the xterm.js terminal panel.
- Manual insertion of line breaks during Shift+Enter ensures robust multiline prompts across webview environments.
- Tmux background configuration threads successfully disable the terminal status line.
- Web app successfully compiles under `pnpm build` and Rust backend passes `cargo check`.

## What Didn't Work / Known Issues
- Semicolon-chaining `tmux new-session ... \; set-option ...` inside single command builders failed or didn't apply status changes correctly. Using a spawned Rust thread executing 150ms post-launch resolved this reliably.

## Architecture Notes
- Tauri's macOS webviews require explicit application menus for standard clipboard shortcuts to execute naturally. Writing explicit JS document-level clipboard event intercepts guarantees uniform clipboard functionality without altering the window menu configurations.
- Custom selections inside canvas-rendered terminals like xterm.js do not populate standard DOM `window.getSelection()`, requiring API calls like `term.getSelection()` to extract text content.
