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

## 23:00 Less detail, layered Readthrough

You wanted details files shorter and less technical, with more detail only when you ask for it, and the Readthrough to open and start talking by itself when a reply lands.

- Saved as a global rule: medium detail by default, no back-end talk unless asked, deeper bits in a "More" layer.
- The float now opens wider (640 px). Once you resize it, it keeps your size.
- The player's own settings sit behind its "Tune" button (bottom right), not in the ⌃⌥⌘T panel yet. Bringing them into the panel is part of the plan below.
- Planned player behaviour is waiting for your 👍 (see the reply).

## 23:09 The Readthrough now talks you through each reply

When an agent replies, the float opens on the newest reply and starts talking right away. You don't need to press anything. It no longer reads out the page title or the headings, just the text, so it sounds more like someone explaining.

Each part has a small "Hold Enter for more detail" button. Hold Enter, or click it, and that part's extra detail opens and gets read out next. Right arrow and the other keys work exactly as before.

If a new reply lands while it's still reading, the new one waits and starts when the current one finishes. Switching threads pauses it.

#### More

This section is itself a test of the new layout: you're hearing this only because you asked for more. Agents write the extra layer under a "More" heading, and it stays folded until you ask. Pages published before tonight keep the old behaviour until they're published again.

Not tested yet: whether the float can start sound on its own without a first click. If it can't, you'll see "Tap anywhere to start reading" the first time.
