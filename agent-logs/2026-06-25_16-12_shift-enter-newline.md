## Goal
Fix Shift+Enter in the AI-OS terminal app so it inserts a newline in Claude Code (instead of submitting the prompt).

## Changes Made
1. **Created `macOS-app/AI-OS/ClaudeTerminalView.swift`** — New subclass of SwiftTerm's `LocalProcessTerminalView` that overrides `keyDown(with:)` to intercept Shift+Return and send `\n` (0x0a, line feed) instead of the default `\r` (0x0d).
2. **Modified `macOS-app/AI-OS/TerminalViewContainer.swift`** — Changed `makeNSView` return type from `LocalProcessTerminalView` to `ClaudeTerminalView` to use the new subclass.

## What Worked
- Shift+Now sends `\n` (0x0a) to the child process.
- Plain Enter still sends `\r` (0x0d) via the normal SwiftTerm path.
- Only bare Shift (no Ctrl/Opt/Cmd combos) triggers the new behavior.
- No `.pbxproj` changes needed — the project uses `PBXFileSystemSynchronizedRootGroup` which auto-discovers new files.

## What Didn't Work / Known Issues
- N/A

## Architecture Notes
- SwiftTerm's `MacTerminalView` handles `insertNewline:` in `doCommand(by:)` which sends `cmdRet` (`[13]` = `\r`) to the child process.
- Claude Code uses `\r` as "submit" and `\n` as "newline in prompt" — this is standard readline/line discipline behavior.
- The `ClaudeTerminalView` intercepts before `interpretKeyEvents([event])` is called, so the AppKit text system never routes it to `insertNewline:`.
