# Getting life organized (2026-10-25)

## 18:50 Opening: directions and questions

Matt asked to discuss getting his life as organized as possible, with no building yet. Usage/CodexBar part went to a separate thread.

What I read first: `docs/ABOUT_MATT.md`, `docs/SCHOOL.md` (refreshed Oct 20, so slightly stale), `services/checkin/`, `PROJECT_BOARD.md` (last updated Oct 17, stale).

What already exists (the raw pieces):
- Apple Reminders for to-dos.
- Morning check-in (`services/checkin/`) with a habit ladder.
- `SCHOOL.md` with schedule and due dates (manual refresh from Canvas).
- `PROJECT_BOARD.md` (stale), Obsidian vault, ~60 project threads.

My read: the problem isn't missing tools, it's too many places. With a bad memory, every extra place is a place things get lost.

---

### One inbox

Everything he thinks of (to-do, idea, worry) goes to one capture point: voice, a key, a text. Agents sort it into Reminders, project IDEAS files, calendar. He never decides where something goes.

---

### One daily glance

The morning check-in becomes the single "today" view: what's due (from Canvas), 1 to 3 picks, nothing else. Tiny start, ramps slowly.

---

### Weekly reset

A 10-minute Sunday chat with Claude: what's coming this week, what slipped, what to drop. Builds on voice calls he already likes.

Rejected for now: a big new app or dashboard first (the dashboard ideas thread already exists; this should decide what it shows rather than duplicate it). No bed/wake reminders.

Untested / open: which area feels most out of control is a guess until he answers.

## 19:05 Overseer + specialists: proposed shape

Matt said it's everything, not one area: too much, no central place, agents don't know his whole life. He wants one overseer and specialists, named the areas (school, Slub, money, health physical/mental, part-time job, notes + old projects, Mac inventory), asked for guardrails on building more Mac tools / custom harness, a CEO rhythm, and worried about things lost in threads. Recorded in `IDEAS.md` ("Life OS") and memory.

---

### Yes it makes sense

One agent can't hold everything; the fix is files, not a bigger agent. Each area gets one short "area brief" file (what's true now, what's open, what's due). A specialist only reads its own brief. The overseer reads only the top 5 lines of each brief. That keeps every agent's context small and makes nothing depend on an agent remembering.

---

### Eight areas

School, Slub/software, Money, Physical health, Mental health, Part-time job, Notes and old projects, Mac inventory. Job gets its own area as he asked. Rejected: merging health into one area (he named two different kinds).

---

### CEO rhythm

Two fixed times a day. Morning: he gives orders (voice or text) to the overseer, who routes them. Evening: one short report, at most 3 things that need him. Everything else waits for the report. Times are his call (not bed/wake times, no reminders for those).

---

### Build guardrail

Proposed: no new global Mac tool until every existing one is listed in the Mac inventory with how to turn it off and a test. After that, one new tool at a time, and only after the last one has a week with no bugs. Agents flag violations instead of building. Also: stay on Claude app; no custom harness work.

---

### Lost things sweep

One pass over this week's threads (~60) to pull every open loose end into the area briefs. The existing "Custodian for loose ends" thread overlaps; check it before doing this.

---

### Suggested first step

Write the 8 area briefs from what's already on the Mac and in threads; Matt only reviews. Reversible, small, and every later step (budget, job search, inventory) needs it. Waiting for his 👍 since he said discuss first.

## 19:20 CEO rhythm too optimistic; project management software

Matt (comment on CEO rhythm): far too optimistic, he's much more hands-on. Suggests max 2 projects actively live on his Mac at once, a much larger cap on ongoing projects, fine as long as each one's stage is clear. Feels he needs project management software.

Dropped the twice-a-day CEO rhythm. Recorded the WIP caps as his proposal (not yet a rule, he said "maybe").

---

### Two live projects cap

"Live on Mac" = an agent is actively changing things on his machine. Max 2. Everything else sits in a named stage. Agents check the board before starting work and flag if a third would go live. Untested idea, enforcement not designed.

---

### Stages for every project

Proposed stages: Idea → Planned → Live on Mac (max 2) → Waiting/Paused → Done or Dropped. Every project and life area task carries one.

---

### Project management tool options

Looked for existing tools first (rule 1a). Notion is already connected to Claude here (Notion connector), so agents can read and update a Projects database with Stage and Area fields, and it covers life areas, not just code. Linear is the nicest for software stages and has a Claude plugin, but needs sign-in and is built for code teams. GitHub Projects is free and close to his repos but code-only. Rejected building his own (guardrail he just asked for). Recommendation: Notion, with Linear as the alternative if he wants a stricter software-style board.

## 19:20 Correction: Notion

The coordinator pointed out two things I missed: Matt tried a Notion dashboard demo on Oct 18 and hated it (finicky property list, bad memories, said he didn't want Notion; reopened the idea Oct 24), and the Notion connector is failing here (proxy 403), so "already connected" was wrong. I should have searched past threads before recommending it.

---

### Non-Notion options

- **Linear** (recommended now): a fast board with stages built in, little property fiddling, a Claude plugin exists. Needs a one-time sign-in through /mcp in a Claude terminal. Fine for life areas even though it's made for software.
- **GitHub Projects**: works today through the gh CLI agents already use, free, sits next to his repos. Plainer and code-flavoured.
- Craft (installed, connector present) is a docs app more than a board; left out.

## 19:58 Linear chosen

Matt 👍'd Linear. I can't create accounts or run sign-ins, so he does two things: make a free account at linear.app (if he has none), then connect the Linear connector from the card in the thread. After that I'll set up the board: one team, stages Idea / Planned / Live on Mac (max 2) / Paused / Done, a label per life area, and load his current projects from PROJECT_BOARD.md, IDEAS.md and open threads so he only reviews.

---

### Board setup plan

- Workflow states map to the stages above.
- Labels: School, Slub, Money, Physical health, Mental health, Job, Notes & old projects, Mac inventory.
- Seed: active projects and open threads, each with a one-line "where it's at".
- Not decided yet: how agents enforce the 2-live cap (likely a rule: check Linear before starting work on his Mac).
