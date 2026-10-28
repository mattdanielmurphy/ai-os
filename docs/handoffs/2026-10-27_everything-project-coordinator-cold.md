# Handoff: Why the Everything coordinator can't start the Glass TV Stremio add-on thread in ~/projects (2026-10-27, cold)

## Chain
- Old thread: cfb6e98f-ceb6-4b51-8625-5cbb28c623d6 ('Everything' project coordinator can't start a new thread in ~/projects; find ou). Reopen with `claude --resume cfb6e98f-ceb6-4b51-8625-5cbb28c623d6` (expensive: cold cache).
- Earlier handoff files: none mentioned in the conversation. The `docs/handoffs/` files showing as untracked in git status (e.g. `2026-10-22_relay-from-coordinator-session-cold*.md`) are unrelated to this thread.

## Chain summary
- Matt reported that the "Everything" project coordinator could not start a new thread in `~/projects`; this thread was started to find out why.
- Investigation of the coordinator and Mac-side logs found that **`~/projects` itself is fine**. The Mac accepted new threads there at 5:46 and 6:01 (the 6:01 one is the investigating thread).
- Only one task fails: the **Glass TV Stremio add-on** thread. The coordinator tried it 7 times between 5:55 and 6:00, and each try failed.
- Each failure looked the same: the Claude servers closed the new session about 150 ms before the Mac could open it.
- The coordinator's own guess, that Matt had switched to the Testing account, was wrong. The logs show the Mac stayed on Matt's own account the whole time.
- Unconfirmed best guess: a server-side check on the task text. The early briefs named torrent and debrid add-ons (Torrentio, Real-Debrid), and the later ones also attached Matt's original message. The logs do not show the server's reason.

## This thread
- Done: read the coordinator and Mac logs, ruled out the folder, the account and the Mac side, and narrowed the failure to the one task.
- Done: wrote a details file at `~/projects/ai-os/docs/details/2026-10-27-coordinator-thread-creation.md` (not yet confirmed committed or pushed).
- Done: told Matt the findings and the workaround in the reply.
- Did not work: nothing was fixed. The exact server-side rejection reason could not be found in any log.
- Not done: no test confirms the "task wording" theory. Nobody has tried starting the thread with reworded text.

## Working on now
The diagnosis is finished and reported. The open question is whether the failure really comes from the wording (torrent/debrid terms) or from something else about that one task. The thread stopped after giving Matt the workaround: start the Glass TV add-on work himself from the Code tab in `~/projects/glass-tv`, without the old message attached.

## Keep in mind
- Matt's rules for replies: aim for about 50 words and up to 100 if clarity needs it, answer first, bold the point, one idea per line, blank lines between items. Every reply ends with a `Details:` line, and the details file gets a Readthrough link via `pages readthrough`.
- Matt's rule against inventing causes: the coordinator must not analyze or invent fixes itself. Root causes and new rules go to a dedicated thread.
- Matt wants any thread you mention to be linked (`[title](#cmsg_…)` or `[title](#local_…)`).
- Matt wants "try this" requests to come with a copy-pasteable command or clickable link.
- Matt is on a live call with Tyler (transcript at `/Users/matt/calls/2026-10-27-tyler.md`). Matt is telling Tyler to use the one "Everything" coordinator project for all work. A fix that makes that coordinator unreliable matters more because of this.
- The "wording" theory is unconfirmed. Do not present it as fact.
- Git status was clean of this thread's files at the start. The details file may be uncommitted, so check it and commit and push it with `python3 ~/projects/ai-os/scripts/auto_commit.py -m "<message>" --paths <file>`.
- The old thread's guess about the Testing account is already disproven, so don't revisit it.

## Next steps
1. Test the wording theory cheaply: have the coordinator (or a direct Mac call) start a new thread in `~/projects/glass-tv` with a short neutral brief such as "Glass TV: add a Stremio add-on source", with no torrent or debrid terms and no attached original message. If it starts, the cause is content-based, and the coordinator should be told to paraphrase around those terms. If it fails again, the cause is something else, so compare the failed session creation against the successful 6:01 one in the coordinator and Mac logs. After that, check that the details file is committed and pushed.

## Read first
- `~/projects/ai-os/docs/details/2026-10-27-coordinator-thread-creation.md`: this thread's evidence (timestamps, the 7 failed attempts, the 150 ms observation).
- `~/projects/ai-os/.rules/core_safety.md`: the coordinator routing rules, including the "coordinator does no analysis" and "reuse only warm threads" rules.
- `/Users/matt/calls/2026-10-27-tyler.md`: context on why Matt cares that the coordinator works for Tyler too.

Paste into a new thread: "Read /Users/matt/projects/ai-os/docs/handoffs/2026-10-27_everything-project-coordinator-cold.md and continue."
