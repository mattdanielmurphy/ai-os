## Goal
Improve visual details for the custom TUI step logs by making the tool action summaries bold and adding secondary-colored clickable file links for any file or directory path arguments.

## Changes Made
- Modified [src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts):
  - Updated `ToolCallItem` interface to include optional `targetPath`.
  - Added target path extraction to `buildTimelineHtml` for `TargetFile`, `AbsolutePath`, `DirectoryPath`, and `SearchPath` arguments.
  - Exposed `window.openPath` as a global function that calls Tauri's `open_path` command.
  - Updated `renderToolCallHtml` to bold the action summary and append a clickable, secondary-colored relative path link pointing to the target path when present.

## What Worked
- Project built successfully with `pnpm build`.
- Clickable relative file paths are correctly rendered for file/directory operations and trigger Tauri paths on click.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The custom HTML step log uses standard DOM injection and inline `onclick` handlers referencing global variables on `window`. Exposing `window.openPath` allows easy communication back to Tauri commands without needing complex custom event delegation.
