## Goal
Fix visual/functional bugs in PTY terminal bridge (Phase 1) and implement Phase 2 (Global Anchoring Bootloader & Engine Toggle routing).

## Changes Made
* `src/main.ts`:
  * Imported `@xterm/xterm/css/xterm.css` at the top of the file to fix xterm helper text textarea box showing up.
  * Ensured `disableStdin: true` is configured in xterm `Terminal` options.
  * Added State management for toggling between `claude` (Native) and `agy` (Orchestrated).
  * Added click event listeners for `engine-claude` and `engine-agy` buttons.
  * Modified keydown prompt listener to route commands correctly based on the toggle. If `claude`, it's sent raw. If `agy`, it is escaped and wrapped as `agy "[prompt]"\r\n`.
  * Changed the command terminator from `\n` to `\r\n` to ensure command execution triggers properly in `zsh`.
* `index.html`:
  * Added control bar layout for Engine selection with styled Tailwind buttons for "Claude (Native)" and "Agy (Orchestrated)" right above the `<textarea>`.
* `bin/ai-os`:
  * Created the bootloader script. Sets up absolute path anchoring `AI_OS_HOME="/Users/matthewmurphy/projects/ai-os"`, runs the symlink guardrails for home directory (`~/CLAUDE.md`, `~/MEMORY.md`, `~/memory`), and boots the application dev server via `pnpm tauri dev`.
* `FEATURES.md`:
  * Appended Phase 1 & 2 details to the features and operations ledger.

## What Worked
* Vite builds successfully. CSS styles are compiled properly.
* Input routing correctly checks selection and formats string before calling PTY.

## What Didn't Work / Known Issues
* None observed. Ready for verification of the Tauri dev setup with the new configuration.
