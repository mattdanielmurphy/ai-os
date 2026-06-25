## Goal
Fix the agent CLI so it can successfully spawn a background PTY session on macOS. The user reported a timeout error waiting for the prompt, which was caused by the `script` command immediately exiting with code 1.

## Changes Made
- `src/ptyWrapper.js`: Replaced `spawn('script', ...)` with `spawn('python3', ['-c', 'import sys, pty; pty.spawn(...)'])`.

## What Worked
- Python's `pty` module successfully spawns the bash session, tricking `agy` into thinking it's running in an interactive session, without crashing `posix_spawnp` (which `node-pty` was doing on Node v26).
- The warm background session correctly initialized and captured the `Ready for input>` prompt.

## What Didn't Work / Known Issues
- `node-pty` fails with `posix_spawnp failed` on this Node version.
- `script` command on macOS fails with `tcgetattr/ioctl: Operation not supported on socket` when `spawn` uses pipes.

## Architecture Notes
- The background PTY wrapper `WarmPtySession` exploits consumer flat-rate subscriptions by running `agy` directly in an interactive bash session and passing commands through standard input.
