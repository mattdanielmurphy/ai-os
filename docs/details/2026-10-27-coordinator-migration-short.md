# Leaving Projects for Claude Code: the short version (2026-10-27)

## What you need to know

### Threads can keep going with no handoffs

Claude Code can compact a big thread just before its cache expires, so the thread carries on in the same place. It only does this in the terminal, but your desktop mod can trigger the same compaction.

### Don't hand off every expired thread

Your own test on Oct 23 found that resuming an expired thread remembered more than a handoff did (7.5 vs 5.8 out of 10), at about the same cost below 250k tokens. Handoffs only pay off for very big threads.

### Leaving Projects saves tokens on every thread

A new project thread starts at 134k tokens. A new Code-tab thread starts at 60k.

### The Code tab already has most of a coordinator

One session can start threads on a chosen model, message threads that are still warm, and gets woken when each one finishes.

### The plan

1. Your mod compacts big threads just before they expire. This helps your project threads today too.
2. One pinned Coordinator session in the Code tab, running your routing rules.
3. Voice tasks and the Shelf feed into it.
4. Run it next to Everything for a few days, then switch.

### What you'd lose

Threads that run with the Mac off, and the phone's card view. On your phone you'd see a list of sessions instead.

### Not tested yet

Whether the mod's timer still fires while the desktop app sits idle.

### What you need to do

Reply 👍 to build step 1.
