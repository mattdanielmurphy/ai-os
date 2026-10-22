# Smart waiting-on-you nudges (2026-10-21)

## 22:50 Is the cache really 1 hour?
- Asked: is the prompt cache for threads 1 h for sure? Should reminders come at 15 min and then every 10?
- The docs (platform.claude.com, prompt caching) say the default is 5 min and that 1 h is an opt-in `cache_control.ttl: "1h"`. The lifetime counts from the start of the request that reads or writes the cache.
- Checked on the Mac: the transcripts from the last 3 days had 6,732 cache writes. Every one was `ephemeral_1h_input_tokens` and none was 5m. Claude Code drops to 5-min caching when the account is in usage overage. `cold_handoff.py status` reads the TTL from each write, so that case is handled.
- Proposed one nudge 10 min before expiry, sent only when the thread asked Matt something, holds 50k+ tokens and Matt isn't busy. Decided against the 15-min plus every-10-min schedule as spam, now that 1 h is confirmed.

## 23:58 Built it (Matt 👍, "asked you something" = waiting)
- `scripts/warm_threads.py` scans the transcripts in `~/.claude/projects` touched in the last ~hour. It takes the last reply time, TTL and size from `cold_handoff.status`. A thread counts as "asked" when the last message Matt saw ends with a "?" or a 👍 offer in its last 2 lines, ignoring the trailing `Details:` line. That message is a hearthbot `reply`, an `ask_decision`/`AskUserQuestion`, or the final text of a Code-tab turn. Any non-tool-result user message after it (Matt, or a wake carrying his reaction) means he answered.
- `~/.hammerspoon/modules/claude_warm.lua` scans every 60 s with an async `hs.task`. A due thread (asked, 50k+ tokens, 1-10 min left, not yet nudged this cycle) waits while Matt is busy and retries every 15 s.
  - Away means the screen is locked or there has been no input for 2 min. Busy means a key press in the last 20 s, the mic in use, or lecture mode on.
  - Under 1 min left means the nudge is dropped. Several due threads share one toast. The toast is claude_notify's amber "needs" toast.
- Typing is read by `bin/key-idle` (Swift, `CGEventSource.secondsSinceLastEventType(.keyDown)`). That needs no new event tap, because extra key taps caused stalls before.
- Rejected:
  - A Stop hook to mark "asked". Reading the transcript is simpler and also covers threads that started before this change.
  - A keyDown event tap. It would run on the main thread and add a tap.
  - A "keep warm" auto-ping. Hammerspoon can't post into a project thread.
- Untested: a real toast firing at T-10 on a live thread. The logic is unit-tested and the scan ran against live data.
- Undo: untick "Keep-Warm Nudges for Waiting Claude Threads" in the Hammerspoon menu, or remove `safeRegister("modules.claude_warm")` from init.lua.
