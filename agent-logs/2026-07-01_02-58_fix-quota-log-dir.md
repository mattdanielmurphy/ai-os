## Goal
Fix `get_quota` failing to fetch the quota (returning 0%).

## Changes Made
- Changed `get_quota` in `src-tauri/src/main.rs` to treat `~/.gemini/antigravity-cli/log` as a directory rather than a file.
- `std::fs::read_to_string` was failing because it was a directory.
- It now reads all files in the directory, sorts them (which puts them in chronological order due to their naming format), and iterates through them from newest to oldest. 
- It reads each file backwards line-by-line until it finds the `authenticated successfully as ` entry to extract the email.

## What Worked
- Correctly parsed the email by searching the actual `.log` files inside the directory.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The `log` folder under `~/.gemini/antigravity-cli/` is a directory of rotated logs, not a single monolithic file.
