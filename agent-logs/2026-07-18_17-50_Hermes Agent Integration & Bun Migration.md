## Goal
Enable Hermes Agent Integration in Tauri GUI and Rename App Folder (continued).

## User Feedback & Decisions
- Switched package manager to Bun for local builds.
- Added Hermes agent support as the third toggleable execution engine option.

## Changes Made
- `package.json`: Updated root workspace to specify `tauri-gui` and added `@rollup/rollup-darwin-x64` in `devDependencies` to support both native arm64 and Rosetta-based x64 Node environments.
- `bin/ai-os`: Changed GUI run script execution command from `pnpm tauri dev` to `cd tauri-gui && bun run tauri dev`.
- `tauri-gui/package.json`: Migrated package manager settings to Bun workspace dependency resolution protocol (`"ai-os": "workspace:*"`).
- `tauri-gui/index.html`: Added "Hermes (Hermes Agent)" radio button option to the engine selection dashboard.
- `tauri-gui/staging.html`: Added "Hermes Agent" select switch button to the stage execution dialog.
- `tauri-gui/src/main.ts`: Added typescript definitions and history cache buffers for `hermesBuffers`, updated type signatures for `currentEngine` and resolved buffers references across switches and clear hooks.
- `tauri-gui/src/staging.ts`: Updated active staging engine state parameters to handle `hermes` click selection toggles.
- `tauri-gui/src/systemPromptConfig.ts`: Corrected unescaped template string backticks to resolve compiler syntax errors.
- `tauri-gui/src-tauri/src/main.rs`: Added Rust backend support for spawning and monitoring `hermes` PTY/TUI sessions inside tmux windows (`ai_os_hermes_<tid>`), checking active process alive states, mapping session writers, and resolving process PIDs.
- `FEATURES.md`: Updated active features log.
- `.devtool/features/hermes-agent-gui-integration.md`: Set status to "review".

## What Worked
- Complete migration of dependencies from `pnpm` to `bun` using hoisted node compatibility.
- Clean compilation of both the Tauri Rust backend (`cargo check` passed) and client-side typescript (`vite build` succeeded).

## What Didn't Work / Known Issues
- Rosetta translation translation mismatch: Native Bun compiled and symlinked rollup binaries for `darwin-arm64` but Node.js 26.0.0 was x64 translated, requiring manual addition of `@rollup/rollup-darwin-x64` to the workspace dependencies using the `hoisted` linker and `--cpu=x64` flags.

## Architecture Notes
- `hermes` now runs natively alongside `agy` and `claude` CLI harnesses inside their own isolated tmux windows.

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-cli/brain/cb22be82-9f3e-408d-9895-5b615378e878/.system_generated/logs/transcript.jsonl)

[Full Transcript for this conversation](file:///Users/matt/.gemini/antigravity-cli/brain/cb22be82-9f3e-408d-9895-5b615378e878/.system_generated/logs/transcript.jsonl)
