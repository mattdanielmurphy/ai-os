# Claude habit gate (2026-10-22)

## 09:20 Idea recorded + options

Asked (via coordinator): record the idea of gating Claude use behind a habit step, and propose the smallest way, building on the check-in habit ladder. Don't build until Matt says "make it".

Recorded in `IDEAS.md` ("Earn Claude with a habit step").

---

### Existing tools checked

- **macOS Screen Time** (built in): Downtime / App Limits on Claude.app. Zero code, but it knows nothing about the ladder; "Ignore limit" is one tap.
- **one sec / Opal** (third-party blockers): add friction before opening an app; one sec can run a Shortcut. Not installed; paid; also blind to the ladder unless glued with a Shortcut.
- **Claude Code hooks** (already used on his Mac): a `UserPromptSubmit` hook can refuse a prompt and show a message. Fires in the Code tab and in project threads (they run as Claude Code on his Mac). Can read the ladder's `data/history.jsonl` directly.

---

### Option A: soft hook gate (recommended)

- New ladder habit, e.g. "Logic study", minutes, levels 5 → 10 → 15 → 20 → 30, weekdays only.
- A `UserPromptSubmit` hook, active only after a set time (e.g. 14:00) on habit days.
- If today's step isn't recorded: the first prompt is held with one line, "5 min of logic first? Reply `done` or `skip`."
- `done` records it (`ladder.py record logic=5`); `skip` passes through and counts as a miss, so the ladder shrinks the dose instead of nagging.
- Only new prompts from Matt are gated; running agents and scheduled jobs are never blocked.
- Size: ~40 lines plus a ladder entry. Gentle by design: the escape hatch costs nothing but a smaller dose tomorrow.

---

### Option B: Screen Time Downtime

- Downtime on Claude.app (and claude.ai in Safari/Chrome) 14:00–14:30 on weekdays.
- No code. But no link to the ladder, no growth or pull-back, and it blocks agent replies he wants to read.

---

### Option C: hook gate, hard mode

- Same as A, but no `skip`: Claude prompts stay blocked until the step is recorded.
- Rejected as default: it punishes instead of shrinking the habit, against his "pull back after misses" rule, and could lock him out mid-deadline.

---

### Risks / untested

- Nothing built. Hooks also fire in other agents' sessions on his Mac; the gate must only check Matt-typed prompts (not relays or scheduled wakes).
- Undo: remove the hook entry from settings and the habit from `ladder.json`.

## 09:25 Refinement: the gate hands over the questions

Matt: "you don't even ask me, you just give me an artifact with the logic questions" (his message looked cut off mid-sentence).

---

### Revised Option A logic

1. After 14:00 on weekdays, if today's logic step isn't recorded, Matt's first prompt is held.
2. Instead of a question, the hold reply links a ready-made logic artifact: today's dose worth of questions (5 min to start), from his current logic course material.
3. Finishing the set records the step in the ladder and unlocks Claude for the day.
4. Escape hatch kept (`skip`): passes through, counts as a miss, so the dose shrinks rather than nagging.

Unresolved: where questions come from (course notes per SCHOOL.md vs generated); whether the artifact reports completion back itself (artifact database) or Matt replies `done`.

## 09:55 Built and live

Matt approved with 👍 (I wrongly asked him to confirm it; rule saved: approvals are "Reply 👍 to …").

---

### How the gate works

- `services/checkin/habit_gate.py`, a Claude Code UserPromptSubmit hook, config `"gate"` in `ladder.json` (habit `study`, after 14:00, weekdays from the habit's `days`).
- It never blocks a prompt. It adds context telling the agent to hand over today's logic practice page (an Artifact, questions ~ 1 per minute of today's study dose, answers hidden until tapped) and hold his request.
- 👍 reaction or "done" records the dose in the ladder history and unlocks for the day; the agent then carries on with the held request. "skip" records 0 and unlocks; the ladder shrinks the dose after two short days.
- First thread builds the page and saves its URL (`habit_gate.py url`); other threads reuse it that day.
- Only Matt's own messages: agent/coordinator relays, side-session events, scheduled runs and non-👍 reactions pass untouched.
- If the morning check-in already recorded study for today, no gate.

---

### Decisions

- Context, not a hard block: a blocked prompt in a project thread would just look like Claude ignoring him (no message on the project page). Context also lets the agent resume his request after.
- Questions generated per day by the agent from SCHOOL.md's current logic unit, not a fixed bank: always matches where he is in the course.
- Any crash in the hook passes silently, so the gate can never lock him out.

---

### Untested / risks

- Not yet tried live in a real afternoon thread (tests cover the logic with simulated prompts and times).
- Each thread's agent decides how to word it; if one ignores the context, the gate just doesn't fire there.
- Undo: set `"enabled": false` in `ladder.json`, or remove the hook line from `~/.claude/settings.json`.
