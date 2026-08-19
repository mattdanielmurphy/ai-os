---
title: "please update Hermes Agent"
date: "2026-08-10"
conversation_id: "6acbf2c8a862"
source: "antigravity"
---

# please update Hermes Agent

## User

please update Hermes Agent

---

## Assistant

I'll inspect the `hermes-agent` skill and environment to check how to update Hermes Agent safely.

I am going to check the `hermes-agent` skill file directly.

I will check how `hermes` is installed and its current version/installation path.

I will run `hermes version` and check the git status in `/Users/matt/projects/hermes-agent`.

I'll check if `~/.hermes/hermes-agent` is a symlink to `/Users/matt/projects/hermes-agent` or a separate git repository.

I will check how `hermes` is installed in the python environment and test `hermes update --help` or `hermes update`.

I'll run `hermes update --check` to see what update status `hermes` reports.

I'll check for leftover lock files in `/Users/matt/projects/hermes-agent/.git/` and inspect git branches/remotes in both directories.

I'll inspect `~/.hermes/hermes-agent` as well.

I will check where the Python package for `hermes-agent` is pointing in the venv.

I'll check the contents of `/Users/matt/.hermes/hermes-agent/venv/bin/`.

I will check where `hermes_cli` is imported from in the active virtual environment.

I will check the git branches and status in `/Users/matt/projects/hermes-agent`.

I'll check the structure of `~/.hermes/hermes-agent` and `/Users/matt/projects/hermes-agent` and remove any stale `.git/*.lock` files.

I will check the branch status and any uncommitted changes in `/Users/matt/projects/hermes-agent` before proceeding with `hermes update`.

I will check the latest commit history on `main` and `origin/main`.

I will inspect the `/Users/matt/.hermes/hermes-agent/venv/bin/hermes` entry point script to confirm which source directory it executes.

I will inspect `hermes_cli/commands/update.py` (or related update code) in `/Users/matt/projects/hermes-agent` to see how `hermes update` runs.

I will search for update handlers inside `hermes_cli`.

I will check the branch status and diff between `feature/agy-native` and `main` in `/Users/matt/projects/hermes-agent`.

I will now run `hermes update --yes` to update Hermes Agent to the latest upstream release on `main`.

I'll run `hermes version` and `hermes doctor` to verify the update and system health.

I will now run `hermes doctor --fix` to apply available auto-fixes, such as migrating `config.yaml` to v34.

I will run `hermes version` to confirm the final version status.

Hermes Agent has been updated and verified:

### Summary of Actions Taken
1. **Lock Clean-up:** Removed stale `.git/shallow.lock` files blocking git ops.
2. **Repository Sync:** Switched working repository (`/Users/matt/projects/hermes-agent`) to `main` and updated to the latest upstream release (`3bd844ed`).
3. **Dependencies & Web UI:** 
   - Rebuilt Python and Node.js workspace dependencies.
   - Rebuilt the web UI frontend.
   - Refreshed model catalog and synced bundled skills (7 new, 20 updated).
   - Installed `hermes-acp` launcher.
4. **Configuration Migration:** Ran `hermes doctor --fix` to migrate `config.yaml` to schema v34.
5. **Services Restart:** Restarted the background dashboard backend process.

### Current Status
- **Version:** Hermes Agent `v0.20.0` (2026.8.3)
- **Upstream Commit:** `3bd844ed` (Up to date)
- **Doctor Status:** All core checks passing, configuration migrated to v34.

---
