# macOS Service Migration — Session Reproduction

## Context

Migrated from `matthewmurphy` to `matt` on macOS 15.7.8. Several permissions issues appeared after the migration, including:

> "AlDente" couldn't be copied because you don't have permission to access "Applications"

## Inventory of Stale Services

### Running as `matthewmurphy` (killed)

| PID | Process | Function |
|-----|---------|----------|
| 398 | `lsd` | Launch Services daemon — manages app registration, file access. Running under old UID was the most likely cause of the /Applications/ permission error |
| 382 | `distnoted` | Distributed notifications — stale, respawned by launchd immediately |
| 10480 | `mdbulkimport` | Spotlight metadata import |

### com.matthewmurphy.* Plists Found

1. **`energy_monitor.sh`** — CPU energy watchdog
   - Polls every 5 min for processes > 100% CPU
   - If found, pops a dialog: "High energy impact detected: [process]" with link to Gemini thread
   - Excludes known-heavy apps (Chrome, Final Cut, Logic Pro, etc.)
   - Old plist path: `CloudMounter-MatthewMurphy/...` (broken)
   - Script found at: `~/Documents/Scripts/macOS/energy_monitor.sh`
   - **Verdict:** Keep. Updated plist path, renamed to `com.matt.energy_monitor.plist`

2. **`irig_watcher.sh`** — iRig Pre HD audio interface hotplug
   - Polls USB via `ioreg` every 2 seconds (changed to 10s for lower impact)
   - On connect: switches audio output to BlackHole 16ch, opens Audio Hijack
   - On disconnect: restores previous audio output, quits Audio Hijack
   - Old plist path: `CloudMounter-MattMurphy/...` (broken)
   - Script found at: `~/Documents/Scripts/macOS/irig_watcher.sh`
   - **Verdict:** Keep. Updated plist path, slowed polling, renamed to `com.matt.irig-watcher.plist`

3. **`personal-sync`** — Obsidian Unison sync
   - Uses `fswatch` to monitor iCloud Obsidian vault + Google Drive (CloudMounter)
   - Runs `unison personal -batch` to bidirectional sync
   - Scripts hardcode `/Users/matthewmurphy/...` paths throughout
   - **Verdict:** Archived. Plist moved to `~/Library/LaunchAgents/Archive/com.matt.personal-sync.plist`

4. **`backup-launch-agents`** — Daily LaunchAgent backup
   - Originally rsynced to CloudMounter
   - Changed to simple `cp` to `~/Documents/LaunchAgentBackups/`
   - **Verdict:** Keep. Updated to use local `cp` + renamed plist.

5. **`rqbit`** — BitTorrent server (v8.1.1)
   - Running but user no longer uses it
   - **Verdict:** Removed. Unloaded and sent to Trash.

### Other Findings

- **~/Documents/LaunchAgentBackups/** created for backup-agent target directory
- **~/Library/LaunchAgents/Archive/** created for archived plists
- **Runaway `chown` process** found running for 5+ minutes (`find /Users/matt -user matthewmurphy -exec chown`) — killed
- **~/Library/Preferences/ files** with stale `matthewmurphy` references exist (plists from Transmission, Chrome Canary, Keyboard Maestro, rqbit, Folx, etc.) — these are typically lazy-loaded and self-heal; no action taken unless a specific app fails

## Commands Used

```bash
# Inventory plists
for f in ~/Library/LaunchAgents/com.matthewmurphy.*.plist; do
  echo "=== $(basename $f) ==="
  plutil -p "$f" | head -20
done

# Unload by Label
launchctl bootout gui/$(id -u)/com.matt.<label>

# Unload by file
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/name.plist

# Load new plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.matt.<name>.plist

# Verify
launchctl list com.matt.<name>

# Kill stale processes
sudo kill <pid>

# Confirm /Applications/ write access
touch /Applications/.test  # succeeds
rm /Applications/.test     # succeeds
```

## Diagnostic Commands Used

```bash
# Check /Applications/ permissions
ls -lde /Applications/
test -w /Applications && echo "writable"
touch /Applications/.test-write-perms  # confirms write access as non-root

# Find stale processes
ps -U matthewmurphy -o pid,comm

# Check SIP status
csrutil status

# Check TCC database (Full Disk Access entries)
sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db \
  "SELECT client, service, auth_value FROM access WHERE service LIKE '%SystemPolicy%';"

# Search for moved scripts
mdfind -name "energy_monitor.sh"
find ~/Documents -name "irig_watcher.sh"
