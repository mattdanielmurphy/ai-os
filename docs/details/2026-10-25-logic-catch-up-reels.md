# Logic catch-up reels (2026-10-25)

## 22:30 Four catch-up reels with Ask

**What Matt asked (via the coordinator):** he missed the last two Symbolic Logic classes and hasn't studied; Midterm 2 is Nov 4. Make explainer reels from the textbook covering what he missed, with a way to ask questions as he goes, and make ask-as-you-go a general feature of explainer reels. School rule: explain only, never do assigned or graded work.

---

### What he missed

The syllabus puts Unit 5 (first-order logic: language and syntax, forall x: Calgary ch. 23–29) in weeks 6–7, Oct 14 and Oct 21. Those are the two missed Wednesday classes. Unit 6 (semantics, ch. 30–35) starts Oct 28, so it isn't covered. Earlier notes in `~/Documents/School/Symbolic Logic/Unit 5/catch-up.md` agreed.

---

### The four reels

- Logic 1 · All and Some (ch. 23–24): pieces of FOL, ∀/∃, domains, not-flips, the four patterns, empty predicates, scope. https://claude.ai/artifact/BrBy9VCdTbZapqZ4Fw1Zrs
- Logic 2 · Two-Place Predicates (ch. 25): gaps and order, quantifier order and the shift fallacy, stepping stones, hidden quantifiers (Astell). https://claude.ai/artifact/6DrNZ9BD27r9EPHbUgaxww
- Logic 3 · Identity and Counting (ch. 26–27): =, only/except, at least/at most/exactly, grammar, free vs bound, brackets. https://claude.ai/artifact/MDkbTk9z3DjtXeWVVisAqt
- Logic 4 · The and Ambiguity (ch. 28–29): Russell's analysis, empty descriptions, inner/outer not, possessives, both/neither, Strawson and Donnellan, scope ambiguity. https://claude.ai/artifact/2webCnZjMNJtHwMBDgtGxW

Each starts from the symbols (his PHIL 120 rule: start at the definitions, small winnable steps). Every example is my own; none of the textbook's practice exercises appear or are answered. The book is CC BY 4.0 and credited at the bottom of each page. 12 "Your turn" checks in total, made up by me; the reading pauses at each until he tries it once.

---

### Why Artifacts, not Vercel pages

The rule says pages go on Vercel unless they need Artifact runtime features. Ask needs one: the `sample` capability lets the page ask Claude on Matt's own account with no API key. There is no Anthropic key in ai-os `.env` or on the matt-pages Vercel project, so a Vercel /api/ask would need him to create one. Rejected for now. Narration audio ships as files inside each Artifact (the page's network is blocked, so it can't call the Vercel /api/tts).

---

### How Ask works

`services/reels/scroll/kit/ask.js`. Button bottom-left (or A key), "Ask" in the long-press bar, "Ask about this" under each check. It pauses the reading, shows the sentence he's on, offers 4 quick questions, streams the answer, and resumes when closed. The prompt includes the whole page text, the sentence, the chat so far, and in school mode strict rules: explain, invent new examples, give hints; never solve, symbolize, prove or check textbook exercises, assignments, quizzes or exams; coach instead of answering "symbolize this". Each question uses Matt's own Claude usage; the first one asks him to allow it.

---

### Tested and untested

Tested headless (muted Chrome, fake Claude): words wrap, narration audio loads and drives the highlight, reading pauses at a check and resumes, Ask opens/pauses/sends the integrity rules and sentence/renders the answer/resumes, no sideways scroll on a phone in light and dark, no page errors, on all four reels.

Not tested: the real claude.ai viewer. Audio served from Artifact files, and the real `sample` consent prompt, haven't been tried in a real browser (opening reels in the browser pane has hung sessions before). If the voice doesn't play there, the page reads silently and says "Voice unavailable here".

---

### How to undo

Delete the four artifacts from claude.ai, and revert the commit that added `services/reels/scroll/`.
