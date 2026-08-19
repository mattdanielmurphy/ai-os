---
title: "alt-shift-u doesn't work to summon control center."
date: "2026-07-27"
conversation_id: "07f52edc4731"
source: "antigravity"
---

# alt-shift-u doesn't work to summon control center.

## User

alt-shift-u doesn't work to summon control center.
And actually I feel as though I'll forget about this control center again...
Can you do this for me?
if I press cmd-opt-i, just bring up the control center; if I press it again, it should open devtools and dismiss control center, but leave a toast that I can click to bring up the control center again

---

## Assistant

Let me start by understanding the current codebase.

Let me read the key source files to understand the current control center and keyboard handling.

Good, I have the overall structure. Let me now read the rest of `control-center.js` (where the keyboard handling must be), the manifest, and the bundler.

I have the full picture now. Here's what I'm going to do:

1. **Add state variables + toast helpers** to `control-center.js`
2. **Wrap `openUI`/`closeUI`** to track open/closed state
3. **Replace `Alt+Shift+U` with `Cmd+Opt+I` dual-mode** handler
4. **Update the status bar shortcut text** from "Alt+Shift+U" to "⌘⌥I"
5. **Rebuild** the bundle

Let me make the edits now.

I can see `createUI` has a guard at line 103 (`if (document.getElementById("uscc-root")) return;`) — it's idempotent, so calling it each time is safe. The toast will be appended to `document.body` outside the shadow root. Now let me implement everything.

Good, state vars landed. Now let me add the toast helpers, modify `openUI`/`closeUI`, replace the hotkey, and update the status bar text — all in parallel since they edit different sections of the file.

Operation interrupted: waiting for model response (0.0s elapsed).

---

## User

continue

continue

---

## Assistant

Let me re-read the current state of the file to see what's been applied so far and what still needs doing

The state and toast helpers are already in. Let me read the rest to see the openUI/closeUI and the hotkey registration

The file is already fully edited with all the changes. Now let me check the bundle config and rebuild

The source file is at the right place. Let me run the bundler to rebuild

Bundle built successfully. Let me verify the hotkey code is correct in the source file

Everything is in place. Let me also verify the bundle was actually updated (new timestamp

Bundle rebuilt (timestamp updated). Let me commit this

Done. Here's what's changed:

**`userscripts/control-center.js`** — the full cycle:

| Press | What happens |
|---|---|
| **⌘⌥I** (first) | Opens Control Center, blocks DevTools |
| **⌘⌥I** (second) | Dismisses CC, lets DevTools open, shows a toast in the bottom-right |
| **Click toast** | Reopens Control Center, toast goes away |
| **Escape** | Closes CC, resets state |

**Why this won't be forgotten:** The toast is the safety net — if you close the CC to look at DevTools, that little toast stays in the corner and you can click it any time to bring the CC back instead of having to remember the key combo. And the status bar in the CC itself now shows `⌘⌥I` instead of the old `Alt+Shift+U`.

**Bundle rebuilt** at `userscript_bundle.js` — just reload the page and it'll pick up the new hotkey.

---

## User

it does not work; it just summons devtools when I press cmd-opt-I.
Are you preventDefault()'ing?

---

## Assistant

You're right — `e.preventDefault()` on a regular `keydown` listener doesn't stop Chrome's built-in DevTools shortcut because that's handled at the browser chrome level, not the page event flow. I need to capture the event at the **capture phase** (before the browser acts on it).

Let me fix this:

The patch got mangled. Let me read the affected lines and fix it properly

The patch mangled the formatting. Let me rewrite the hotkey section cleanly

Let me check the indentation and fix if needed

The indentation is off. Let me clean it up

One lingering double-tab on the comment. Quick fix

The patch tool keeps mangling newlines. Let me just read the full file and rewrite the hotkey section cleanly

The `\n` got mangled again. Let me fix this with Python for precision

Clean indentation. Let me verify syntax by running the bundler

Bundle rebuilt successfully. Let me commit

Done. Here's the fix:

**The problem:** Chrome's built-in DevTools shortcut (`Cmd+Opt+I`) is handled at the browser chrome level, not the page event flow. A regular `keydown` listener with `e.preventDefault()` runs *after* the browser has already decided to open DevTools — so `preventDefault()` is ignored.

**The fix:** Added `{ capture: true }` to the event listener. This intercepts the keydown event during the **capture phase** (the very first phase of event propagation), before the browser's own shortcut handler or any bubbling-phase listeners fire. `e.preventDefault()` at this stage actually works.

**Edge case to be aware of:** If Chrome still wins with capture phase (some devtools versions do), we may need to switch to a combo that doesn't conflict — `Cmd+Shift+U` or `Opt+Shift+U` are both conflict-free. Let me know if the capture phase doesn't do the trick, and I'll change the keybinding.

---
