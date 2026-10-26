# Scroll reels (with Ask as you go)

A scroll-to-read explainer: the page is the text, a highlighter follows the narration word by word, and an
**Ask** button answers questions about the sentence you're on. Built from the pages "scroll-read" mockup
(2026-10-24) and made reusable on 2026-10-25 for the PHIL 120 catch-up reels.

**For Matt now, built to go public later** (self-contained kit, no Matt paths in the page).

## Make one

1. `reels/<id>/reel.json`: `id`, `title` (a name, e.g. "Logic 1 · All and Some"), optional `next` + `nextUrl`,
   and `ask` (below).
2. `reels/<id>/body.html`: the inside of `<main>`. Narrated blocks carry `data-read` (h1, h2, p, blockquote,
   `<li><span data-read>`). Keep narrated text speakable: no symbols in it. Shown-only extras:
   - `<div class="f">∀x P(x)<small>caption</small></div>` formula card (`.f.pair` with `<div>` rows and `.tag` labels);
   - `<div class="key"><b>Symbolization key</b>…</div>`, `<table class="sym">`;
   - `<div class="try" data-id="unique"><p class="q">…</p><button class="opt" data-ok data-why="…">…</button>…</div>`:
     a check. The reading pauses after the block before it until it's tried once (remembered per browser).
   - Quiz mode (2026-10-26): add `data-back` to a check that revisits an earlier section ("Throwback"). Put empty
     `<div class="try redo" data-id="unique"></div>` slots after later blocks: a check missed on its first pick
     comes back there, options reshuffled, once it's at least a section old (an empty queue skips the slot).
     The first pick on every check is scored (pill, top left); the end panel shows the tally and lets the reader
     retry whatever is still missed. Each check must follow a `data-read` block (one check per block).
3. `bun build.ts reels/<id>` (records each block once with Speechify via `~/projects/pages/tts.ts`, cached in
   `cache/`, backs off on 429). Output: `out/<id>/index.html` (Artifact fragment), `audio/`, `files.json`, `test.html`.
4. Test: `NODE_PATH=<dir holding playwright-core> node test.cjs <id>` (and `quiz-test.cjs <id>` for quiz mode) (headless, muted, fake Claude). Never open
   reels in the Claude browser pane.
5. Publish as a claude.ai **Artifact** (it needs the `sample` capability, so not Vercel): `file_path`
   `out/<id>/index.html`, `root` `out/<id>`, `files` = `files.json`, `capabilities: {"sample": {}}`. Republishing
   only the page keeps the audio.

## Ask as you go

`ask.js` uses the Artifact runtime's `sample` capability: the viewer's own Claude answers, the first question asks
them to allow it, and anywhere else the button stays hidden. It sends the whole page text, the sentence they paused
at, and the chat so far. Openers: the Ask button (or `A`), "Ask" in the long-press reaction bar, "Ask about this"
under a check. Past questions are kept per reel in the browser ("Earlier questions").

`reel.json` `ask`:
- `mode: "school"` adds the academic-integrity rules (explain, new examples, hints; never solve or check textbook
  exercises, assignments, quizzes or exams; coach rather than answer "symbolize this"). Use it for every course reel.
- `audience`: who's reading and where they are. `rules`: anything extra. `chips`: replace the quick-question buttons.

## Files

- `kit/player.js|css`: the reader (scroll gestures, highlight, narration, checks). `kit/reactions.js|css`: long-press
  reactions. `kit/ask.js|css`: Ask.
- `reels/speed-1..`: PHIL 120 speed review with heavy quizzing for Midterm 2. Speed 1 (ch. 1–8)
  https://claude.ai/artifact/WVneBno1UzEMfzY5a1rnpA · Speed 2 (ch. 9–15) https://claude.ai/artifact/J17qDAd1PejdMqhhjnZRaN ·
  Speed 3 (ch. 16–22) https://claude.ai/artifact/8KFVUwnGYh5JQkyAGAVyY2
- `reels/logic-1..4`: PHIL 120 Unit 5 catch-up (forall x ch. 23–29). Live: Logic 1 https://claude.ai/artifact/BrBy9VCdTbZapqZ4Fw1Zrs ·
  2 https://claude.ai/artifact/6DrNZ9BD27r9EPHbUgaxww · 3 https://claude.ai/artifact/MDkbTk9z3DjtXeWVVisAqt ·
  4 https://claude.ai/artifact/2webCnZjMNJtHwMBDgtGxW
