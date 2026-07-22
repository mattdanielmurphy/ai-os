## Goal
The user requested removing the custom pseudo-toolbar in favor of enabling real native macOS window decorations (title bar and native stoplight buttons) when transforming the Gemini floating window, and ensuring the window's bottom does not extend off screen.

## User Feedback & Decisions
- Prefer real native macOS window frame decorations over custom HTML controls.
- Dynamic window sizing bounded strictly within visible screen height (`availHeight`).

## Changes Made
- Modified `/Users/matt/projects/ai-os/tauri-gui/src-tauri/src/main.rs`:
  - Removed `#aios-pseudo-toolbar` HTML element creation and custom listeners.
  - Added `appWin.setDecorations(true)` call inside `transformToNormalWebview()` to switch the window to real native macOS window frame decorations.
  - Calculated safe bounds relative to `window.screen.availHeight` (`targetH = Math.min(760, Math.floor(screenH * 0.80))`), ensuring at least 15-20% margin above the Dock and screen bottom.
  - Added `appWin.center()` to place the window cleanly in the middle of the display.
  - Added `window.set_decorations(false)` call inside `Cmd+Option+Space` handler in Rust to reset decorations back to frameless floating input mode when re-triggered.
- Updated `FEATURES.md`.
- Updated `DEVELOPMENT_JOURNAL.md`.

## What Worked
- Clean native macOS titlebar and stoplights rendered by macOS window server.
- Window bounds safely fit within screen dimensions without overflowing off bottom edge.
- `cargo check` built with zero warnings or errors.

## What Didn't Work / Known Issues
- None.
