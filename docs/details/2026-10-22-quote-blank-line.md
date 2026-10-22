# Quote tool: blank line before the comment

## 21:25 Blank line between quote and ↳ comment

Matt asked: the ⌥R commenter must leave a blank line between the quote and the comment, or markdown folds the whole thing into the blockquote.

---

### Cause found

The first insert already pastes `> quote\n\n↳ `. The blank line is lost when Return saves the comment to the queue: the text is read back from the box's AXValue, which drops empty paragraphs, so the queue stores `> quote\n↳ comment`. Final send pastes that, and markdown's lazy continuation pulls the ↳ line into the quote.

---

### The fix

`spaceComment()` in `~/.hammerspoon/modules/quote_comment.lua` rewrites any run of newlines before a `↳` line to exactly one blank line. Applied in `itemText()`, so it fixes items already in the queue too. The ↳ marker stays. Rejected: fixing it at save time only (old queued items would still be broken).

---

### Testing and risk

Plain-Lua unit test of the function (4 cases) passed; module hot-reloaded (`_spaceComment` present). Not tested on screen. A follow-up `hs -c` check hung (Hammerspoon busy); left running, not killed. Undo: `git revert 885eca3` in ~/.hammerspoon.
