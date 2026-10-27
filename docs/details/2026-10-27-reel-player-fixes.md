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
