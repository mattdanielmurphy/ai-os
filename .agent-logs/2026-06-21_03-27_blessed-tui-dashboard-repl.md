## Goal
The user requested using a TUI framework instead of building our own CLI input handler from scratch to resolve multiline paste issues and improve REPL interaction.

## User Feedback & Decisions
- User approved the implementation plan to use a TUI framework (`neo-blessed`) and implement full-screen layouts, log redirections, stats sidebar, and paste buffering.

## Changes Made
- Installed `neo-blessed` as a dependency in `package.json`.
- Modified [src/logger.js](file:///Users/matthewmurphy/projects/ai-os/src/logger.js) to support a custom `writer` callback on `GatewayLogger`, sending log statements directly to the TUI chat/log widget.
- Modified [src/index.js](file:///Users/matthewmurphy/projects/ai-os/src/index.js):
  - Created a full-screen `neo-blessed` dashboard layout with a Header bar, left Log pane, right Status & Cost sidebar, and bottom multiline Textarea.
  - Redirected global `console.log`, `console.warn`, and `console.error` methods to output to the TUI Log widget.
  - Enabled **Bracketed Paste Mode** (`\x1b[?2004h`) in the terminal and monkey-patched `process.stdin.emit` to intercept and buffer pasted multi-line text, inserting it as a single block into the input textarea.
  - Replaced standard console-based prompts (`askQuestion`, clarification choices, and audit acceptance) with interactive TUI-native widgets (text inputs, list selectors, and question cards).
  - Hooked keyboard shortcuts: `Enter` to submit, `Shift+Enter`/`Ctrl+Enter` to add newlines, `Up`/`Down` arrows to navigate history when input is single-line, and `Esc` to cancel executing tasks.
- Modified [FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md) to document the new Blessed TUI REPL, bracketed paste mode, and native dialogs.

## What Worked
- High-level layout renders correctly.
- Redirecting global `console` and logger streams works seamlessly.
- Stdin intercept correctly captures bracketed paste sequences and inserts multiline blocks cleanly without premature submission.
- Standard suggestions listing still works perfectly via CLI flags without spawning the TUI.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Using `neo-blessed` creates a cohesive full-screen TUI wrapper while preserving low latency and direct execution fallback capabilities.
- Intercepting the `process.stdin` emit function allows us to selectively capture terminal paste sequences (`\x1b[200~` and `\x1b[201~`) before they reach `blessed`, solving terminal newline pasting constraints cleanly without external library wrappers.
