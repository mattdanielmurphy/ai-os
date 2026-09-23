---
name: macos-service-migration
description: "Migrate launch agents, permissions, and daemons after a macOS user account migration — audit stale plists, fix hardcoded paths, kill leftover processes, reload services under the new user."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [macOS, User-Migration, LaunchAgents, Launchd, TCC, Permissions, System-Admin]
    related_skills: [systematic-debugging]
---

# macOS Service Migration

## When to Use

After a macOS user account migration (e.g., `matthewmurphy` → `matt`) when:

- Apps report "you don't have permission to access" errors
- Launch agents from the old user are still loaded
- Old user processes (`lsd`, `distnoted`, `containermanagerd`) are still running under the old UID
- TCC permissions granted to the old user aren't working
- Stale `~/Library/Preferences/` files reference the old username in paths

## Prerequisites

- List all loaded launch agents: `launchctl list | grep -v "com.apple"`
- Check for stale processes: `ps -U <old_username>`
- Check filesystem write access: `test -w /target/path && echo writable`

## Procedure

### Phase 1: Audit Existing Services

Run these in parallel batch to inventory stale state:

```bash
# 1. List all launch agent plists
ls ~/Library/LaunchAgents/*.plist

# 2. Check which ones are loaded (and find stale matthewmurphy-name plists)
for f in ~/Library/LaunchAgents/com.matthewmurphy.*.plist; do
  echo "=== $(basename $f) ==="
  plutil -p "$f" | head -20
  echo "Loaded?"
  launchctl list "$(plutil -extract Label raw "$f" 2>/dev/null)" 2>&1 | head -3
done

# 3. Check for old-user processes still running
ps -U <old_username> -o pid,comm

# 4. Check filesystem / Applications/ for stale ownership
find /Applications -user <old_username> -maxdepth 3 2>/dev/null
```

### Phase 2: Understand What Each Service Does

For each stale plist:

1. **Read the plist** — see what `Program` or `ProgramArguments` it runs
2. **Check if the script/binary still exists** — the actual script at the referenced path
3. **Read the script content** — `cat` the actual script to understand its function
4. **Search for moved scripts** — CloudMounter documents often migrate to `~/Documents/Scripts/macOS/` after a re-mount. Use `mdfind -name <script_name>` and `find ~/Documents -name <script_name>`
5. **Classify each service**:

   | Category | Action |
   |----------|--------|
   | **Keep** — actively useful, works as-is | Update plist path, rename file |
   | **Keep, needs fix** — useful but path/reference broken | Fix paths in plist AND in referenced scripts |
   | **Archive** — might want later | Unload, move plist to `~/Library/LaunchAgents/Archive/` |
   | **Remove** — no longer wanted | Unload, move plist to Trash |

6. **Check for stale paths inside the scripts themselves** — the script may have hardcoded `/Users/old_username/...` references that need updating even after fixing the plist path.

### Phase 3: Fix and Migrate

For each service to keep:

```bash
# 1. Unload the old service (by Label or by plist path)
launchctl bootout gui/$(id -u)/com.example.label  # by Label
# OR
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/old-name.plist  # by file

# 2. Create new plist with updated paths and com.matt.agent.* filename
cat > ~/Library/LaunchAgents/com.matt.agent.<name>.plist << EOF
... updated plist XML ...
EOF

# 3. Load the new service
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.matt.agent.<name>.plist

# 4. Verify
launchctl list com.matt.agent.<name>
```

**All scripted services run inside tmux.** After migrating, wrap every script-based launch agent through `tmux-agent-wrapper.sh` (`~/Library/Scripts/tmux-agent-wrapper.sh`). This gives every service a named tmux session for live log access (`tmux attach -t agent-<name>`), auto-restarts when the script file is edited (via fswatch), and shows a macOS notification on restart. See `references/tmux-agent-wrapper.md` for the full architecture, plist templates, and migration steps. See `references/fswatch-watchdog-pattern.md` for the keepalive watchdog script pattern used by directory-watching agents.

