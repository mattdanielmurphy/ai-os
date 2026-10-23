# Blind two drafts

## 18:05 Summary, where it stood, next steps

Matt asked (via the coordinator) to split the "blind two drafts" idea out of the Claude vision HUD thread
(cmsg_01CUPXyY9oUwKVDFREVDpYDrRr3KmhjyB41KcxfAQSwP4Q) into its own thread. I read that thread and its
details file (docs/details/2026-10-21-claude-sees-hud.md#blind-two-draft-method). No vision or Figma
work done here; another thread owns that.

---

### The idea in short

1. Matt writes his own take first (voice memo or a few rough lines) into a sealed file, e.g. `ideas/matt-blind.md`.
2. A separate Claude session drafts its own take from a one-line problem statement only, told not to open the sealed file.
3. Both go side by side; merge the best of each.
4. Competitor research comes last, only as a "did we miss anything?" check.

Same trick as blind peer review / "diverge before converge". Rejected earlier: Matt fully specs first
(anchors Claude), competitor research first (anchors Matt).

---

### Where it stood

Proposed once on 2026-10-22 02:09 UTC as one line in a reply; Matt never answered on it. Nothing built.
On the vision mockup he skipped his own blind draft (tired), so it hasn't been tried yet.
Now recorded in ai-os IDEAS.md.

---

### Next-step options

- **Try it by hand next time (recommended)**: on the next design question, Matt drops a 2-line voice note
  first; I spawn a blind session; we compare. Zero build. If it helps, then make a skill.
- **Make a `_draft-blind-first` skill**: one command seals his note, starts the blind session, and posts a
  side-by-side. ~1 small skill file. Rejected as first step: builds before knowing it helps.
- **Park it**: leave it in IDEAS.md.

Why hand-trial first: Matt rabbit-holes into builds; the method only needs two sessions and a file,
so test whether the comparison is actually useful before automating.

## 18:12 Made it a standing rule, not a skill

Matt: skills are a bad pattern for him because he has to remember they exist. Instead, agents should
suggest the think-alone-first step themselves whenever we design UI/UX with room for innovation, and
explain the benefit.

---

### Where the rule lives

- `.rules/core_safety.md` 1j "Think Alone First on Open UI/UX Design", compiled into ai-os CLAUDE.md / GEMINI.md via build_rules.py.
- 1k "Proactive Behaviour Over Skills He Must Remember": the general lesson behind it.
- One line each added to `~/.claude/CLAUDE.md`, plus a memory file `think-alone-first-design.md`.
- IDEAS.md entry marked as done-as-rule.

Not tested in a live design task yet; the first real open-ended design thread will show whether agents pick it up.
Undo: revert this commit and remove the two lines from ~/.claude/CLAUDE.md.

---

### Live status

Pushed to origin/main. Your global ~/.claude/CLAUDE.md has it now, so every new Claude session sees it. The main ai-os checkout on the Mac is 3 commits behind because another session has uncommitted edits there; I didn't touch those. It catches up on its next pull.
