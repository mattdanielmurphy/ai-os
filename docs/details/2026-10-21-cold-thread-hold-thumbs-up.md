# Cold-thread hold and 👍 handoff (2026-10-21)

## 18:15 Why the 👍 did nothing, and the fix

**Asked:** Matt 👍'd the "Held, nothing sent yet" note in "Lid-closed setup for Tyler" and no fresh thread started. Also: does a further message to a held thread stay held, and what happens if he edits the original? Coordinator added: a 👍 in "About-me index on Mac" also did nothing; test Matt's theory that agents only see reactions/messages when something else wakes them.

**Root cause (from the Lid thread's transcript, 50fe0561…jsonl):** the context-alert mod's `prompt.submit` hook only looked at turns from a person (`isMeta` false, origin composer/bridge/sdk). The app delivers reaction wakes and edit wakes as *system* turns (`isMeta: true`, `promptSource: system`). Counted across all local transcripts: 263 mention wakes (person), 10 reaction wakes and 1 edit wake (all system). So the 👍 skipped the hold check and went straight to the model: the old thread re-read ~285k tokens and started building the lid-sleep menu itself (lid_sleep.lua, menu_bar.lua, lidstay commit 6bcefdd). The coordinator was told, since its new lid thread duplicates that work.

**About-me thread:** different cause. Its session went offline on Oct 20 ("messages wait for it") and never came back, so the reaction had no live session to wake. That matches Matt's theory for parked sessions: a reaction or message waits until the session is back. Live sessions do get reactions immediately (the Lid thread got its 👍 two seconds later). Nothing in the mod can wake a parked session; that's the platform.

**Answers before the fix:**
- Further message while held: treated as the answer. Unless it was ⏩/"here"/"go", it started the fresh thread with only the *first* message; the second message's text was lost.
- Edit of the held message: arrives as a system turn, so it bypassed the hold and ran the cold thread at full price on the edited text.

**Fix (context-alert 0.3.4):**
- While a message is held, reaction wakes from a person count as his answer: 👍 (or any other emoji) = fresh thread, ⏩ = continue here, ❌ = drop the held message, ✋/👀 = keep holding.
- An edit of the held message replaces the held text, re-starts the Haiku handoff with it, and keeps holding.
- A follow-up message with real content goes to the fresh thread along with the held one ("He added…"). Bare answers ("ok", "fresh", "sounds good") add nothing.
- Other system turns (relays, edits of other messages, agent reactions) pass as before.
- Hold note now lists ❌ and says editing updates what gets sent.

**Rejected:** treating every system turn as an answer while held (a coordinator relay would wrongly trigger a fresh thread). Matching reactions to the hold note's own message id (the tool result shape for the note's id isn't documented; any person reaction in the thread is good enough).

**Tested:** 15/15 mod tests pass, 6 new ones built from the real reaction/edit envelope shapes. Not tested live yet.

**Live:** installed (0.3.4, managed scope); the app loads it after its next restart (the nightly 04:30 restart covers it).

**Undo:** `git revert` the commit, bump version, `claude plugin update context-alert@ai-os-mods`.

## 18:55 "Canoodling" after the hold: is it really held?

**Asked:** in "Always-on piano and MIDI capture" the hold note appeared but the thread showed "Canoodling" (working), so Matt suspected the message went through anyway.

**Checked:** that thread's transcript (gallant-borg 39f1c442…jsonl). At 00:50:20 the message was queued and dropped by the hook ("Held (project thread): cache expired 1h ago, ~188k tokens"). There is no API request after it: the model never ran and nothing was re-read. The session list now shows that thread as waiting on Matt, not working.

**So:** the hold works. "Canoodling" is the app's working indicator for the half-second the hook runs (it posts the hold note), shown before the dropped turn's end reaches the project page. It's cosmetic; the mod can't change that indicator.

**No code change.**
