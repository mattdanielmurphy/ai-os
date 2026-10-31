
## Eye breaks go quiet when you cancel
You asked that repeated cancels mean you're busy. Two cancels in a row now silence the eye break, 3-hour nudge and 6-hour overlay for 90 minutes; the quiet survives a Hammerspoon reload. A completed break resets the count. Knobs: busy.cancels, busy.quietMinutes (Tweaks panel). Rejected: counting only eye-break cancels, because the other two would still interrupt. Logic test passes; the on-screen wash wasn't triggered live. Undo: revert the commit in ~/.hammerspoon.

## 21:40 Broken file links

You asked why links in the Autoethnography thread kept failing. That session started in ai-os, and the agent moved to the Autoethnography folder. The app resolves relative links against the start folder, so Rough-Cut.md pointed into ai-os. Evidence: session cwd is ai-os, transcript cwd is Autoethnography; the file exists. Not click-tested. Earlier failures were names with spaces, unencoded. Rule now: absolute paths with %20, never relative. Rejected a hook for now: the rule covers it, and a reply-scanning hook would be more machinery. Undo: revert the rule line.
