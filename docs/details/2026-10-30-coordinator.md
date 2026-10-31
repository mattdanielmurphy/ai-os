
## Eye breaks go quiet when you cancel
You asked that repeated cancels mean you're busy. Two cancels in a row now silence the eye break, 3-hour nudge and 6-hour overlay for 90 minutes; the quiet survives a Hammerspoon reload. A completed break resets the count. Knobs: busy.cancels, busy.quietMinutes (Tweaks panel). Rejected: counting only eye-break cancels, because the other two would still interrupt. Logic test passes; the on-screen wash wasn't triggered live. Undo: revert the commit in ~/.hammerspoon.

## 21:40 Broken file links

You asked why links in the Autoethnography thread kept failing. That session started in ai-os, and the agent moved to the Autoethnography folder. The app resolves relative links against the start folder, so Rough-Cut.md pointed into ai-os. Evidence: session cwd is ai-os, transcript cwd is Autoethnography; the file exists. Not click-tested. Earlier failures were names with spaces, unencoded. Rule now: absolute paths with %20, never relative. Rejected a hook for now: the rule covers it, and a reply-scanning hook would be more machinery. Undo: revert the rule line.

## Cold threads now restart by themselves

You asked that the cold-thread hook stop telling you to do things. Now a big cold Code thread gets a cheap Sonnet brief, clears itself in place, and sends the brief with your message. It stays the same sidebar thread. I did not route it through the coordinator, because the app refuses to start sessions from another session's message, and this also matches your "right here" wish. If anything fails, your message simply sends in the old thread at full price. The automated tests pass; the real clear has not been tried in the app yet. Saved a global rule: hooks never give you a job.

## Cold-thread hold removed from Code threads

You pointed out Claude now auto-compacts on its own, and the hook was reading a stale 370k when the thread was really 91k. So the hold is gone for Code threads, along with the restart-in-place I had just added. Project threads and the coordinator's own catch-up are unchanged.
