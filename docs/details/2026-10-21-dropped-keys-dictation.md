# Dropped keys and Claude dictation freeze (2026-10-21)

## 15:40 Typing froze for seconds
- Asked: keys dead for seconds; Claude dictation freezes the app.
- Cause found: Hammerspoon's key taps run on its main thread. song_key polled `hs.application.get("Spotify")` every 4 s; with Spotify closed that falls back to AX-scanning every window of every app (100-260 ms, seconds if an app is hung). ps5_dashboard polled the focused text field every 0.3 s while the controller was idle.
- Fix: bundle-ID lookups, osascript off the main thread, idle-skip in ps5, global AX timeout 0.5 s (init.lua). Measured 25 stalls (250-1700 ms) in 6 min before, 0 in 90 s / 300 keys after.
- Rejected: blaming keyboard battery (stalls matched Hammerspoon exactly; K850 battery not readable via the Logitech receiver).
- Undo: revert ~/.hammerspoon commits 1658fd2, 2a8240d; ps5 repo f2ce11d.

## 15:56 Dictation freeze capture
- `scripts/claude_hang_capture.py` (running in background) samples Claude when the mic is requested or the webview hangs; output in ~/projects/ai-os/tmp/claude-hang/.
- Claude's log: 4 "Main webview is unresponsive" today, ~18 s after mic start. None since 15:34 (dictations at 16:07, 16:54 were fine).
- Likely factor: memory pressure (8.5 GB swap). Unconfirmed.

## 16:15 Memory and shelved services
- Stopped and `launchctl disable`d: hermes-gateway, hermes-webui, agy-proxy, agymcp, litellm, aios-server; killed orphan agy hub. Revive steps in shelf/INDEX.md.

## 16:17 Nightly restart
- `com.matt.agent.nightly-restart` runs scripts/nightly_restart.sh 04:30-05:45 (15-min retries). Skips outside 04:25-06:00, if up < 3 h, or while Claude holds its "Electron" keep-awake assertion (a turn running).
- Restart via loginwindow `aevtrest` (apps with unsaved work cancel it). Untested for real until tonight. Auto-login declined (security); FileVault is off, recommended on.
- Undo: `launchctl bootout gui/$(id -u)/com.matt.agent.nightly-restart`.

## 17:10 Freezes during Hammerspoon reloads
- Cause: a reload ran all module starts synchronously (2.4-3 s) with key taps already live; two hs.window.filter users (keybindings CloudMounter nag, quote_comment badge) scanned every app (~1.9 s).
- Fix: debounced reload (1.5 s, ignores tests/tmp/archive), one module per run-loop turn with slow-start logging, per-app uielement watchers. All modules now start in ~0.2 s, max step 63 ms. Commit 21668a6.

## 17:50 Confirmation test
- Probe (`modules/_keyprobe.lua`, temporary, loaded from init.lua) logged key latency. Reload phase: 91 keys from 1 s after reload, all < 5 ms. Freeze phase didn't run (hs -c hung under the IPC; killed by alarm), so the "busy Hammerspoon = frozen keys" mechanism is still not directly confirmed in this test (it was correlated earlier: 421 ms stall ↔ 318 ms key latency).
- Open: remove the probe line from init.lua and modules/_keyprobe.lua after the rerun.
