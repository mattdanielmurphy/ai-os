# Platform-Agnostic Capture & Comment (Deferred)

> [!NOTE]
> **Status**: Parking Lot / Future Possibility Only.
> The Hammerspoon quote-comment module is disabled and archived. It is kept as a reference for a redesign, not as an active tool.

---

## Goal

Highlight text anywhere (a Claude reply, a browser page, a PDF, a doc), add a short comment, and bundle the quote plus comment for pasting into a later prompt. Matt wants this option available "for some situation in the future."

## Why It Is Parked

- The archived module is Hammerspoon-only and tied to the Claude composer (it injects into the Claude.app input).
- Cross-app value needs a platform-neutral capture path, so the composer-specific design does not carry over.

## Reference

- Archived module: `~/.hammerspoon/archive/quote_comment.lua` (committed in the Hammerspoon repo, commit `307483d5`)
- Original design doc: `docs/handoffs/2026-10-17_quote-comment-tool.md`

## Smallest Viable Version

- One hotkey script: grab the current selection, prompt for a comment, append both to a persistent clipboard stack.
- No composer injection. Works in any app that supports copy.
- Paste the stack into any thread when needed.

## Reconsideration Threshold

Revisit when Matt repeatedly copies quotes into prompts by hand and the manual copy-paste becomes the bottleneck.
