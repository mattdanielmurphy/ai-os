## Goal
Implement missing features:
- shift+enter should add a newline (and not submit!)
- esc should cancel the current execution and show the last sent message
- entire history of all threads should be saved
- entire history of all user prompts should be saved; when you press arrow-up in a brand new thread it should pull the last prompt

## User Feedback & Decisions
- User approved the implementation plan to build a custom raw-mode multiline command editor in the Node.js readline/keypress context.

## Changes Made
- Modified [src/circuitBreaker.js](file:///Users/matthewmurphy/projects/ai-os/src/circuitBreaker.js) to track and kill active child processes on cancellation.
- Modified [src/ptyWrapper.js](file:///Users/matthewmurphy/projects/ai-os/src/ptyWrapper.js) to add `cancelCurrentTask` method to WarmPtySession.
- Modified [src/index.js](file:///Users/matthewmurphy/projects/ai-os/src/index.js) to:
  - Add thread history saving to `~/.ai-os/threads/thread_[timestamp].json` and global prompt history to `~/.ai-os/prompt_history.json`.
  - Pass the AbortSignal to standard fetch call in `callGemini`.
  - Replace the default readline `startRepl` loop with a custom raw mode multiline command reader.
  - Listen for keypress events to support `Shift+Enter` for multiline input and `Esc` to cancel execution, print the last message, and resume cleanly.
  - Temporarily disable raw mode keypress handling during interactive nested prompts (like clarification and audit decisions).

## What Worked
- Custom raw mode command editor renders correctly and supports backspace, left/right movement, history up/down, and Shift+Enter.
- `Esc` key cancels the executing prompt via `AbortSignal`, kills active processes, cancels warm PTY session task, and prints the last query.
- Saved prompts and thread files write successfully under `~/.ai-os`.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- Using Node's standard `readline.emitKeypressEvents` coupled with `process.stdin.setRawMode(true)` allowed building a custom line editor without third-party dependencies, keeping it extremely light.
