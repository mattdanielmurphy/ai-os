# Mic blocked, dictation failing (2026-10-21)

## 20:30 Root cause and fix

Matt: dictation fails in TypeWhisper (gracefully) and Claude (freezes); "like my microphone is held up".

---

### Orphaned audio taps

- coreaudiod was at 130-220% CPU, logging `StartIOThread ... Error: 0x3C` (timeout) and failed power assertions hundreds of times a minute. New mic IO couldn't start, so dictation failed.
- 24 `audiotee` processes (Core Audio process-tap CLI) were running, all orphaned (parent = launchd). They come from `~/.hammerspoon/bin/song-key-listen`, the song-key pill's ear listener, which Hammerspoon starts/stops whenever the pill shows or the source app changes (a plain + a `--app Music` copy each time).
- Repro: SIGTERM to song-key-listen left audiotee alive. audiotee ignores SIGTERM and SIGINT; only SIGKILL stops it. The script's handler used `ff.terminate()`.
- pmset also showed coreaudiod holding mic contexts for dead PIDs (likely the crashed Claude dictation helper, TypeWhisper) — leftover state from the wedge.

---

### Leak fix (live)

- `song-key-listen`: `ff.kill()` (SIGKILL) instead of `terminate()`. Tested: SIGTERM to the script now leaves no audiotee.
- `modules/song_key.lua`: `stopListener` SIGKILLs the task's children before terminating it, and `startListener`/`stopListener` reap any audiotee whose parent is launchd (covers Hammerspoon reloads / python being killed).
- Killed all 24 orphans, reloaded Hammerspoon. Committed 5f39628 in ~/.hammerspoon.
- Undo: `git revert 5f39628` in ~/.hammerspoon.

---

### Restart coreaudiod

- After the orphans were gone coreaudiod stayed at ~130% CPU with the same errors: its internal state is already wedged. Restarting it needs sudo, which I can't do: `sudo killall coreaudiod` (audio drops for ~2 s, apps reconnect). A reboot does the same.
- Untested: whether dictation works after that restart.
- Rejected: disabling the song-key pill entirely — the leak is fixed, so no need.
