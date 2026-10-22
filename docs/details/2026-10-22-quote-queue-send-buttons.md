# Quote tool: Queue vs Send buttons (2026-10-22)

## 14:35 Queue ⏎ / Send all ⌘⏎ buttons

Matt asked (via coordinator): make it obvious that Return in the ⌥R quote tool queues rather than sends; ideally two buttons, Queue (default, Return) and Submit (⌘Return).

---

### Bar replaces the pill

The old "❝ N queued" pill (`~/.hammerspoon/modules/quote_comment.lua`) is now a bar: `[❝ N queued] [Queue ⏎] [Send all ⌘⏎]`. It shows while a quote + comment is in Claude's box or anything is queued (before, only when the queue was non-empty, so the very first quote showed nothing). Fixed widths, so the count changing never shifts the buttons. Pill click still opens the menu (insert now / show / remove last / clear). Queue is dimmed when there's nothing in the box to queue; Send's label then reads "Send all ⏎" because plain Return sends in that state.

---

### Command Return sends everything

New: ⌘Return in Claude's box queues a quote + comment still in the box (stopping dictation first) and sends the whole queue. Before, ⌘Return was ignored by the tool. With nothing queued or pending, or a "/" command, ⌘Return passes through to Claude untouched. Plain Return behaviour is unchanged.

---

### Clicks not tested

Rendering is tested (drawn off screen to an image). Clicking the buttons wasn't, since that's input on Matt's screen. Risk: if a click pulled focus away from Claude, the bar would hide. hs.canvas normally doesn't take focus, so it should be fine.

---

### Tweak knobs

`~/.hammerspoon/tweaks/quote_comment.json` / ⌃⌥⌘T panel, "Quote comments (⌥R)": bar.right, bar.bottom, bar.height, bar.gap, bar.text, look.accent, look.alpha, look.dimAlpha.

Undo: `git -C ~/.hammerspoon revert 4f4cc90`.

## 14:40 No terracotta

Matt's message also said never use terracotta again. The bar's pill used #c96442 (the old badge colour, Claude's terracotta). Changed the default to deep teal #2b5f75 in code and tweaks/quote_comment.json. Other terracotta across his apps is handled in another thread.

## 14:58 Return sent instead of queueing

Matt queued a comment, typed body text, highlighted again, dictated, hit Return: everything was sent.

---

### Draft text caused it

Not a double Return (or not only). With body text in the box, ⌥R adds the quote *below* the draft. The old check only counted the box as "a quote + comment" if the whole box started with ">", so with a draft on top Return took the "send the queue" path. Fixed: `splitComment` finds the last "> quote" block followed by the ↳ line at the end of the box; Return queues just that block and puts the draft back (select all, delete, paste draft, clipboard restored). Unit-tested on 6 box shapes (tmp/split_test.lua). A box ending in a ↳ comment that spans several lines still counts as one comment (can't tell a multi-line comment from body text typed under it).

---

### Double Return guard

New knob `send.guard` (1.5 s, Tweaks panel): a plain Return within that time of queueing a comment is swallowed instead of sending. ⌘Return still sends immediately. A second Return while the first is still queueing no longer queues the draft as a comment.

---

### Not tested live

The full flow (dictation, draft restore) wasn't run on screen; that needs Matt's input. Undo: `git -C ~/.hammerspoon revert HEAD`.
