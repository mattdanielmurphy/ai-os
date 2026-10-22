# Fix expiry notification

## 15:30 Goes-cold toast: title and click

Asked (via coordinator): the "thread expiring" notification showed a long path instead of the thread title, and clicking it didn't open the thread.

---

### Where the toast lives

Not the context-alert mod: it's the Hammerspoon keep-warm nudge, `~/.hammerspoon/modules/claude_warm.lua`, fed by `scripts/warm_threads.py` (scans transcripts) and shown by `modules/claude_notify.lua`. So no Claude app restart is needed; I hot-swapped the module in the running Hammerspoon.

---

### Title showed a path

Project threads with no custom title, label or status header fell back to the first prompt's first 60 characters. Wakes with an image start with `@"/Users/matt/.claude/uploads/…"`, so that path became the title. Now: title order is custom title → thread label (`set_thread_label`) → AI title → status checklist header → cleaned first message (attachment paths and the wake/relay envelope stripped, HTML entities decoded).

---

### Click opens the thread

The toast never had a `url`, so a click only dismissed it. The scanner now finds each project thread's root id (from the wake envelope's `<thread ts="cmsg_…">`, or a `reply` tool's result) and the project id, and returns the same `claude://claude.ai/epitaxy/project/<chan>?thread=<cmsg>` link claude-control `--thread` uses. With several threads in one toast, the click opens the soonest. Code-tab sessions still get no link (no known mapping from transcript to app session id).

Rejected: grepping any `cmsg_` in the transcript; tool output and test fixtures contain other threads' ids (caught it picking another thread's id).

---

### Tested

Lua unit test (url passthrough) and a Python test (`tests/test_warm_threads.py`: path stripped, link built) pass. Live scanner run: every project thread got its own distinct link. Fired a real toast via `test()`. I did not click it myself (can't without taking the mouse); the link form is the one the banner already uses.

Undo: revert the commits in ai-os and ~/.hammerspoon, then `hs -c 'hs.reload()'`.

## 15:25 Test toast for a real thread

Matt wanted a test toast with a button that opens a real thread. `test("cmsg_…")` now builds the toast for that thread in the Everything project; the toast's hover "Open" pill (or a click anywhere on it) opens the link. The command I gave targets this thread, so a working click lands him back here. Plain `test()` still picks the soonest linkable thread.
