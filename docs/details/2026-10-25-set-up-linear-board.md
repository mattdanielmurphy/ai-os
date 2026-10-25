# Set up Linear project board (2026-10-25)

## 20:20 Board seeded; states need Matt

Coordinator brief: one team, states Idea / Planned / Live on Mac / Paused / Done, 8 area labels, seed current projects with a "where it's at" line, note the proposed caps without enforcing them.

---

### Linear connector works

The Linear connector loaded fine in this session (workspace `mattmurphy`). No proxy 403.

---

### States need a two-minute rename

Linear's connector has no tool to create or rename workflow states, and the browser pane isn't signed in to Linear (I can't sign in for Matt). So I used the existing team "Mattmurphy" (key MAT) and its default states, mapped:

- Backlog → **Idea**
- Todo → **Planned**
- In Progress → **Live on Mac**
- Done → Done; Canceled stays as "dropped"
- **Paused** doesn't exist yet. Cards that should be Paused sit in Backlog with "Paused." at the start of their description: MAT-12 qwerty MIDI, MAT-15 UI Mixer, MAT-16 palette, MAT-23 check-in, MAT-32 HUD slots, MAT-33 reply review page.

Matt's part: in Settings → Teams → Mattmurphy → Workflow (https://linear.app/mattmurphy/settings/teams/MAT/states) rename the three states and add a "Paused" state (Started group is the usual spot). Renaming keeps cards where they are. Then an agent moves the six Paused cards.

Rejected: a temporary "Paused" label (clutters the area labels, which should only be areas); renaming the team (no tool, and "Mattmurphy" is fine for one team).

---

### Labels created

School, Slub, Money, Physical health, Mental health, Job, Notes & old projects, Mac inventory, as workspace labels with one-line descriptions. Colours left at Linear's default (all the same blue) because the suite palette isn't picked and no colours may be invented. Linear's starter labels (Feature, Improvement, Bug) left alone.

---

### 30 cards seeded

MAT-5 to MAT-34, from PROJECT_BOARD.md (stale since Oct 17), IDEAS.md, SCHOOL.md, ABOUT_MATT.md and the open/blocked/review-ready project threads. Each description starts with "Where it's at". School cards carry due dates (Logic midterm Nov 4, CMPUT LockDown test Oct 29, autoethnography Oct 30).

Only one card is Live on Mac: MAT-34 "Life OS: get everything organized" (this work). I didn't mark anything else live because I can't tell what's actively running on his Mac right now.

Judgement calls: software projects (crossword, Slub Utils, reels, ideas) all got the Slub label, since the area is "Slub / software". The PROJECT_BOARD ai-os backlog became one card (MAT-30) instead of ~20, since most items look stale. Linear's 4 onboarding issues were already canceled; left them.

Not added: Hue lights, finished threads, the "Allow rm in scratch folders" thread (rule already exists).

---

### Caps noted, not enforced

Team doc "How this board works" (https://linear.app/mattmurphy/document/how-this-board-works-b5c045e51281) explains the stages and labels and lists the caps as a proposal: max 2 Live on Mac, a larger ongoing cap (number not picked). Nothing enforces them.

Undo: archive MAT-5..34, retire the 8 labels, delete the doc.

## 21:52 States renamed in Chrome; rule saved

Matt: "you don't need the API to control a web app for me. YOU do it". He's right: Claude in Chrome (his real Chrome, Browser 1 profile) is signed in to Linear. With a light claude-control clearance I opened Settings → Issue statuses in a new tab and renamed Backlog → Idea, Todo → Planned, In Progress → Live on Mac, and added Paused under Started. Closed the tab, released clearance. Then moved MAT-12, 15, 16, 23, 32, 33 to Paused through the connector and removed the "Paused." prefix from their descriptions.

The switch_browser Connect prompt timed out (no click came through), so I tried "Browser 1" directly; it was signed in.

Rule saved to `.rules/core_safety.md` (1n): when a connector can't do a web-app step, drive the UI with Claude in Chrome instead of giving Matt steps. Also forwarded his "too concise to be confusing" feedback to the coordinator to route as a rule change.

Undo: rename the states back in Settings → Teams → Mattmurphy → Issue statuses.
