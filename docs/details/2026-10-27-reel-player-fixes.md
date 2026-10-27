# Reel player fixes (2026-10-27)

## 08:55 Highlighter, voices, arrow keys, overhead, name

Matt asked: fix the highlighter's false start and snap-back, make it calmer, pick from about 10 Speechify voices with previews, arrow keys by sentence and paragraph, check what reels cost an agent, and a better name ("Read along").

---

### False start fix

The cause: with the voice on, the highlight kept walking at reading speed while the voice was still loading (about 1.5 to 3.5 seconds for a new block), then jumped back to the voice's word once audio started. A second, smaller snap: the player seeked 0.05 s before the word, so for a moment it showed the previous word.

The fix: while the voice is on, the highlight waits for the voice (loading, seeking, between blocks). It walks on its own only when the voice is off or failed. The voice can no longer show a word before the one it started on. Tested headless: the word index never went backwards, locally and on a live reel.

---

### Calmer highlight options

Four looks, switchable live in Tune, Highlight:

- **Sentence** (new default): a faint wash over the whole sentence, which moves once per sentence. The current word is in full ink.
- **Ink**: no shape at all. Upcoming words are pale and darken as they are read.
- **Underline**: a thin line glides under the word.
- **Glide**: the original moving highlight.

The pull and snap feedback during a big scroll still appears in every look. Rejected: building separate mockups first; the options are cheap to compare live in the real player, which is what the "options before building" rule is for.

---

### Voice picker

Tune, Voice lists 10 of Speechify's own staff picks for the simba-3.2 model, 5 women and 5 men: Beatrice (default), Harper, Imogen, Geffen, Carly, Wyatt, Edmund, Dominic, George, Oliver. The ▶ button plays Speechify's own sample clip (free, instant). Picking a voice re-reads from the current word in that voice; each block is made once per voice, then cached for everyone.

Only these 10 voices can be requested, so the voice endpoint stays closed. The list lives in `pages/tts.ts` (`VOICES`). The full English catalog (125 voices) is at `/api/tts?voices=all` if Matt wants more.

---

### Arrow keys

