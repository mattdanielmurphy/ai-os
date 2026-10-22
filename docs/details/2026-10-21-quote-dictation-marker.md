# Quote tool: dictation marker

## 18:32 Visible marker after the quote
- Ask: Claude dictation strips leading whitespace, so the dictated comment merged into the "> quote". Insert a visible character after the quote + newline.
- Did: `~/.hammerspoon/modules/quote_comment.lua` now inserts `> quote\n\n↳ ` (new `M.marker`). When ⌥R moves the box to the queue and nothing was dictated, the dangling `↳` is stripped.
- Why `↳`: reads as "reply to the quote", works even if dictation also eats the space after it (`↳hello`). Rejected text like "Me:" (noisy in every message).
- Tested: stripping logic in lua, syntax check, Hammerspoon reloaded and marker loaded. Not tested on screen with real dictation.
- Undo: set `marker = ""` or revert the commit in ~/.hammerspoon.

## 18:38 How queuing works
- Matt confirmed the ↳ marker works; asked how to queue.
- Answered from modules/quote_comment.lua header: ⌥R on the next highlight moves the box (quote + comment) to a hidden queue and starts a fresh quote; plain Return sends queue + box together; ⌥⇧R queues with no comment; ⌥⌘R puts the queue back in the box without sending; "❝ N queued" pill has Remove last / Clear. Not tested on screen by me.

## 18:44 New flow: Return saves the comment
- Matt's test: quotes piled up in the box instead of queuing, and no pill showed. Likely cause: on ⌥R the tool checks the previous box element is still "alive"; Claude's web composer seems to get re-created, so the check fails and the next quote is appended below as if the box held a draft. Not confirmed.
- Matt wants: Return after a dictated comment saves quote+comment to the queue and clears the box (pill shows); later, his final Return sends with all quotes inserted above what he typed.
- Plan: decide by box content, not the element: box contains a "↳" comment line → Return = queue + clear; otherwise queue non-empty → Return = insert queue above and send. Restated to Matt before building (multi-state logic rule).

## 18:52 Built: Return saves the comment
- Matt 👍'd the plan.
- `quote_comment.lua`: new `isComment(text)` (box starts with ">" and has a "\n↳" line) and `queueBox` (strip dangling ↳, queue, ⌘A+Delete). Return tap: comment in box → `saveComment` (settle = ⌘D stop if dictating, wait for text, queue, clear), swallowing Return so nothing sends. No comment + queue → old flush-and-send. ⌥R now checks the target box's text instead of `alive(prev element)`, fixing the pile-up.
- Tested: detection on 5 sample strings, syntax, reload. Not tested on screen.
- Risks: if the "is dictation listening" check misses (it looks for a stop/recording button), dictation isn't stopped and late words could land in the cleared box. A draft above a quote isn't treated as a comment, so Return sends it as before.
- Undo: `git revert` the commit in ~/.hammerspoon.
