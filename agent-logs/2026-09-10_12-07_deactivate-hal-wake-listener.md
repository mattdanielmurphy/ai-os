# Agent Log: Deactivate Hal Wake Word Listener & Put Hal Back to Sleep

## Context & Problem
The user requested putting "hal" back to sleep as it is not ready for prime time yet.
Investigation confirmed that `services/wake-hal/hal_listener.py` was running continuously in the background under LaunchAgent `com.aios.wake-hal` (PID 4107). It had actively recorded microphone audio and falsely triggered on speech earlier during the day, invoking `triage-launcher.sh` / `triage_router.py` with the HAL-9000 persona and voice synthesis.

## Changes Made
1. **Unloaded Background Service via Launchctl / `la`**:
   - Executed `~/.local/bin/la unload wake-hal` (`launchctl unload -w ~/Library/LaunchAgents/com.aios.wake-hal.plist`).
   - Verified process PID 4107 terminated immediately and confirmed `launchctl list` no longer contains `com.aios.wake-hal`.
   - Confirmed `launchctl print-disabled gui/501` persistently marks `"com.aios.wake-hal" => disabled`.

2. **Hardened Plist Configuration**:
   - Modified `~/Library/LaunchAgents/com.aios.wake-hal.plist` to set `<key>Disabled</key><true/>`, `<key>RunAtLoad</key><false/>`, and `<key>KeepAlive</key><false/>` to prevent inadvertent reload across system boots.

3. **Registered in `la` Launch Agent Manager**:
   - Added `"wake-hal": (USER_AGENTS / "com.aios.wake-hal.plist", "user")` to `KNOWN_AGENTS` in `~/.local/bin/la` so its unloaded state is transparently visible in `la list` (`✕ wake-hal unloaded`) and controllable via `la load`/`la unload`.
