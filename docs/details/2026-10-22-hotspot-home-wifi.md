# Hotspot → home Wi-Fi watcher

## 15:25 Watcher built and live

Asked (via coordinator): Mac joined the iPhone hotspot instead of home Wi-Fi; both must stay auto-join. Check preferred order first, then build a watcher that rejoins home, with a subtle note and a retry knob.

---

### Preferred order already right

`networksetup -listpreferredwirelessnetworks en0`: `mdm` is #1, `Matt’s iPhone 14 Pro Max` #2. So reordering fixes nothing: macOS only uses the order when choosing a network, and never drops a working one for a higher-priority one. That's why it stuck on the hotspot.

---

### How it detects home

Hammerspoon has no Location access, so `hs.wifi` returns no SSIDs. Instead:
- current SSID from `ipconfig getsummary en0` (not redacted);
- nearby networks from `system_profiler SPAirPortDataType` (names redacted, but channel + security shown). While on home it learns home's fingerprint (now `157 (5GHz, 80MHz)|WPA2 Personal`, in `~/.hammerspoon/cache/wifi_home.json`). On the hotspot, a nearby network with that fingerprint = home in range.
- False matches can only happen near home (neighbours), where home is in range anyway. If the router changes channel, the fingerprint re-learns next time he's on home (hourly).
- Rejected: granting Hammerspoon Location (real SSID scans) needs Matt to change a privacy setting; optional upgrade later.

---

### How it switches

Wi-Fi power off for 2 s, then on; macOS rejoins the top visible preferred network (home). No password needed. Rejected `networksetup -setairportnetwork` (may need the password or pop a keychain prompt). Each switch is a few seconds offline, so attempts are at most every 5 min (`retry.cooldown`). Checks every 60 s (`retry.every`) and 15 s after any network change.

---

### Untested real switch

The Mac was on home the whole time, so the off/on switch and the note never ran for real. Tested: parser/decision unit tests, live dry run (learned the fingerprint). Undo: delete the `safeRegister("modules.wifi_home")` line in `~/.hammerspoon/init.lua`, or `git revert 0282371` there.
