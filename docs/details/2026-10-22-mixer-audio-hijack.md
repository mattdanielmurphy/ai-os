# Mixer vs Audio Hijack

## 09:45 Make the mixer and Audio Hijack coexist

Asked: the trackpad mixer seems to stop Audio Hijack capturing apps; make them coexist.

---

### Cause found

The mixer uses Core Audio process taps with `muteBehavior = .mutedWhenTapped` (Sources/Taps.swift): each tapped app is muted at the source and its audio is replayed from TrackpadMixer at the channel gain. Audio Hijack (via Rogue Amoeba's ARK driver) captures the app itself, so it gets the muted stream. Inferred from the code; not confirmed with a recording.

---

### Fix shipped

- While Audio Hijack is running, every app in its saved sessions (currently Music and Claude) is left untapped, and excluded from the System tap too. Read from Sessions.plist, cached by mtime; refresh on Hijack launch/quit (NSWorkspace notifications) plus the existing 2s sweep.
- Rogue Amoeba apps (`com.rogueamoeba.*`) are always bypassed, so Hijack's own output isn't re-routed.
- Trade-off: those apps get no mixer volume control while Hijack is open. Rejected: keeping taps and capturing from TrackpadMixer instead (loses per-app capture); bypassing all apps while Hijack is open (too broad).
- Log line on change: "Audio Hijack open: leaving [...] alone".

---

### Restart bug

The first restart left the mixer not running for about a minute (exit 75 hand-over, launchd's KeepAlive didn't relaunch), so the output stayed muted until I kickstarted it. `scripts/restart-mixer` now waits up to 3s for a new process and kickstarts the job itself. Retested: clean restart.

---

### Untested

Matt hasn't yet recorded Music or Claude with Hijack after the fix.

Undo: revert the commit and run scripts/restart-mixer.
