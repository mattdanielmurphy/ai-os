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

## 10:25 Buffering spinner

Matt asked for a buffering icon while the voice loads. The play button now turns into a spinning ring whenever reading is on but the voice hasn't started yet (first load, a new block, after a skip, or a voice or speed change), and goes back to ❚❚ the moment it speaks. Tested headless with a deliberately slow voice server: spinner for about 1.5 seconds, then speaking. Undo: revert the "play button spins" commit in ~/projects/pages and run `pages deploy`.

## 10:45 Smart skip, built

Matt approved smart skip and asked that the stages be visible and reversible.

---

### How it works now

- **Ratings come for free.** Every `pages readthrough` now starts a background job (about 45 seconds including the push) that asks Claude's small model, through the claude command on Matt's plan, to rate each sentence crucial, useful or detail and to pick one key phrase per paragraph where it matters. It writes `ratings.json` next to the page. Agents do nothing extra. If the text changes, old ratings are ignored until the new ones land.
- **The Pace chip (top left) shows the stage**: four dots and its name. Tapping it opens the four stages with a one-line explanation each, and you can pick any of them directly. That's how it works on a phone.
- **→ skims more, ← skims less.** Everything → Skip details → Hurry → Key points. ← steps back one stage without moving; only at Everything does ← go back a sentence. A small note names each stage as you enter it, with "← to undo".
- **Skip details** and **Hurry** apply to the section you're in and wear off at the next section. If the skip itself lands in the next section, the stage moves with it. **Hurry** and **Key points** read 25% faster; your speed setting isn't changed.
- **Skipped sentences stay on the page, faded.** Tapping one reads it, then skimming carries on after it.
- **Key phrases** are underlined.

Readthroughs without ratings (or the scroll-read demo page) keep the plain → = next sentence.

---

### Also fixed

The section list on wide screens let long headings run into the text; they now cut off with "…" and the list scrolls.

---

### Untested

Not tried on a phone or by ear. The ratings come from a small model, so some judgments will be off; tell me which ones and I'll tune the prompt in `pages/rate.ts`. All existing Readthroughs are being rated in the background now.

Undo: revert the "smart skip" commit in ~/projects/pages and run `pages deploy`.

## 11:15 Highlight stall on "0.05 s", and held small scrolls

---

### Stall after words like "0.05 s"

Cause: Speechify gives "0.05 s" as one timing mark, but the page has two words ("0.05" and "s"). The matcher then let "s" match the start of "so" four words later, so every word in between got the same time and lit up all at once. Fix: short words (under 3 letters) must match exactly; a page word that is the leftover end of the previous mark shares that mark's time; and any word without a mark gets a time spread evenly between its neighbours instead of copying the previous one. Tested on the exact sentence: old code put "s before the word, so" all at one time, new code gives each its own.

---

### Held small scroll

A scroll too small to snap now still moves the reading if you stay there: after the page has been still for 1.5 seconds, the reading jumps to the line 40% down the screen (where auto-follow keeps it, so the page doesn't shift afterwards). A dashed outline on the target word fills in and a small note counts down ("reading moves here in 0.8s"), so you can scroll back before it happens. Only while reading is playing; paused scrolling stays free. Tested headless with a 115 px wheel scroll: jumped after about 1.5 seconds.

Changed with it: after a small scroll, auto-follow now waits until the reading is back within a line of its spot, rather than anywhere in the middle band.

---

### Ratings for older Readthroughs

9 of 16 rated so far; the rest are running in the background.

## 11:25 Double back and smarter preloading

---

### Pressing back twice

A second ← within 0.7 seconds now goes one sentence further back from where the first one landed (same for ↑ with paragraphs). A single ← still goes to the start of the current sentence first if you're more than a couple of words in. Tested: from the middle of sentence 8, three quick presses landed on 8, 7, 6.

---

### Preloading

Before, only the next paragraph's voice was fetched ahead. Now it also fetches the paragraphs holding the next sentence, the one after next, and wherever → would land in smart skip, and it downloads their audio files too (before, only the timing was fetched, so the audio still had to load when you jumped).

## 11:35 Pauses between short sentences

Cause: the voice comes in one recording per paragraph or heading, and moving to the next one meant swapping the audio file in the one player and waiting for it to load, so short paragraphs had a pause after each. Fix: a second, hidden player holds the next paragraph already loaded and takes over the moment the first one ends. The voice is also fetched ahead for the next 160 words, however many short sentences or paragraphs that spans. Measured: gaps between paragraphs are now 0 to 2 milliseconds (headless, on this Readthrough and the demo page).

## 11:45 Speed keys back to small steps

Matt: 25% per key press was far too much; he meant the slider should snap to 25% marks. Now `,` and `.` change speed by 5% per press, and the speed slider accepts any value but snaps to 100%, 125% and the other 25% marks when you come within 5% of one. Tested: keys step 135 → 140 → 145; slider 97 and 103 both snap to 100, 112 stays 112.
