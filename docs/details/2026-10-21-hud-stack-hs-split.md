# HUD stack and Hammerspoon split (2026-10-21)

## 20:40 Is HS too central, and what should HUDs be built with?

Matt asked (via coordinator): is his "Save to Dock = WebKit, lighter than Electron" idea right, what's the lightest/fastest way to make floating HUD apps, why were past builds slow/big, and how to stop one Hammerspoon edit reloading every utility. Decision stage only; nothing built.

What I checked on his Mac: `~/.hammerspoon/init.lua` (auto-reload), `modules/module_manager.lua`, sizes of his built apps, `tauri-monorepo` and `music-companion` contexts, his Aug 13 Gemini threads "Tauri Slow Initial Startup Optimization" and "Monaco Editor in Wails/Tauri" (via QMD).

---

### webkit hypothesis verdict

Mostly right. Safari "Add to Dock" web apps and any WKWebView app use the system WebKit framework that ships in macOS. They do not need Safari open or even used; being a Chrome user doesn't matter. Electron bundles its own Chromium per app (300-400 MB each; his Proxima.app is 405 MB, Hermes.app 313 MB).

But Save-to-Dock apps are just websites in a window: no always-on-top, no click-through, no hotkeys, no file/system access. So they don't solve HUDs. The useful part of the idea is "use system WebKit", which Hammerspoon's `hs.webview`, Wails, Tauri and a tiny Swift app all already do.

---

### measured app sizes

From `du` on his Mac:
- TrackpadMixer.app (Swift): 544 KB
- TypedRecall.app (Swift): 1.5 MB
- music-companion.dev.app (Wails v3, Go): 23 MB
- tauri-monorepo folder: 770 MB (mostly Rust `target/` build cache + node_modules)
- Proxima.app / Hermes.app (Electron): 405 / 313 MB

---

### why past builds were slow

- Tauri: Rust compile. First build pulls and compiles hundreds of crates (minutes, GBs of `target/`); incremental rebuilds still tens of seconds. His Aug 13 Gemini thread hit exactly this and Gemini pointed him to Wails.
- Wails: Go builds fast, but you still carry the Go runtime (~10-20 MB) plus a Vite/React frontend build and node_modules. Fine, but heavy for a 200-line HUD.
- Both add a JS bundler step and a framework layer you don't need for one floating panel.

---

### hud options

1. Swift NSPanel (his trackpad-mixer pattern). ~0.5 MB, a few seconds of `swiftc`, ~10-20 MB RAM, full control (always-on-top, click-through, all Spaces). Can host a WKWebView inside if he wants HTML/CSS UI. Already reads `hud_slots.json`. Pick.
2. Keep HUDs in Hammerspoon `hs.webview` but make reloads per-module (below). Zero new apps; same WebKit; downside is they share HS's process and its crashes.
3. Wails v3. Only worth it if a HUD grows into a real app with a Go backend and lots of UI. Tauri: skip (Rust build cost is what he hated). Electron: skip.

Rejected: Save-to-Dock (can't float), Electron (size), Tauri (build time). SwiftUI-only HUDs are fine too, but NSPanel + WKWebView lets him keep writing HTML.

---

### hs reload options

Root cause: `init.lua` line 46 watches all of `~/.hammerspoon/` and calls `hs.reload()` on any save (1.5 s debounce). `hs.reload` restarts the whole Lua state, so every module stops and starts.

1. Per-module hot reload (pick, smallest step). In the pathwatcher, if every changed file is `modules/<id>.lua`, call that module's `stop()`, clear `package.loaded["modules.<id>"]`, `require` it again, re-register, `start()`. Only `init.lua` or shared libs trigger a full reload. `module_manager.lua` already has per-module `start/stop`, so this is ~30 lines. Risk: modules that leak timers/hotkeys outside `stop()` will double up; fix those as found.
2. Move heavy/fragile utilities out of HS into their own small Swift processes run by launchd, like trackpad-mixer and ps5_bridge already are. Each restarts alone. Good for the big ones (piano HUD, ps5 dashboard), not worth it for 20-line hotkeys.
3. Multiple Hammerspoon instances. Possible (copy the app, change bundle ID, point it at another config dir) but each copy needs its own Accessibility/Input Monitoring grants, a second menu bar icon, and event taps can fight. Not recommended.

Untested: nothing was built. Undo: nothing to undo.

## 20:46 Built: per-module Hammerspoon hot reload

Matt 👍'd the pick (per-module reload first, Swift HUDs for new ones).

What changed (`~/.hammerspoon`, commit 388576a):
- `modules/module_manager.lua`: `ModuleManager.reload(id, path)` calls the old module's `stop()`, clears `package.loaded`, re-requires, and `start(true)`s it if enabled. Returns false (→ full reload) if the module has no `stop()`, fails to load, or fails to start.
- `init.lua`: the pathwatcher now collects changed files over the 1.5 s debounce. If every one is a loaded module (`suite.pathOf`), only those are swapped; anything else (init.lua, module_manager, suite, hud_layout, modules without stop) still does `hs.reload()`.

---

### hot reload test

Set `_G.hotMarker`, touched `modules/eye_breaks.lua` then `modules/song_key.lua`: marker survived (no full reload), console shows `↻ hot-reloaded eye_breaks` / `song_key`, module still enabled. Touched `init.lua`: marker gone (full reload, as intended).

---

### hot reload risk

A module whose `stop()` doesn't undo everything `start()` made (hotkeys, event taps, timers, canvases) will end up with duplicates after a hot reload. I didn't audit all ~25 modules' `stop()`. If something double-fires after an edit, fix that module's `stop()`, or use the menu's full reload. Modules without `stop()` (gemini_thread_search, turn_swap…) always full-reload.

Left alone: another session's uncommitted `_keyprobe` TEMP line in init.lua (not included in my commit).

Undo: `git -C ~/.hammerspoon revert 388576a`.

## 21:16 Self-cleaning hot reload + the crash

Matt: "I have no memory" — so double-firing must be caught by the system, not by him noticing. (His sticky-notes/shortcut-tutor idea went to a separate thread per the coordinator.)

---

### leak sweep

`module_manager.lua` now wraps the constructors for hotkeys, key/event taps, timers, canvases, webviews, pathwatchers, tasks and app/screen/usb/caffeinate watchers. While a module's `start()` runs, everything it creates is recorded. On hot reload, after the old `stop()`, anything still active is logged (`⚠️ hot reload leak` in the console + `~/.hammerspoon/cache/hot_reload_leaks.log`) and stopped/deleted, so the new copy can't double up. Tested: a fake module that leaked a repeating timer was caught and cleaned; eye_breaks, song_key and claude_warm hot-reloaded with no leaks and Hammerspoon stayed up. Not covered: objects created at require time or later inside callbacks; hotkeys can't report "enabled", so they're deleted silently rather than logged.

---

### crash cause

Hammerspoon crashed at 20:57:38 (crash report: SIGTRAP in `ipc_sendMessage`). My checks wrapped `hs -c` in a perl alarm; when one timed out, the CLI process died and Hammerspoon crashed sending the reply to its dead port. AG_CONTEXT actually recommended that alarm pattern, so other agents would hit it too. Fixes: init.lua now skips replies to ports already invalid (narrows it, not proven to catch every race: I didn't re-run the crash on purpose); AG_CONTEXT now says never kill an `hs -c` client, run slow checks in the background instead. Matt relaunched Hammerspoon after his 👍.

Commit 79f06a6 in ~/.hammerspoon. Undo: `git -C ~/.hammerspoon revert 79f06a6`.
