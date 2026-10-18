# Handoff: Expired thread cache detection (2026-10-18, cold)

## Chain
- Old thread: a7d5386c-630e-449a-a708-4c6112b7127f (this one). Reopen with `claude --resume a7d5386c-630e-449a-a708-4c6112b7127f` (expensive: almost certainly cold after 1h).

## Chain summary
- Built a cache-expiry warning in the context-alert mod bar, showing countdown ("Cache expires in 10 min") then red alert after expiry.
- Added a "Fresh thread" button that spawns a new Code thread without reloading the old one—uses a standalone Python script (`cold_handoff.py`) with Haiku to write the handoff from disk.
- Implemented phone fallback: messages into cold threads are held back with a choice to `/fresh` or re-send.
- All code committed and pushed; 4 tests pass, mod validates, type-checks clean.

## This thread
- Mod code written, validated, and tested at `/Users/matt/.claude/dev-mods/a7d5386c-630e-449a-a708-4c6112b7127f/context-alert/`.
- `scripts/cold_handoff.py` reads old thread files and calls Haiku to write handoff in a separate session (proof: 44-line handoff for a 147k-token thread in ~45s, old thread never reloaded).
- Countdown calculation uses thread's last-reply timestamp + cached lifetime from the thread file (exact, not guessed).
- Phone hold-back catches messages before model, offers `/fresh` or retry within 10 min.

## Working on now
Matt just raised a real concern: **does `/fresh` carry forward user context like `/_handoff` does?** Right now `/fresh` opens a new thread and gives a paste prompt for the handoff only—doesn't preserve user messages, attachments, or input state from the current prompt. The distinction: `/_handoff` types inline in the same thread; `/fresh` is a clean new thread. Need to check whether this gap matters for Matt's workflow or if it's acceptable as-is.

## Keep in mind
- **Not tested in the real app yet.** Type `/reload-plugins` or start a new thread to load the mod. Opening the new thread doesn't pre-fill the prompt (you paste once with ⌘V).
- **Phone message tagging is unknown.** Tests use the doc's tag, but hold-back may not catch phone messages if they're tagged differently. First cold-thread test on phone will confirm.
- **Held message may not stay in the box.** If it vanishes, user will need to retype.
- **The countdown only shows for threads >30k tokens** (smaller reloads are cheap).

## Next steps
1. **Test on Mac first:** reload the mod, open an old cold thread, verify countdown displays correctly and "Fresh thread" button works (should open new thread with handoff as a paste prompt).
2. **Clarify the `/fresh` vs `/_handoff` gap:** does Matt want `/fresh` to carry forward the current message/attachments, or is it fine as a bare handoff-only hand-off? If carry-forward is needed, the script and button logic will need to be extended.

## Read first
- `/Users/matt/.claude/dev-mods/a7d5386c-630e-449a-a708-4c6112b7127f/context-alert/hooks/register.tsx` — mod code; countdown logic on lines ~60–90, phone fallback on ~110–130.
- `/Users/matt/projects/ai-os/scripts/cold_handoff.py` — reads thread file, calls Haiku, writes handoff.
- Test file: `/Users/matt/.claude/dev-mods/a7d5386c-630e-449a-a708-4c6112b7127f/context-alert/hooks/register.test.ts` — countdown and phone-hold tests.

Paste into a new thread: "Read /Users/matt/projects/ai-os/docs/handoffs/2026-10-18_expired-thread-cache-detection-cold.md and continue."
