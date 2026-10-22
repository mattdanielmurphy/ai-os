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
