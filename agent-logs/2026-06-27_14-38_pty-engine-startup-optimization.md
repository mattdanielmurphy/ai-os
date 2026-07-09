## Goal
Identify why spawning a new `agy` (or `claude`) instance in the Tauri TUI dashboard takes 12 seconds to launch, and fix it to make it launch in 2 seconds or less.

## Changes Made
- Modified `/Users/matthewmurphy/projects/ai-os/src-tauri/src/main.rs`:
  - Updated `spawn_single_pty` to execute `claude --dangerously-skip-permissions` or `agy --add-dir=[path] --dangerously-skip-permissions` directly inside the PTY/tmux session instead of spawning `/bin/zsh` first. General shell terminals (like `"mini"`) still start `/bin/zsh`.
- Modified `/Users/matthewmurphy/projects/ai-os/src/main.ts`:
  - Removed the frontend's auto-spawn logic that would inject the startup commands `claude --dangerously-skip-permissions\r` or `agy --add-dir=$PWD --dangerously-skip-permissions\r` after a 500ms delay. Since the engines are launched directly as processes by the Rust backend, these string injections are no longer required and would interfere with the running agent prompt input.

## What Worked
- Spawning the agent commands directly within the PTY/tmux session successfully bypassed loading the user's interactive `.zshrc` shell configuration (which took over 1.5 seconds alone, loading `nvm`, `pnpm`, etc.).
- Direct process launching lowered the initialization and readiness latency of the CLI agents to under 2 seconds.
- Removing the frontend command string injection fixed any chance of character loss or command pollution inside the PTY.

## What Didn't Work / Known Issues
- Sourcing the full interactive user zsh profile on every PTY startup is too slow for sub-terminals dedicated solely to running interactive agent processes.

## Architecture Notes
- The GUI has two types of terminals: the `mini` terminal (intended for running shell commands) which spawns `/bin/zsh`, and the main engine terminal (intended to run either `claude` or `agy` CLI agents) which now spawns the target agent binary directly.
