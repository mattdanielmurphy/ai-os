# Voice-call auto-save

## 20:40 Does hanging up early lose the call?

Matt asked (via the coordinator): if he leaves a voice call before the end-of-call save, does he lose everything?

---

### Nothing was ever lost

The call itself lives on claude.ai as a normal chat. `scripts/pull_voice_chats.py` (launchd, 3:30 nightly)
copies every voice chat into `Voice calls/Transcripts/` and sends calls without `save_call` to the coordinator
for review (`_review-voice-calls`). Proof: 5 of the 6 transcripts there have no save_call. What was missing
was speed: the summary, facts and to-dos waited until the next morning's review.

---

### Mid-call notes now

New connector tool `note_call` (services/mac-connector/server.ts). Voice Claude calls it whenever Matt says a
to-do or a fact, and every few minutes with what he said. Each call rewrites a live note
`Voice calls/<date> <time> Voice call (live).md` immediately. `save_call` merges the noted facts/to-dos
(deduped) into the final note and moves the live note to the Trash. The connector's instructions tell voice
Claude about it, so no settings change is required, but the suggested preferences line now mentions it too.

Rejected: auto-saving from the claude.ai transcript every few minutes (polling Chrome every few minutes
risks visible tab/permission prompts during the day; the nightly run is at 3:30 for a reason).

---

### Quiet call flushes after 20 min

A 2-minute timer in the connector: if the live draft has had no note for 20 min and no save_call came,
it sends the noted facts and to-dos to the coordinator ("File voice call: unsaved call HH:MM"), marks the
live note "Ended without save_call", and runs the transcript pull early. The pull now skips chats touched in
the last 15 min so it never flags a call that is still going.

---

### Chrome is signed out of claude.ai

Testing the pull showed Chrome's claude.ai tab on the sign-in page (`/login?from=logout&reauth=1`), so the
transcript safety net currently copies nothing. Matt needs to sign in to claude.ai in Chrome once.

---

### Untested parts

- No real voice call was made: voice Claude actually calling `note_call` is untested (LLM compliance).
- Unit tests (bun, 9 pass) cover the draft, dedupe, flush-once and note rendering. The connector restarted
  and answers /health.
- Undo: revert the commit and `launchctl kickstart -k gui/$UID/com.matt.agent.mac-connector`.
