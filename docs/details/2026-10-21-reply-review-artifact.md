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
