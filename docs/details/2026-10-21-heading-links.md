# Heading links in replies (2026-10-21)

## 18:35 Test status and proposed rule

Asked (via coordinator, Matt's idea from the Tyler utils thread): test whether `file.md#heading` links in replies open the details file at that heading; if yes, make each non-trivial reply line link to its own heading.

What I did: started writing my own test file, then the coordinator said the Tyler utils thread had already posted a 4-link demo and asked Matt to tap them. I dropped my duplicate test so Matt isn't asked twice. His answer there decides it.

Known so far: the platform docs say a `/mnt/project-files/<file>.md#<slug>` link opens the preview at that heading. Mac paths (`/Users/matt/...#slug`) in Code-tab replies are untested.

Proposed rule (waiting on Matt's 👍 and his tap result): each non-trivial reply line links to its matching `##` heading in the details file; the bold point stays readable on its own, so anything important is still said in chat, never only behind a link. The final "Details:" line stays.

Rejected: changing the global rule before Matt confirms the links actually land on the heading.

Undo: nothing changed yet.

## 18:36 Heading links rule made global

Matt tapped the demo links: they open at the heading ("Yes, they work! ok, I REALLY love it"). He asked to also make generous whitespace around each linked section a rule.


---

### Rule text

Added to `.rules/core_safety.md` (Every Word Costs Matt > details file), rebuilt with `build_rules.py` (CLAUDE.md, GEMINI.md, Codex AGENTS.md), and one line in `~/.claude/CLAUDE.md`. Each non-trivial reply line wraps its bold point in a link to its own unique `###` subsection under the reply's `## HH:MM` section. Tiny replies skip it. The line still carries the point on its own.


---

### Whitespace choice

I read "whitespace around each section" as the details file sections (the place he lands). Markdown previews collapse extra blank lines, and raw HTML like `<br>` shows as text in the Claude app, so the reliable spacer is blank line + `---` + blank line before each linked heading. Rejected: `&nbsp;` lines (fragile, may render as text). If he meant the reply lines instead, those already get a blank line between each.


---

### Still open

Project instructions (Talking to Matt) need the same line; asked the coordinator to add it. Mac-path anchors (`/Users/matt/...#slug`) in the Code tab are untested; only `/mnt/project-files/...#slug` was confirmed.

Undo: revert the commit on this branch and rebuild rules; remove the added sentence in `~/.claude/CLAUDE.md`.

## 19:20 Why two links showed raw paths

Matt asked why the top two links in the mixer thread's reply showed as file paths. Checked the rendered page in the built-in browser (DOM text of each link chip): "Hue:" and "Wiggle:" showed the path; "Secondary functions:", "Shift look:", "Record stop:" showed labels. Same markdown shape, anchors all existed, so the difference was the label.


---

### Label test

Posted a test reply here with five variants and read the rendered page: `[**Hue:**]` path, `[Hue:]` (not bold) label, `[**Hue rate:**]` label, `[**Abcdefghijklmnop:**]` path, `[**Hue**]` path. So a bold label with no space in it falls back to the raw path; length doesn't matter. Likely a renderer quirk in the Claude app, not something we control.


---

### Fix

Rule now says bold link labels need at least two words (`.rules/core_safety.md`, rebuilt; `~/.claude/CLAUDE.md`). Rejected: dropping bold inside links (plain one-word works, but bold is how Matt skims). Undo: revert the commit.
