# Audio Hijack recording vs trackpad-mixer

## 00:00 Recording still silent: mixer now steps aside fully

### What Matt said
"sadly recording does not work in AH" after the earlier fix (leave Audio Hijack's session apps untapped while a session runs).

---

### Session source is the mixer
His "Input Device" session in `~/Library/Application Support/Audio Hijack 4/Sessions.plist` now uses TrackpadMixer itself as the source app (changed 23:26). The mixer excludes itself from taps already, so the old "leave session apps alone" logic did nothing for that session. And with taps off, the mixer plays nothing, so recording it is always silent. The source must be the real app (Music, Chrome) or System Audio.

---

### New behaviour
`Sources/Taps.swift`: while an Audio Hijack session runs (Audio Hijack or arkaudiod running Core Audio I/O), the mixer stops every tap, so every app plays natively and Audio Hijack can capture anything. Removed the Sessions.plist parsing. Rejected: keeping per-app bypass (already failed for Matt, and breaks whenever he picks a new source).

---

### Trade-off and untested
No mixer faders while recording; apps play at their own volume. Not tested with a real Audio Hijack recording (needs clicking in its UI); built, restarted, mixer back and tapping normally.

---

### Undo
`git revert` the commit "Mixer steps aside fully while Audio Hijack records" in ~/projects/trackpad-mixer, then `./build.sh && scripts/restart-mixer`.
