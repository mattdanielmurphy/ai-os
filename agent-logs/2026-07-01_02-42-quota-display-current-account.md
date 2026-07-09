## Goal
Modify the ai-os desktop application so that its quota display portion fetches and displays the quotas for the currently signed-in account in the `agy` CLI, rather than the global default or hardcoded account.

## Changes Made
- Modified `src-tauri/src/main.rs`: Updated the `get_quota` Tauri command. It now dynamically reads `~/.gemini/google_accounts.json` to extract the `active` account.
- It then executes `ag-quota --account <active_account> -j` instead of just `ag-quota -j`. This forces `ag-quota` to output the quotas only for the logged-in user in the proper JSON format, which the frontend TS parses and renders without further changes.

## What Worked
- Confirmed that `ag-quota --account <email> -j` returns a valid JSON object matching the standard un-filtered format.
- The Rust code was successfully updated, tested with `cargo check`, and committed.

## What Didn't Work / Known Issues
- None.

## Architecture Notes
- The active logged in user for `agy` is stored at `~/.gemini/google_accounts.json` under the `"active"` key. 
- The quota viewer frontend just calls the `get_quota` Tauri command which proxies straight into the `ag-quota` CLI utility.
