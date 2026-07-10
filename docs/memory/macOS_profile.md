# macOS System Profile (Auto-Generated)
## Storage & Volumes
Storage:

    Macintosh HD:

      Free: 4.55 GB (4 548 390 912 bytes)
      Capacity: 494.38 GB (494 384 795 648 bytes)
      Mount Point: /System/Volumes/Update/mnt1
      File System: APFS
      Writable: Yes
      Ignore Ownership: No
      BSD Name: disk3s1
      Volume UUID: DECCCDF9-E88C-4D9C-A074-84D186C59DA3
      Physical Drive:
          Device Name: APPLE SSD AP0512Z
          Media Name: AppleAPFSMedia
          Medium Type: SSD
          Protocol: Apple Fabric
          Internal: Yes
          Partition Map Type: Unknown
          S.M.A.R.T. Status: Verified

    Data:

      Free: 4.55 GB (4 548 370 432 bytes)
      Capacity: 494.38 GB (494 384 795 648 bytes)
      Mount Point: /System/Volumes/Data
      File System: APFS
      Writable: Yes
      Ignore Ownership: No
      BSD Name: disk3s5
      Volume UUID: 803BA0DA-CFF1-407D-88AD-0A0631D9E971
      Physical Drive:
          Device Name: APPLE SSD AP0512Z
          Media Name: AppleAPFSMedia
          Medium Type: SSD
          Protocol: Apple Fabric
          Internal: Yes
          Partition Map Type: Unknown
          S.M.A.R.T. Status: Verified

    Warp:

      Free: 102.5 MB (102 465 536 bytes)
      Capacity: 570.4 MB (570 425 344 bytes)
      Mount Point: /Volumes/Warp
      File System: APFS
      Writable: No
      Ignore Ownership: Yes
      BSD Name: disk5s1
      Volume UUID: 6872811E-41F9-4526-BEF6-D490A984B696
      Physical Drive:
          Device Name: Disk Image
          Media Name: AppleAPFSMedia
          Protocol: Disk Image
          Internal: No
          Partition Map Type: Unknown

    AlDente:

      Free: 48.1 MB (48 062 464 bytes)
      Capacity: 79.1 MB (79 126 528 bytes)
      Mount Point: /Volumes/AlDente
      File System: APFS
      Writable: No
      Ignore Ownership: Yes
      BSD Name: disk9s1
      Volume UUID: 286FFAAF-E5A5-4674-83DC-D6EF5043432F
      Physical Drive:
          Device Name: Disk Image
          Media Name: AppleAPFSMedia
          Protocol: Disk Image
          Internal: No
          Partition Map Type: Unknown

    Macintosh HD:

      Free: 4.55 GB (4 548 239 360 bytes)
      Capacity: 494.38 GB (494 384 795 648 bytes)
      Mount Point: /
      File System: APFS
      Writable: No
      Ignore Ownership: No
      BSD Name: disk3s1s1
      Volume UUID: 3C6A96EA-501E-42AB-8DC1-D29B58438B55
      Physical Drive:
          Device Name: APPLE SSD AP0512Z
          Media Name: AppleAPFSMedia
          Medium Type: SSD
          Protocol: Apple Fabric
          Internal: Yes
          Partition Map Type: Unknown
          S.M.A.R.T. Status: Verified

