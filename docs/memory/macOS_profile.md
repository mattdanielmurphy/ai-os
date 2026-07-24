# macOS System Profile (Auto-Generated)
## Storage & Volumes
Storage:

    Macintosh HD:

      Free: 18.18 GB (18 180 759 552 bytes)
      Capacity: 494.38 GB (494 384 795 648 bytes)
      Mount Point: /System/Volumes/Update/mnt1
      File System: APFS
      Writable: Yes
      Ignore Ownership: No
      BSD Name: disk3s1
      Volume UUID: 229A6DE2-2998-43AC-B1AA-3188979D70F7
      Physical Drive:
          Device Name: APPLE SSD AP0512Z
          Media Name: AppleAPFSMedia
          Medium Type: SSD
          Protocol: Apple Fabric
          Internal: Yes
          Partition Map Type: Unknown
          S.M.A.R.T. Status: Verified

    Data:

      Free: 18.18 GB (18 180 759 552 bytes)
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

    iOS 26.3.1 Simulator:

      Free: 459.6 MB (459 620 352 bytes)
      Capacity: 17.75 GB (17 754 488 832 bytes)
      Mount Point: /Library/Developer/CoreSimulator/Volumes/iOS_23D8133
      File System: APFS
      Writable: No
      Ignore Ownership: No
      BSD Name: disk5s1
      Volume UUID: 24D4020B-374E-41EA-850D-95D245363378
      Physical Drive:
          Device Name: Disk Image
          Media Name: AppleAPFSMedia
          Protocol: Disk Image
          Internal: No
          Partition Map Type: Unknown

    Macintosh HD:

      Free: 18.18 GB (18 180 759 552 bytes)
      Capacity: 494.38 GB (494 384 795 648 bytes)
      Mount Point: /
      File System: APFS
      Writable: No
      Ignore Ownership: No
      BSD Name: disk3s1s1
      Volume UUID: 0FDB629A-27A5-4431-AA03-33A88A1EA3AC
      Physical Drive:
          Device Name: APPLE SSD AP0512Z
          Media Name: AppleAPFSMedia
          Medium Type: SSD
          Protocol: Apple Fabric
          Internal: Yes
          Partition Map Type: Unknown
          S.M.A.R.T. Status: Verified

## Active LaunchAgents
total 224
drwxr-xr-x@  23 matt  staff    736 Jul 21 20:11 .
drwx------@ 101 matt  staff   3232 Jul 23 21:25 ..
drwxr-xr-x@  14 matt  staff    448 Jul 21 20:38 Archive
-rw-r--r--@   1 matt  staff    871 Jul  5 00:08 com.google.GoogleUpdater.wake.plist
-rw-r--r--@   1 matt  staff    181 Jul  5 00:08 com.google.keystone.agent.plist
-rw-r--r--@   1 matt  staff    181 Jul  5 00:08 com.google.keystone.xpcservice.plist
-rw-------@   1 matt  staff    905 Jul 19 23:51 com.matt.agent.agy-proxy.plist
-rw-r--r--@   1 matt  staff    656 Jul 11 16:22 com.matt.agent.agymcp.plist
-rw-------@   1 matt  staff   1158 Jul 10 16:39 com.matt.agent.backup-agents.plist
-rw-------@   1 matt  staff    850 Jul 10 16:39 com.matt.agent.chrome-debug.plist
-rw-------@   1 matt  staff    957 Jul 10 16:39 com.matt.agent.energy-monitor.plist
-rw-------@   1 matt  staff    890 Jul 10 16:48 com.matt.agent.gemini-ingest.plist
-rw-------@   1 matt  staff   2513 Jul 19 18:35 com.matt.agent.hermes-gateway.plist
-rw-------@   1 matt  staff    894 Jul 10 16:39 com.matt.agent.irig-watcher.plist
-rw-------@   1 matt  staff    930 Jul 10 16:39 com.matt.agent.litellm.plist
-rw-r--r--@   1 matt  staff   1234 Jul 21 20:06 com.matt.agent.local-automation-server.plist
-rw-------@   1 matt  staff    959 Jul 10 16:39 com.matt.agent.notesync.plist
-rw-------@   1 matt  staff    889 Jul 20 01:49 com.matt.agent.rules-watcher.plist
-rw-r--r--@   1 matt  staff    427 Jul  4 23:32 com.pieces.os.launch.plist
-rw-r--r--@   1 matt  staff    747 Jul  4 23:32 com.samschott.maestral.maestral.plist
-rwxr-xr-x@   1 matt  staff    376 Jul 10 15:53 git-sync.sh
-rw-r--r--@   1 matt  staff    685 Jul  4 23:32 homebrew.mxcl.nginx.plist
-rwxr-xr-x@   1 matt  staff  33472 Jul  4 23:32 notesync-wrapper
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
require("modules.qwerty_midi")

-- ── Startup confirmation ─────────────────────────────────────────────────────────

hs.alert.show("⚙️  Hammerspoon config loaded")
