# Readthrough float

## 22:55 First version

### What was asked
Readthrough opens by itself in a floating window tied to Claude's window, per thread, closable, with tweak knobs.

### How it works
- `~/.hammerspoon/modules/readthrough_float.lua`: a small standard utility window (native drag, resize, close button; Esc closes when focused), placed over the right of Claude's window (never the sidebar), frame remembered. Shows only while Claude or the float is in front. Per thread: switching hides it, switching back reshows it, closed stays closed until the next publish. Knobs in ⌃⌥⌘T "Readthrough float" (width, height share, right/top offsets, fade in/out).
- Thread detection: new ai-os mod `mods/visible-session`. The desktop app only draws a thread's prompt band while that thread is on screen, so the mod writes the session id to `~/.hammerspoon/tmp/claude_visible_session` and calls `visible(id)` on change. Window title is just "Claude" and walking Claude's AX tree is far too slow (it hung Hammerspoon), so both were rejected.
- Publish signal: asked the readthrough-hook session to call `hs -c 'require("modules.readthrough_float").published(url, sessionId)'` after each publish.

### Untested / risky
- Hammerspoon crashed at 22:43 during my AX probe (before the new module loaded) and is not running; it needs relaunching. The float itself has not been seen on screen yet.
- Mod loads in new/restarted Claude sessions; unverified that band renders fire on every thread switch.
- No shared Lua HUD-movement module exists (hud-kit is Swift), so it uses a native window for drag/resize; no snap-to-centre.

### Undo
Remove the `safeRegister("modules.readthrough_float")` line in `~/.hammerspoon/init.lua`; delete `mods/visible-session`.
