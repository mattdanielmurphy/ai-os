# Scroll-read reactions (2026-10-24)

## 12:40 Interaction options before building

Ask: react to a sentence, paragraph or the whole report while it plays; reactions are love, agree/prefer an option, don't want, confused, dictated comment; send all at once. Don't build the voice mode.

What I read: `~/projects/pages/site/scroll-read/index.html`. Taps on a word jump the narrator there (line 405). Touch/wheel/middle-drag scrolls and the highlight "lets go" past a pull threshold. Space toggles play. The earlier tap-a-sentence idea is in `docs/details/2026-10-21-reply-review-artifact.md` (tap sets the target, one always-focused box, dictation fills it).

### Clash to solve
A plain tap already means "jump here", a drag means "scroll". Reactions need a gesture that is neither.

### Option A: long-press
Hold a sentence ~0.4s: it's picked, a small bar floats above it (love, agree, don't want, confused, mic). Hold again on the same spot widens to paragraph. Tap and scroll unchanged. Whole report: one button at the end. Con: hidden gesture; needs a hint line.

### Option B: React mode switch
A visible React button. On: taps pick instead of jump, scroll still works, a level switch (sentence / paragraph / all) sits in the bar. Off: today's behaviour. Con: one more mode to forget.

### Option C: margin dots
A thin gutter beside each paragraph with a dot; tap = paragraph bar. Sentence via long-press (as A). Always visible, so discoverable. Con: crowds narrow phones.

### Sending
A static page can't message a thread. "Send all" would copy a tidy list (quote + reaction + comment) to the clipboard, and also save it to a shared JSON the agent can read. Untested idea; pick later.

### Agent effort
Reactions are keyed to `data-read` paragraph + sentence index, so any document the page renders is reactable with no per-document work.

Nothing built. Coordinate with thread "Scroll-to-read reel v2" before editing index.html.
