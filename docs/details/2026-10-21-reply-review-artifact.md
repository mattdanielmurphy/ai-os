# Reply review artifact (2026-10-21)

## 19:50 Plan before building

What Matt asked (via the coordinator, from the Mac-dependence walkthrough thread): the AskUserQuestion page-by-page review of a long reply "doesn't cut it". "Artifact is definitely the way to go"; make a shared module out of the morning check-in phase 1 page so improvements carry over. Wants per-section read/agree checkboxes, inline comments as editable highlights, real formatting, no stuck "Next" step.

What I read: `services/checkin/template.html` (single-file page: theme tokens, segmented progress strip, step sections, db save + resume via `window.claude.use("db")`) and `build.py` (injects `__DATA__` JSON into the template).

---

### One scrolling page

The "page sits until Next" complaint comes from paging. The review page shows every section at once, formatted markdown, with a checkbox per section. Progress strip shows ticked sections and jumps to them. No Next button anywhere.

---

### Highlight to comment

Select text, tap "Comment", type. The text gets a highlight; tapping it reopens the note to edit or delete. A general comment box per section too. Hand-rolled with the browser Selection API (about 80 lines), because the annotation libraries (Recogito text-annotator) are heavier than the job and pull in React-style setup. Markdown via marked + DOMPurify from cdnjs.

---

### Shared page kit

New `services/pages/kit.css` + `kit.js`: theme tokens, fonts, buttons, progress strip, db save/resume, markdown render. `build.py` inlines them into each page at build time (artifacts are single-page; inlining avoids cross-artifact file copies). Check-in's template switches to the kit with its look and behaviour unchanged; I rebuild it and diff the output visually before it goes live, since the 7:45 job uses it daily.

---

### How Claude gets the result

The page saves to its db (`reviews/<id>`). Matt says "done" (or ✅) in the thread; the agent reads it with ArtifactData and acts. A page can't message a thread itself (tested 2026-10-19).

---

### Existing tool considered

Claude Docs (connected) already does formatted docs with inline comments that reach Claude. Rejected as the main path because Matt chose Artifact, it has no per-section tick, and it can't share code with the check-in page. Worth a one-line mention only.

Untested: everything; nothing built yet. Undo: nothing to undo.

## 20:25 Tap-a-sentence + dictation logic (restated before building)

Matt: he almost always comments on a sentence, sometimes a few words, never a character or a bullet glyph. One tap should start commenting. The page should be ready for dictation (TypeWhisper) the moment a section shows; that talk = general comments. Tapping a sentence highlights it, and what he says next is about that sentence. The mic/dictation failure aside went to another thread (coordinator).

---

### One box, always focused

A single comment box sits under the section, focused as soon as the section loads, so his TypeWhisper hotkey types into it right away. Text with no sentence chosen is a general comment. One box (not one per sentence) so focus never jumps while TypeWhisper is mid-insert, which could drop words into the wrong box.

---

### Tap sets the target

The page splits each paragraph and list item into sentences (Intl.Segmenter). One tap highlights that sentence and shows it as a chip above the box. Whatever lands in the box after that belongs to that sentence. Tapping a different sentence saves the box's text to the old target, clears the box, and moves the target. Tap the same sentence again (or the chip's x) to go back to general.

---

### Narrowing to words

Long-press-drag (native selection) over words narrows the target to just those words. Single characters and bullet markers are never targets: selections snap to whole words.

---

### Page can't start dictation