## Active LaunchAgents
total 232
drwxr-xr-x@ 23 matt  staff    736 Jul 10 12:55 .
drwx------@ 93 matt  staff   2976 Jul 10 15:12 ..
-rw-r--r--@  1 matt  staff   2394 Jul 10 12:55 ai.hermes.gateway.plist
-rw-------@  1 matt  staff   1392 Jul  4 23:32 ai.openclaw.gateway.plist
-rw-r--r--@  1 matt  staff    650 Jul  8 00:15 com.chrome.debug.plist
-rw-r--r--@  1 matt  staff    871 Jul  5 00:08 com.google.GoogleUpdater.wake.plist
-rw-r--r--@  1 matt  staff    181 Jul  5 00:08 com.google.keystone.agent.plist
-rw-r--r--@  1 matt  staff    181 Jul  5 00:08 com.google.keystone.xpcservice.plist
-rw-r--r--@  1 matt  staff    594 Jul 10 10:44 com.lwouis.alt-tab-macos.plist
-rw-r--r--@  1 matt  staff   1273 Jul  4 23:32 com.matthewmurphy.backup-launch-agents.plist
-rw-r--r--@  1 matt  staff    476 Jul  4 23:32 com.matthewmurphy.energy_monitor.plist
-rw-r--r--@  1 matt  staff    693 Jul  4 23:32 com.matthewmurphy.irig-watcher.plist
-rw-r--r--@  1 matt  staff    666 Jul  4 23:32 com.matthewmurphy.personal-sync.plist
-rw-r--r--@  1 matt  staff    668 Jul  4 23:32 com.matthewmurphy.rqbit.plist
-rw-r--r--@  1 matt  staff    786 Jul  8 05:44 com.mattmurphy.ai-os-rules-watcher.plist
-rw-r--r--@  1 matt  staff    697 Jul 10 01:35 com.mattmurphy.litellm.plist
-rw-r--r--@  1 matt  staff   1480 Jul  9 18:21 com.mattmurphy.userscript-bundler.plist
-rw-r--r--@  1 matt  staff    427 Jul  4 23:32 com.pieces.os.launch.plist
-rw-r--r--@  1 matt  staff    747 Jul  4 23:32 com.samschott.maestral.maestral.plist
-rwx------@  1 matt  staff    856 Jul  4 23:32 com.user.notesync.plist
-rwxr-xr-x@  1 matt  staff    385 Jul  4 23:32 git-sync.sh
-rw-r--r--@  1 matt  staff    685 Jul  4 23:32 homebrew.mxcl.nginx.plist
-rwxr-xr-x@  1 matt  staff  33472 Jul  4 23:32 notesync-wrapper
## Connected Displays
Graphics/Displays:

    Apple M2 Pro:

      Chipset Model: Apple M2 Pro
      Type: GPU
      Bus: Built-In
      Total Number of Cores: 19
      Vendor: Apple (0x106b)
      Metal Support: Metal 3
      Displays:
        Color LCD:
          Display Type: Built-in Liquid Retina XDR Display
          Resolution: 3456 x 2234 Retina
          Main Display: Yes
          Mirror: Off
          Online: Yes
          Automatically Adjust Brightness: No
          Connection Type: Internal

## Hammerspoon Config
-- ~/.hammerspoon/init.lua
-- Entry point for the Hammerspoon configuration.
-- Loads modular components and sets up automatic config reloading.
--
-- ── Global Anchoring Convention ─────────────────────────────────────────────────
-- CRITICAL: All persistent Hammerspoon resources (watchers, window filters, event
-- taps, hotkeys) MUST be anchored to the global `_G.activeWatchers` table. Lua's
-- garbage collector silently collects `local` variables after a module finishes
-- loading, which destroys the underlying macOS event taps and causes silent
-- failures. Never assign these to local variables, and never implement periodic
-- timer "health checks" as a workaround — the root cause is always a missing
-- global reference.
-- ────────────────────────────────────────────────────────────────────────────────

-- ── Global anchor table ─────────────────────────────────────────────────────────
-- All modules and sub-modules share this same table via the `_G` key.
_G.activeWatchers = _G.activeWatchers or {}

-- ── Config auto-reloader ────────────────────────────────────────────────────────
-- Watches the entire ~/.hammerspoon/ directory tree for .lua changes and
-- triggers a full reload so edits take effect immediately.

local function _reloadConfig(files)
  local shouldReload = false
  for _, file in ipairs(files) do
    if file:sub(-4) == ".lua" then
      shouldReload = true
      break
    end
  end
  if shouldReload then
    hs.reload()
  end
end

activeWatchers.configWatcher = hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", _reloadConfig)
activeWatchers.configWatcher:start()

-- ── Modules ─────────────────────────────────────────────────────────────────────

require("modules.clipboard")
require("modules.keybindings")

-- ── Startup confirmation ─────────────────────────────────────────────────────────

hs.alert.show("⚙️  Hammerspoon config loaded")