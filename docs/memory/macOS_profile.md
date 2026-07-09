# macOS System Profile (Auto-Generated)
## Storage & Volumes
Storage:

    Macintosh HD:

      Free: 16.53 GB (16 533 975 040 bytes)
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

      Free: 16.53 GB (16 533 975 040 bytes)
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

      Free: 16.53 GB (16 533 975 040 bytes)
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
total 216
drwxr-xr-x@ 21 matt  staff    672 Jul  8 05:44 .
drwx------@ 92 matt  staff   2944 Jul  8 01:39 ..
-rw-------@  1 matt  staff   1392 Jul  4 23:32 ai.openclaw.gateway.plist
-rw-r--r--@  1 matt  staff    650 Jul  8 00:15 com.chrome.debug.plist
-rw-r--r--@  1 matt  staff    871 Jul  5 00:08 com.google.GoogleUpdater.wake.plist
-rw-r--r--@  1 matt  staff    181 Jul  5 00:08 com.google.keystone.agent.plist
-rw-r--r--@  1 matt  staff    181 Jul  5 00:08 com.google.keystone.xpcservice.plist
-rw-r--r--@  1 matt  staff    594 Jul  4 23:44 com.lwouis.alt-tab-macos.plist
-rw-r--r--@  1 matt  staff   1273 Jul  4 23:32 com.matthewmurphy.backup-launch-agents.plist
-rw-r--r--@  1 matt  staff    476 Jul  4 23:32 com.matthewmurphy.energy_monitor.plist
-rw-r--r--@  1 matt  staff    693 Jul  4 23:32 com.matthewmurphy.irig-watcher.plist
-rw-r--r--@  1 matt  staff    666 Jul  4 23:32 com.matthewmurphy.personal-sync.plist
-rw-r--r--@  1 matt  staff    668 Jul  4 23:32 com.matthewmurphy.rqbit.plist
-rw-r--r--@  1 matt  staff    786 Jul  8 05:44 com.mattmurphy.ai-os-rules-watcher.plist
-rw-r--r--@  1 matt  staff   1449 Jul  6 23:07 com.mattmurphy.userscript-bundler.plist
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
require("modules.keybindings")

-- ── Startup confirmation ─────────────────────────────────────────────────────────

hs.alert.show("⚙️  Hammerspoon config loaded")