The page can focus the box but can't press his hotkey. TypeWhisper has a `typewhisper://` URL scheme, but artifact pages can't launch app URL schemes (claude:// did nothing, 2026-10-19), so I won't count on it. On iPhone the keyboard mic works in the same box.

Questions for Matt: Mac or iPhone for reviews; whether a tap on an already-commented sentence should bring its note back into the box (my default: yes).

## 23:45 Page can start the action (router pushback)

Matt pushed back on "the page can't start it" and pointed at his AIOS URL router. He's right: the page can't call the thread directly, but it can open a link, and a link can hit his Mac.

---

### Router idea still works

`tools/url-router/AIOSURLRouter.app` caught clicks to `http://127.0.0.1:8643/*` and ran a local action instead of opening Chrome. Today it's dormant: Chrome is the default browser again and its listener (`services/url_action_listener`) was removed in an old cleanup commit. It also only works on the Mac, and only if the router is the default browser.

---

### Use mac connector instead

`services/mac-connector` already runs on his Mac and is public over Tailscale Funnel (HTTPS, token in the path). It already has `send_task`, which queues into `tmp/voice-task-inbox/queue/` and posts to the project chat. Plan: add a plain HTTP route (e.g. `/act/<token>/review-done?id=<artifact>`) to the same server. The review page's "Done" button is a normal link to it. Mac gets the hit, queues "review <id> done" for the coordinator, which routes it to this thread; I then read the notes from the page's saved data. A tiny "Sent ✓" page is shown in the browser tab that opens.

Why this over the router: works from iPhone and Mac, no default-browser swap, reuses a running service. Notes never go in the URL (privacy rule), only the page id; content stays in the page's saved data.

Rejected: reviving the 127.0.0.1 router (Mac only, needs browser swap); fetch() from the page to the Mac (artifact CSP likely blocks it).

---

### Not tested yet

Untested: whether a claude.ai artifact lets a link open an outside URL in a new tab (expected yes on Mac and iPhone, will confirm first). Delivery into the thread goes through the coordinator, so it can take ~a minute and relies on the voice-task inbox paste path (take-control queue).

Undo: remove the new route from server.ts and restart the launchd agent.

Defaults if Matt doesn't answer: build for both Mac and iPhone; tapping a sentence with a note reopens that note.

## 09:50 Built and published

Matt 👍'd. Built it.

---

### Done route live

`services/mac-connector` has `/act/<act token>/review-done?page=&thread=`. The act token is a hash of the connector token, so pages never carry the MCP token, and the route only queues a fixed-shape note for the coordinator (page id + thread id, validated). Tested: unit tests, and over the public Funnel URL (wrong token 404, bad id 400). Not yet tested: a real click delivering through the coordinator to this thread.

---

### Page built

`services/review/` (template + build.py), look from new shared `services/pages/kit.css`. Tested in the browser pane: sentence split keeps bold/links, tap switches target, re-tap restores the note, general box, word drag snaps to whole words, tick updates progress. Published: https://claude.ai/artifact/JQcNpN5dEb5kgPtCEm9xcF (reviewing this details file as a trial).

---

### Check-in not migrated yet

The check-in page still has its own CSS copy. Moving it onto kit.css touches the 7:45 daily job, so I left it for a separate careful step.

Undo: revert the services/review, services/pages and mac-connector /act commits; restart the connector.

## 10:15 Size, word drag, paragraph and section picks

Matt tried it on his Mac: far too big, drag didn't select whole words, wants to pick a whole paragraph or section, more inner padding, a wider card, a bit more vertical space. Dictation-from-a-tap went to the coordinator (his words quoted), since he believes another thread is on the URL-router route.

---

### Smaller and roomier

Review-only overrides (kit.css and the check-in are untouched): body 16px, h1 ~30px, section h2 20px, headings inside a reply 16-18px, column 46rem, card padding 32px 40px (20px on phones), larger gaps and line-height 1.65. Done bar is now a small button on the right with the status text on the left, not a full-width orange slab.

---

### Whole-word drag

On mouseup the selection's ends are pushed out to word boundaries, and the words stay painted with the CSS Highlight API while the comment box takes focus (a normal selection would vanish when the box is focused). Tested in the browser pane: a drag from mid-word gave "pushed back".

---

### Paragraph and section picks

Clicking inside a paragraph's box but not on a sentence (e.g. to the right of a short last line) aims at the whole paragraph; list items count as paragraphs. Clicking the section heading aims at the whole section. Picked paragraphs/sections get a soft tint. Notes are stored under `p:<section>:<n>` and `sec:<section>` keys next to the sentence keys. Tested via synthetic clicks.

Untested by me: real mouse drags on his Mac (I used synthetic ranges).
