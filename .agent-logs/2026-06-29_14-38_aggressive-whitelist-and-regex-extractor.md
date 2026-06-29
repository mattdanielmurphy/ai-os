## Goal
Upgrade the command interception logic from individual selective wrappers to an aggressive, dynamic array-based whitelist with smart regex error extraction to prepare for future agentic "token audits".

## Changes Made
- Modified `/Users/matthewmurphy/projects/ai-os/.zshrc_aios`.
- Refactored the `qr` (Quiet Run) wrapper to be smarter: it now takes a display name, silences output on success (showing only the last 3 lines to confirm completion), and on failure, it uses `grep` to extract common error lines (fatal, panic, error, exception) instead of blindly dumping the tail.
- Replaced the hardcoded selective sub-command wrappers (`npm install`, `cargo build`) with a flat `NOISY_COMMANDS` array whitelist that wraps *all* invocations of the whitelisted binaries (`npm`, `pnpm`, `pytest`, `docker`, `rustc`, `go`, etc.).
- A dynamic `eval` loop automatically generates the wrapper functions for everything in the array, making it extremely easy for a future agent to simply append to the array during a token audit.

## What Worked
- File replacement executed cleanly.
- The array-based `eval` loop correctly handles scoping and passes `$@` through `qr`.

## What Didn't Work / Known Issues
- None so far.

## Architecture Notes
- Wrapping the entirety of standard CLI tools (like `npm` or `go`) instead of just specific subcommands ensures the agent has zero "interactive TUI/prompt" attack surface for those tools. If the command succeeds, tokens are saved. If it fails, the error extractor isolates the reason, avoiding massive unpaginated stack dumps in the context window.