For services to remove:

```bash
launchctl bootout gui/$(id -u)/com.example.label
mv ~/Library/LaunchAgents/com.matthewmurphy.<name>.plist ~/.Trash/
```

For services to archive:

```bash
mkdir -p ~/Library/LaunchAgents/Archive
launchctl bootout gui/$(id -u)/com.example.label
mv ~/Library/LaunchAgents/com.matthewmurphy.<name>.plist ~/Library/LaunchAgents/Archive/com.matt.<name>.plist
```

### Phase 4: Kill Stale Old-User Processes

After auditing, kill leftover daemon processes still running under the old UID:

```bash
# Identify stale processes
ps -U <old_username> -o pid,comm

# Kill them
sudo kill <pid1> <pid2> <pid3>

# Key processes to look for:
# - lsd (Launch Services) — manages app registration, can block /Applications/ access
# - distnoted — distributed notifications
# - mdbulkimport — Spotlight metadata import
# - trustd — certificate trust management
# - containermanagerd — app sandbox containers
# - pkd — package kit
```

**Note:** Some of these (especially `distnoted` and `lsd`) are PID-1 children that launchd respawns immediately. A logout/login fully resets the per-user launchd context. Recommend the user logs out after killing.

### Phase 5: Verify

```bash
# 1. Confirm old user has no more processes
ps -U <old_username> -o pid,comm

# 2. Confirm new services are loaded and working
launchctl list com.matt.<name>

# 3. Confirm /Applications/ write access works
touch /Applications/.test && rm /Applications/.test  # or mv to Trash
```

## References

- `references/session-service-migration.md` — detailed session trace with specific plist contents and script analysis patterns.
- `references/tmux-agent-wrapper.md` — architecture and plist templates for running launch agents in tmux with fswatch auto-restart.
- `references/fswatch-watchdog-pattern.md` — reusable watchdog script template for keepalive agents that monitor a directory with fswatch (e.g. auto-ingesters, sync watchers). Includes a plist template, bash loop pattern, and verification checklist.

## Pitfalls

1. **Old service stays cached in launchd even after you create a new plist file.** launchd loaded the old file by its internal Label. When you create a new file with the same Label, you must `bootout` the old one by Label (not by file path) before `bootstrap`ing the new one.

2. **Scripts may have their own hardcoded old-user paths.** Fixing the plist path alone isn't enough if the referenced script contains `/Users/old_username/...`. Always `cat` the referenced script.

3. **CloudMounter path changes after re-mount.** After a CloudMounter re-mount, the mount path may change from `CloudMounter-OldName` to `CloudMounter-NewName`. Scripts that reference the old path will fail silently. Use `find ~/Documents -name <script>` as a fallback.

4. **Don't over-engineer the delegation.** If you're calling a subagent to investigate, use a direct terminal command. No Python wrappers, no temp files, no intermediate layers — just `agy -p "prompt" --dangerously-skip-permissions --print-timeout 5m`.

5. **`-p` argument ordering.** With agy, the prompt text must come IMMEDIATELY after `-p`. Flags after the prompt. See the `agy` skill for full details.

6. **TCC database is per-user.** After a migration, apps that had Full Disk Access under the old user won't automatically have it under the new user. Open System Settings > Privacy & Security and re-grant. The TCC DB is at `~/Library/Application Support/com.apple.TCC/TCC.db`.

9. **Naming convention mismatch after migration.** New plists should use `com.matt.agent.<name>` labels and filenames (not bare `com.matt.<name>`) to clearly distinguish tmux-wrapped services from other plists. Update backup and glob patterns accordingly (e.g., `cp ~/Library/LaunchAgents/com.matt.agent.*.plist ~/Backups/`).

10. **`fswatch` is a hard dependency for `keepalive` mode.** Without it, the wrapper falls back to stat polling every 2s, which is less efficient. If fswatch is unavailable on a new machine, install it: `brew install fswatch`. For binary-only machines where you don't want fswatch, use `keepalive --no-watch`.