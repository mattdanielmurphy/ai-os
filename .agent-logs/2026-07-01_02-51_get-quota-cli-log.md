## Goal
Extract the currently signed-in account for the agy cli from its log file (`~/.gemini/antigravity-cli/log`) and use it to explicitly request quota data via `ag-quota --account <email> -j`, rather than relying on `google_accounts.json`.

## Changes Made
- Modified `get_quota` in `src-tauri/src/main.rs`.
- Removed logic that parsed `~/.gemini/google_accounts.json`.
- Added logic to read `~/.gemini/antigravity-cli/log` from the end (using `.lines().rev()`) and parse the most recent "authenticated successfully as USER" occurrence to find the current active user for the cli.
- Passed the extracted email as the `--account` parameter to `ag-quota`.

## What Worked
- Replaced the implementation to correctly parse the log file for the target email string instead of reading the json file.

## What Didn't Work / Known Issues
- The `google_accounts.json` method was incorrect specifically for the `antigravity-cli` context, as pointed out by the user. The log file accurately reflects this application's state.

## Architecture Notes
- The current user for the `antigravity-cli` is recorded as a log entry: `I0624 ... auth.go:... OAuth: authenticated successfully as [email]`. Reversing through the lines reliably pulls the latest login session.
