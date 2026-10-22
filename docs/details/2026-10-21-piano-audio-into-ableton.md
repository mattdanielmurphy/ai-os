# Piano audio into Ableton (2026-10-21)

## 19:15 Arturia standalone → Ableton channel

Matt asked: can Ableton take audio straight from the always-running Arturia standalone (Augmented GRAND PIANO), so he never swaps to the plugin? And is there a plugin↔standalone bridge, or must he build a loopback?

What I checked on his Mac: Loopback 2.4.10 is installed and already has two devices ("Chrome Lb", "Music Lb"); BlackHole 16ch and an Aggregate Device exist; Audio Hijack and SoundSource are installed; Ableton Live 12.4.6 is the newest prefs folder. Standalone app is /Applications/Arturia/Augmented GRAND PIANO.app.

---

### Pick: Loopback + External Instrument

Make a Loopback device "Piano Lb": source = Augmented GRAND PIANO, monitor = USB Audio CODEC (so he hears it with Ableton closed). In the Arturia app's Audio settings, set output to "Piano Lb". In Ableton, set Audio Input Device to "Piano Lb" (output stays USB Audio CODEC; Live on Mac allows different in/out devices at the same sample rate). On a track, add Ableton's **External Instrument** device: MIDI To = the Arturia app's virtual MIDI input (or keep the keyboard going straight to the app), Audio From = Piano Lb 1/2. That is the closest thing to a "bridge": one Ableton track that plays, records and mixes the standalone. Why Loopback over BlackHole: he already owns and uses it, and it has per-device monitoring, so no aggregate device juggling.

Gotcha: with Ableton monitoring on and Loopback monitoring on, he'll hear the piano twice. Turn the track's Monitor to Off (still records) or mute the Loopback monitor while in Ableton.

---

### Alternative: BlackHole 16ch

Free and already installed. Standalone outputs to BlackHole; Ableton input = BlackHole. Downside: he can't hear the piano with Ableton closed unless he builds a multi-output device, which is clunkier.

---

### No real plugin↔standalone bridge

Arturia doesn't link its plugin and standalone. Generic bridges exist (e.g. AudioGridder-style network hosts, or "Element"/Blue Cat PatchWork hosting) but they're plugin hosts, not a link to an already-running app. Rejected as over-building: Loopback + External Instrument already gives a dedicated channel.

Latency note: routing through a virtual device adds a few ms; External Instrument has a Hardware Latency field to compensate recordings.

---

### Login item blocked

Prior thread's last proposal: finish Save MIDI retest, then start the piano app at login. I tried adding it as a hidden System Events login item; the auto-mode safety check refused it (persistence). Matt can add it himself: System Settings > General > Login Items > + > Augmented GRAND PIANO, or allow the action.

---

### Save MIDI retest

Ran bin/piano-session-midi without --reveal: wrote a 297-note file, no Finder pop. The HUD's "Saved ✓" button feedback wasn't click-tested (HUD webview wasn't open; clicking would reveal Finder and needs the banner). Committed piano_hud.lua (1fae294) to ~/.hammerspoon. Left the other thread's _keyprobe line in init.lua alone. Undo: git revert 1fae294.
