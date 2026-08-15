# macOS System Profile (Auto-Generated)
## Storage & Volumes
Storage:

    Data:

      Free: 49.92 GB (49 922 920 448 bytes)
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

      Free: 49.92 GB (49 922 920 448 bytes)
      Capacity: 494.38 GB (494 384 795 648 bytes)
      Mount Point: /
      File System: APFS
      Writable: No
      Ignore Ownership: No
      BSD Name: disk3s1s1
      Volume UUID: B5C06BDF-F07E-4BF9-A578-BF57D084F689
      Physical Drive:
          Device Name: APPLE SSD AP0512Z
          Media Name: AppleAPFSMedia
          Medium Type: SSD
          Protocol: Apple Fabric
          Internal: Yes
          Partition Map Type: Unknown
          S.M.A.R.T. Status: Verified

## Active LaunchAgents
total 352
drwxr-xr-x@  39 matt  staff   1248 Aug 14 21:25 .
drwx------@ 104 matt  staff   3328 Aug 10 20:11 ..
drwxr-xr-x@  14 matt  staff    448 Jul 21 20:38 Archive
-rw-r--r--@   1 matt  staff    386 Jul 24 01:32 Messauto.plist
-rw-r--r--@   1 matt  staff    871 Jul  5 00:08 com.google.GoogleUpdater.wake.plist
-rw-r--r--@   1 matt  staff    181 Jul  5 00:08 com.google.keystone.agent.plist
-rw-r--r--@   1 matt  staff    181 Jul  5 00:08 com.google.keystone.xpcservice.plist
-rw-------@   1 matt  staff    905 Jul 19 23:51 com.matt.agent.agy-proxy.plist
-rw-r--r--@   1 matt  staff    656 Jul 11 16:22 com.matt.agent.agymcp.plist
-rw-r--r--@   1 matt  staff    864 Aug 15 00:23 com.matt.agent.ai-os-wiki.plist
-rw-------@   1 matt  staff   1158 Jul 10 16:39 com.matt.agent.backup-agents.plist
-rw-r--r--@   1 matt  staff    941 Aug 13 00:48 com.matt.agent.caddy.plist
-rw-------@   1 matt  staff    850 Jul 10 16:39 com.matt.agent.chrome-debug.plist
-rw-------@   1 matt  staff    957 Jul 10 16:39 com.matt.agent.energy-monitor.plist
-rw-------@   1 matt  staff    890 Jul 10 16:48 com.matt.agent.gemini-ingest.plist
-rw-------@   1 matt  staff   2513 Jul 19 18:35 com.matt.agent.hermes-gateway.plist
-rw-------@   1 matt  staff    894 Jul 10 16:39 com.matt.agent.irig-watcher.plist
-rw-------@   1 matt  staff    960 Jul 27 14:05 com.matt.agent.litellm.plist
-rw-r--r--@   1 matt  staff   1234 Jul 21 20:06 com.matt.agent.local-automation-server.plist
-rw-------@   1 matt  staff    959 Jul 10 16:39 com.matt.agent.notesync.plist
-rw-r--r--@   1 matt  staff    781 Aug  8 14:06 com.matt.agent.oracle-vps-mount.plist
-rw-r--r--@   1 matt  staff   1023 Aug 11 15:57 com.matt.agent.proxima-mcp.plist
-rw-r--r--@   1 matt  staff    933 Jul 24 15:03 com.matt.agent.qwerty-midi-bundler.plist
-rw-------@   1 matt  staff    889 Jul 20 01:49 com.matt.agent.rules-watcher.plist
-rw-r--r--@   1 matt  staff    864 Jul 29 12:57 com.matt.agent.turn-swap.plist
-rw-r--r--@   1 matt  staff    796 Aug 11 22:04 com.matt.devcachecleanup.plist
-rw-r--r--@   1 matt  staff    709 Aug 11 23:10 com.matt.sync-skills.plist
-rw-r--r--@   1 matt  staff   1481 Jul 27 20:21 com.mattmurphy.userscript-bundler.plist
-rw-r--r--@   1 matt  staff   1853 Aug  9 18:16 com.parantoux.hermes-webui.plist
-rw-r--r--@   1 matt  staff    427 Jul  4 23:32 com.pieces.os.launch.plist
-rw-r--r--@   1 matt  staff    747 Jul  4 23:32 com.samschott.maestral.maestral.plist
-rw-r--r--@   1 matt  staff    904 Jul 28 17:39 com.user.cm-pinner.plist
-rw-r--r--@   1 matt  staff    788 Jul 28 17:39 com.user.qbit-manage.plist
-rw-r--r--@   1 matt  staff    469 Aug  5 16:04 com.user.tmpdir.plist
-rw-r--r--@   1 matt  staff    854 Aug  6 22:57 com.valvesoftware.steamclean.plist
-rwxr-xr-x@   1 matt  staff    376 Jul 10 15:53 git-sync.sh
-rw-r--r--@   1 matt  staff    685 Jul  4 23:32 homebrew.mxcl.nginx.plist
-rw-r--r--@   1 matt  staff    474 Aug 10 17:02 io.mutagen.mutagen.plist
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

_G.activeWatchers = _G.activeWatchers or {}
local activeWatchers = _G.activeWatchers

-- Enable AppleScript and CLI (hs -c) control for instant reloading without app restarts
hs.allowAppleScript(true)
require("hs.ipc")

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

local ModuleManager = require("modules.module_manager")
require("modules.menu_bar")

ModuleManager.register(require("modules.right_command_raycast"))
ModuleManager.register(require("modules.keybindings"))
ModuleManager.register(require("modules.qwerty_midi"))
ModuleManager.register(require("modules.gemini_thread_search"))
