## Goal
Allow running the non-tauri CLI version of the app in the terminal by default or easily without automatically launching the Tauri GUI interface.

## Changes Made
- **`bin/ai-os`**: Modified the entry script to run the native CLI terminal agent (`exec claude "$@"`) by default. Added a `--gui` flag to explicitly request launching the Tauri GUI interface (`pnpm tauri dev`).
- **`package.json`**: Added a `"cli"` script (`"cli": "./bin/ai-os --cli"`) to run the CLI mode easily via `pnpm cli`.

## What Worked
- Modifying `bin/ai-os` to default to CLI execution unless `--gui` is explicitly passed.
- Adding the `cli` script to `package.json`.

## What Didn't Work / Known Issues
None.

## Architecture Notes
- Running `ai-os` or `./bin/ai-os` now automatically spawns the terminal-based agent.
- Developers can still launch the Tauri-based GUI dashboard by running `./bin/ai-os --gui`.
