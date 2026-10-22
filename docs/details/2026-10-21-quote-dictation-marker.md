# Quote tool: dictation marker

## 18:32 Visible marker after the quote
- Ask: Claude dictation strips leading whitespace, so the dictated comment merged into the "> quote". Insert a visible character after the quote + newline.
- Did: `~/.hammerspoon/modules/quote_comment.lua` now inserts `> quote\n\n↳ ` (new `M.marker`). When ⌥R moves the box to the queue and nothing was dictated, the dangling `↳` is stripped.
- Why `↳`: reads as "reply to the quote", works even if dictation also eats the space after it (`↳hello`). Rejected text like "Me:" (noisy in every message).
- Tested: stripping logic in lua, syntax check, Hammerspoon reloaded and marker loaded. Not tested on screen with real dictation.
- Undo: set `marker = ""` or revert the commit in ~/.hammerspoon.