Right and left move by sentence, down and up by paragraph. Back goes to the start of the current sentence first, and to the previous one if you just started it (like a music player's back button). A key hint sits at the bottom of Tune.

---

### Agent overhead

Overhead is close to zero: one `pages reel <details.md>` command per reply, which took 1.9 seconds here. It renders the Markdown, commits one file to the mattmurphy.ca repo and pushes; Vercel deploys it. No voice is generated until someone presses play. Recent threads are already publishing reels (chrome-tabs, linear-board-questions, shared-ui-library and others).

---

### Name options

Read along (Matt's idea, recommended), Readthrough, Trail. Not renamed yet; waiting for Matt's pick.

---

### Untested and how to undo

- Not tested on a real phone or by ear; the headless test checked timing, keys and layout only.
- Undo: `git revert` the scroll-read commit in ~/projects/pages, then `pages deploy`.

## 09:20 Round 2: Readthrough name, scroll hold, speed keys, extras

Matt picked "Readthrough" (also floated "Table Read"), asked that his own scroll pauses auto-follow at once, that dimmed words light up while he scrolls and dim again on play, `,` and `.` for speed with a reminder when he skips a lot, and anything interactive an agent gets for free.

---

### Scroll hold

Any scroll of yours turns auto-follow off at once and keeps it off afterwards (before, it pulled the page back to the word as soon as you stopped). It comes back when the word scrolls back into view, or when you press "Back to reading" (bottom centre, arrow points to where the reading is), tap a word, use a key or press play. A big scroll still snaps the reading to where you are, as before.

---

### Lit words

While you're scrolling, scrolled away, or paused, every word is full ink (no dimming of read words, no pale upcoming words in Ink). Reading again dims them as before.

---

### Speed keys

`.` reads 20 wpm faster, `,` 20 slower (YouTube's keys without Shift; `>` and `<` work too). A small note shows the new speed and fades. After 3 sentence skips within 30 seconds, if speed hasn't changed in 10 minutes, a one-time note says "In a hurry? Press . to read faster". Rejected: making → temporarily speed up instead of skip; Matt said the skip feels right, and two behaviours on one key would be confusing.

Bug found and fixed while testing: after clicking a button (like play), the arrow and speed keys were ignored because the focused button swallowed them.

---

### Free extras

All automatic from plain Markdown, nothing for agents to write:

- **Section rail**: headings as a list on the left (wide screens) or a "§ Sections" button (narrow), current section marked, tap to jump, plus "About N min left".
- **Copy** on every code block.
- **Task lists** (`- [ ]`) become checkboxes that remember their state per page.

Ideas not built (each would need agents to write something extra): quick-check questions, decision buttons that reply to the thread.

---

### Rename

`pages readthrough` is the command now; `pages reel` still works so nothing breaks. The rule in ai-os and the global instructions now say Readthrough, and the Details line link is labelled `[Readthrough]`.

---

### Untested

Not tried on a real phone or by ear. Touch scrolling uses the same hold logic but was only tested with a mouse wheel.

## 09:52 Why the voice sounds like a log, and the fix I propose

Matt: the voice reads things like "09:20 Round 2: … Matt picked Readthrough, asked that his own scroll…", and no person reading him a report would talk like that.

---

### Cause

Details files are written as an agent's log: third person ("Matt asked"), timestamps in headings, inline code, paths. The voice reads the page word for word, so it reads the log.

---

### Proposed fix

1. **Write to Matt, not about him.** Change the details-file rule: second person ("You asked…", "I changed…"), plain spoken sentences, headings without the time. Agents write this text anyway, so no extra work, and the highlight stays exact because voice and page are the same words.
2. **Voice-only cleanup in the player's voice server.** When making the audio, skip the timestamps in headings, skip code blocks and file paths (the highlight passes over them), and say symbols like `,` and `.` by name. Deterministic, no AI call.

Rejected: having an AI rewrite each block for speech at publish time. It would sound most natural, but the spoken words would no longer match the page, so the word highlight would drift, and every publish would cost an AI call.

## 10:15 Round 3: slow-speed sound, percent speeds, emphasis, smart skip plan

Matt: the sound has artifacts at slow speeds; show speed as a percentage that snaps to 100% and other 25% steps; → should act like a busy CEO saying "uh huh" (cut to the chase, and keep condensing if he keeps pressing); and make it more engaging with highlighting of important things and small formatting touches.

---

### Slow speeds

The warble came from the browser stretching the audio below about 0.8x. Under 85% the voice now uses a second recording that Speechify makes at 70% pace, so the browser only stretches it a little. That recording is made once per block the first time someone listens slowly. The slowest setting is now 60%.

---

### Speed in percent

Speed is now a percentage of the voice's natural pace (100% is about 230 words a minute). Your old 310 wpm became 135%. `.` and `,` jump to the next 25% step (135 → 150 → 175, or down to 125, 100, 75). Every slider in Tune is magnetic near round values: speed snaps to 25% steps within 4%, and the others to their own round numbers.

---

### Emphasis and formatting

Bold text (`**…**`) now has a marker stroke behind it, and italics a quiet tint. A section whose heading mentions Untested, Risks, Failures, Warning, Caveats or Undo gets a coloured bar down its side, so it can't be skimmed past. All of this comes from plain Markdown, so agents do nothing extra. A next step would be the AI pass below also marking key phrases.

---

### Smart skip: plan, waiting for Matt's 👍

1. **Ratings, made automatically.** When an agent publishes, a background step asks Claude (a small model, on Matt's own plan, about 15 seconds, nothing for the agent to do) to rate every sentence: crucial (decisions, what Matt must do, results, failures), useful, or detail. The same pass marks a few key phrases to highlight.
2. **→ once ("uh huh").** It skips to the next sentence in this section that isn't just detail; if there isn't one, to the next section.
3. **→ again within about 20 seconds ("hurry up").** For the rest of the section it reads only the crucial sentences, 25% faster.
4. **→ a third time ("key points only").** The whole rest of the document is read as crucial sentences only. A small "Read everything" button, or ←, goes back to normal at your usual speed.

Without ratings (old Readthroughs, or if the background step fails), → stays a plain next-sentence skip. Open question: should "hurry up" wear off by itself at the next section? I'd say yes, and "key points only" stays until you turn it off.

---

### Untested

Not heard by ear: the slow recording's pitch and the smoothness of the switch at 85% are checked only by measurement (the 70% recording is 1.42 times as long, as expected).
