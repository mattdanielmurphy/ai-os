# macOS System Profile (Auto-Generated)
## Storage & Volumes
Storage:

    Macintosh HD:

      Free: 42.54 GB (42 543 247 360 bytes)
      Capacity: 494.38 GB (494 384 795 648 bytes)
      Mount Point: /System/Volumes/Update/mnt1
      File System: APFS
      Writable: Yes
      Ignore Ownership: No
      BSD Name: disk3s1
      Volume UUID: C7E79875-98EF-4E2E-9ECB-47C841C75850
      Physical Drive:
          Device Name: APPLE SSD AP0512Z
          Media Name: AppleAPFSMedia
          Medium Type: SSD
          Protocol: Apple Fabric
          Internal: Yes
          Partition Map Type: Unknown
          S.M.A.R.T. Status: Verified

    Data:

      Free: 42.54 GB (42 543 181 824 bytes)
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

    Macintosh HD:

      Free: 42.54 GB (42 543 181 824 bytes)
      Capacity: 494.38 GB (494 384 795 648 bytes)
      Mount Point: /
      File System: APFS
      Writable: No
      Ignore Ownership: No
      BSD Name: disk3s1s1
      Volume UUID: 55BFE8E0-6A29-4620-8512-65737149058E
      Physical Drive:
          Device Name: APPLE SSD AP0512Z
          Media Name: AppleAPFSMedia
          Medium Type: SSD
          Protocol: Apple Fabric
          Internal: Yes
          Partition Map Type: Unknown
          S.M.A.R.T. Status: Verified

## Active LaunchAgents
total 208
drwxr-xr-x@  20 matthewmurphy  staff    640 Jun 27 02:46 .
drwx------@ 129 matthewmurphy  staff   4128 May 21 13:43 ..
-rw-r--r--@   1 matthewmurphy  staff   6148 Jun 24 00:47 .DS_Store
-rw-------@   1 matthewmurphy  staff   1437 Jun 13 00:40 ai.openclaw.gateway.plist
-rw-r--r--@   1 matthewmurphy  staff    880 Feb 19 13:37 com.google.GoogleUpdater.wake.plist
-rw-r--r--@   1 matthewmurphy  staff    594 Jun 27 02:46 com.lwouis.alt-tab-macos.plist
-rw-r--r--@   1 matthewmurphy  staff   1336 Jun  7 15:52 com.matthewmurphy.backup-launch-agents.plist
-rw-r--r--    1 matthewmurphy  staff    494 May 19 23:39 com.matthewmurphy.energy_monitor.plist
-rw-r--r--@   1 matthewmurphy  staff    711 Mar 22 14:39 com.matthewmurphy.irig-watcher.plist
-rw-r--r--@   1 matthewmurphy  staff    720 Mar 16 13:12 com.matthewmurphy.personal-sync.plist
-rw-r--r--@   1 matthewmurphy  staff    686 Feb 28 21:01 com.matthewmurphy.rqbit.plist
-rw-r--r--@   1 matthewmurphy  staff   1537 Dec 11  2025 com.mattmurphy.userscript-bundler.plist
-rw-r--r--@   1 matthewmurphy  staff    427 Jun  1 13:15 com.pieces.os.launch.plist
-rw-r--r--@   1 matthewmurphy  staff    747 Oct 11  2024 com.samschott.maestral.maestral.plist
lrwxr-xr-x    1 matthewmurphy  staff    132 Jun 22 22:42 com.user.notesync.plist -> /Users/matthewmurphy/Library/CloudStorage/CloudMounter-MatthewMurphy/My Documents/Scripts/macOS/LaunchAgents/com.user.notesync.plist
-rw-r--r--@   1 matthewmurphy  staff    890 Jan  1 17:23 com.valvesoftware.steamclean.plist
-rwxr-xr-x@   1 matthewmurphy  staff    385 Jun 22 23:35 git-sync.sh
-rw-r--r--@   1 matthewmurphy  staff    685 Jan  5  2025 homebrew.mxcl.nginx.plist
-rw-r--r--@   1 matthewmurphy  staff    386 Dec 19  2025 Messauto.plist
-rwxr-xr-x@   1 matthewmurphy  staff  33472 Jun 22 23:36 notesync-wrapper
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

local _configWatcher = hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", _reloadConfig)
_configWatcher:start()

-- ── Modules ─────────────────────────────────────────────────────────────────────

require("modules.clipboard")

-- ── Startup confirmation ─────────────────────────────────────────────────────────

hs.alert.show("⚙️  Hammerspoon config loaded")
