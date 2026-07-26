---
name: ai-os-quiet-run
description: Run noisy terminal commands with suppressed output — save full logs to ./tmp/ and surface only success/failure + error excerpts. Adapted from the ai-os qr() zsh wrapper.
version: 1.0.0
metadata:
  hermes:
    tags: [ai-os, terminal, token-saving, quiet-run]
---

# AI-OS Quiet Run

When running commands that produce large, noisy output (builds, package installs, test suites, compilers), use this pattern to avoid flooding the agent context window while still capturing full logs for debugging.

## When to Use

- `pnpm install`, `pnpm build`, `pnpm test`
- `cargo build`, `cargo test`
- `pip install`, `uv pip install`
- `make`, `docker build`, `docker-compose up`
- Any command whose output is expected to exceed ~20 lines

## The Pattern

```bash
# 1. Ensure ./tmp/ exists
mkdir -p ./tmp

# 2. Run the command, redirecting all output to a timestamped log
<your-command> > ./tmp/<sanitized-name>.log 2>&1; echo "EXIT:$?"
```

After running, check the exit code:

### On Success (exit 0)
Print only: `✅ '<display-name>' succeeded. (Full log: ./tmp/<name>.log)`
Then show the last 3 lines of the log for context.

### On Failure (non-zero)
Print: `❌ '<display-name>' failed with exit code <N>.`
Then extract and display error lines:
```bash
grep -iE "(error|exception|panic|fatal|traceback|fail|FAIL)" ./tmp/<name>.log | tail -n 30
```
If no error patterns match, show the last 20 lines of the log.

## Sanitized Filenames

Derive the log filename from the command: lowercase, replace non-alphanumeric with underscores, truncate to 40 chars.
Examples:
- `pnpm install` → `pnpm_install.log`
- `cargo build --release` → `cargo_build___release.log`

## Never Quiet-Run These

- `git` commands (output is usually short and meaningful)
- Commands the user explicitly asked to see the output of
- Commands whose output you need to parse programmatically in the same turn
- Interactive commands (use pty=true instead)
