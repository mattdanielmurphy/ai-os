# "What Claude sees" HUD idea — details

## 20:12 First reply: anchoring, existing tools, smallest test

**What Matt asked** (written in the PS5 recording thread after the ui-recorder worked): a HUD showing which frames Claude is looking at; Claude presenting key frames with markup; precise geometry/velocity (sports play-by-play, live player analytics); how to make Claude understand motion; whether an MCP tool already does this; and how to protect his own UX ideas from being anchored by competitors (or by Claude) while still collaborating.

**Stage:** idea only. Nothing built. Coordinator brief: don't build until he says "make it".

---

### Blind two-draft method

How to keep his ideas un-anchored while still collaborating with Claude:

1. Matt writes his own take first (a voice memo or a few rough lines, no polish) into a sealed file, e.g. `~/projects/<project>/ideas/matt-blind.md`.
2. A separate Claude session designs its own take from a one-line problem statement only. It is told not to open the sealed file.
3. Only then do we put both side by side and merge the best of each.
4. Competitor research comes last, and only as a "did we miss anything?" check.

Why: this is the same trick as blind peer review / "diverge before converge" in design. Each side's first draft stays independent, so neither anchors the other. It costs one extra short session, not a big system.

Rejected: having Matt fully spec the GUI before Claude starts (that anchors Claude to his view, which he said he doesn't want), and researching competitors first (anchors Matt).

---

### Existing tools question

I did not search yet, on purpose: he fears anchoring. I asked him to choose: (1) yes/no only, (2) names only, (3) full details. Recommended 1 (yes/no), since it answers "does this exist?" without showing anyone's design. Honest prior without searching: pieces almost certainly exist (screen-recording MCPs, video-analysis tools, sports-tracking products like player-tracking analytics). A tool that shows the user the exact frames an AI agent is looking at, with markup, is less likely to be common, but I haven't checked.

---

### Smallest first test

Before any HUD: on the next recording, Claude picks its 4 key frames, draws boxes/arrows on them (plain image markup with a script), and posts them as one contact-sheet image in the thread with one line per frame ("here I see X"). That tests the core claim (Claude can show what it sees, and whether it picked the right frame) with zero new UI. If that's useful, the HUD is just a live version of the same sheet.

---

### Motion understanding

Claude sees still frames, not video. Motion has to be handed to it: frame-difference images (what changed), short frame strips in order, or numbers from a tracking script (positions per frame → speed). The ui-recorder already pairs frames with input events, which is a start. Sports-grade geometry/velocity needs a real tracking library (computer-vision tracking), not Claude eyeballing frames. Kept out of the reply beyond one line; it's a later step.

---

### Public-later

Coordinator already flagged "planned public project" as the design-for-others trap. Plan: build for Matt, keep personal info out and keep it a separate module so it could go public later. No features for strangers.

**Undo:** nothing to undo; no code changed.
