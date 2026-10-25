# Wake mute: skip at home (2026-10-25)

## 19:30 Only auto-mute away from home

**Asked:** the wake auto-mute always muted; mute only when Matt is not at his apartment.

**Where:** `~/.hammerspoon/modules/wake_mute.lua` (mutes after >10 min asleep/locked).

**Home signal:** Wi-Fi SSID `mdm`, already the `net.home` knob in the "Wi-Fi home" tweaks (⌃⌥⌘T). Read via `ipconfig getsummary en0` (no Location permission needed), reusing `modules/wifi_home.lua`.

**Rules:**
- On `mdm` → home, no mute.
- On the iPhone hotspot but home's network fingerprint is nearby → home (wifi_home will switch back anyway).
- Any other network, or no Wi-Fi → away, mute.
- Right after wake Wi-Fi may still be joining (no SSID): re-check every 2 s up to 6 times, then mute if still unknown (safe side for classrooms).

**Code:** new `wifi_home.isHome` (pure, tested) and `wifi_home.atHome(cb)`; `wake_mute.muteUnlessHome`.

**Tested:** unit tests pass; live home check returned `true mdm`; ran the wake path at home with clearance, audio stayed unmuted. **Not tested:** the away path for real (the mute call itself is unchanged).

**Rejected:** mute-then-unmute-if-home (flicker, and could unmute something Matt muted himself); GPS/location (Hammerspoon lacks Location access).

**Undo:** revert the commit in `~/.hammerspoon`.
