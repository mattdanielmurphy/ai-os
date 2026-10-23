# Split into separate projects

## 07:10 Migration plan for splitting "Everything"

**Asked:** plan how to split the catch-all Everything project into focused projects, each with its own coordinator. At least Slub Utils and a proactive personal assistant; suggest others. Cover memory, threads, routines, repos, per-project instructions, and which steps only Matt can do. Move nothing yet.

**What I looked at:** all ~190 thread sessions in the project, the project library, `coordinator/custodian-state.md`, every routine on the account (`RemoteTrigger list`), the desktop scheduled tasks, Matt's launch agents, and `~/projects`.

---

### Four projects, not five

| Project | What lives there | Coordinator's job |
|---|---|---|
| **Slub Utils** | Every suite utility: Hammerspoon modules, hud-kit apps, trackpad mixer, palette, launcher, file search (findd), clipboard, dictation/quote tools, claude-control banner, tweaks panel, design system and exemplars | Route build/bug asks, keep the palette and shared-module rules |
| **Assistant** | Morning and afternoon check-ins, health (Mounjaro, pickleball), habits ladder, reminders, Hue lights, errands (DATS, shopping, TV/PS5 home stuff), **and school** | Proactive: posts check-ins, deadline nudges, follow-ups |
| **Music** | Slub synth work, qwerty MIDI, Ableton, piano capture, two-knob ADSR, chord/bass display, scale playlists, generative ambient, song key detector | Music projects and research |
| **AI OS** (rename Everything) | ai-os rules, coordinator routing, Claude workflow tooling (handoffs, reply review, details links, cold threads, voice-call bridge, Mac connector), model charts, anything that fits nowhere else | Catch-all and meta |

### School stays inside Assistant

I considered a separate School project. Rejected for now: the assistant's best feature is nudging about deadlines, and it would need to see school anyway. School study threads (Logic ladder, CMPUT labs, World Music quizzes) are still separate threads inside Assistant. If school threads swamp the assistant, splitting it out later is cheap.

### Why AI OS keeps the old project

Renaming Everything instead of making a fifth project keeps its history, library files and custodian routine in place. Only the other three are new.

---

### Only Matt can do these (claude.ai UI)

1. Create three projects: **Slub Utils**, **Assistant**, **Music**. Make each private.
2. In each one, approve the folder `~/projects/ai-os` (and the extra repos below) for Remote Control threads.
3. Paste each project's instructions (I draft them; see below).
4. Connect connectors the Assistant needs (Calendar, Gmail) in that project.
5. Rename Everything to **AI OS**.

Everything after that, agents can do from inside each new project.

---

### Threads: they don't move

There's no tool to move a thread between projects. So:

- **Resolved threads stay** in AI OS as history.
- **Live threads** (open, waiting on Matt or review-ready) get a fresh thread in the new project from a cold handoff (`scripts/cold_handoff.py`), linking back. Then the old one is resolved.
- I'd only carry over threads Matt still cares about; the custodian can ask once per batch.

Live threads by destination (from the session list, 2026-10-23):

**Slub Utils:** Mixer vs Audio Hijack recording · TypeWhisper clone in the suite · Shared app architecture constraints · Quote tool queue vs send · HUD layout traffic control · Personal design system and palette · Preview buttons for new builds · Agents triggering dictation · Sticky per-app reminder notes · Hammerspoon suite as its own app · Public export of utilities app · Launcher file search · Agent-aware clipboard manager · Mixer on built-in trackpad · Live tweak panels / Tweaks presets · GIF finder · Decide where key presses should go

**Assistant:** Voice-friendly morning check-in · Morning check-in, continued · Sleep reminders and SUB habit · Logic catch-up and study block · Logic gate flashcards · CMPUT 174 Lab 4 · Class schedule and course progress · Claude as habit reward · Agent wake-up phone call · Hard-to-dismiss alarm clock · Mounjaro dose and pickleball prep · AI cat toy mouse

**Music:** Live chord and bass display · Always-on piano and MIDI capture · Plugin crash hunt, continued · Claude-driven generative ambient · Two-knob ADSR design · Scale practice playlists · Live song key detector · Piano standalone into Ableton

**Stay in AI OS:** Seamless cold-thread handoff · Quiz-style walkthrough / Interactive reply review · Less Mac dependence · Voice wake word assistant · Smart prompt queue · Live thread chains page · Coordinator vs DIY connector · Import Mac agent rules

---

### Routines and scheduled jobs

| Job | Now | Plan |
|---|---|---|
| Project custodian (hourly, `trig_0172…`) | Everything | Stays in AI OS. Each new project gets its own custodian after its first week, cloned from this one (state file path changes per project) |
| Reminder: XIME show, Oct 26 | Everything | Recreate in Assistant, then disable the old one |
| Reminder: Autoethnography due, Oct 29 | Everything | Same |
| Future one-off reminders | coordinator creates them in Everything | Assistant coordinator creates them |
| Morning check-in (desktop task, 07:45 daily) | iMessages Matt a page link; not tied to a project | Keep the task; change where its thread/links point to Assistant |
| Afternoon check-in | doesn't exist yet | Build in Assistant as a new routine (separate ask) |
| Launch agents (hue-daily, nightly restart, findd, palette, mixer…) | Mac, not project-bound | No change |
| Voice task inbox / Mac connector `send_task` | sends to the Everything coordinator | Add a target project argument, default Assistant; utilities go to Slub Utils |

Routine IDs are tied to one project channel (`hearth_channel_id`), so reminders must be recreated, not moved.

---

### Memory and shared files

- **Mac memory and `.rules/` stay global.** Matt's rule: every rule applies everywhere. Nothing to split.
- **Project memory** (the coordinator's store): I couldn't read it from this thread; there's no read_memory tool here. The AI OS coordinator should export it once, and each new coordinator gets the subset for its area, plus a copy of the global "how to talk to Matt" notes.
- **Project library files** don't cross projects. Copy per project: Slub Utils gets `ARCHITECTURE.md`, `EXEMPLARS.md`, `UTILITIES.md`, `VISION.md`, palette and mixer details; Assistant gets check-in details; every project gets `coordinator/routing-rules.md`.

---

### Repos per project

- **Slub Utils:** `~/.hammerspoon`, `hud-kit`, `trackpad-mixer`, `claude-palette`, `lidstay`, `hs-rcmd`, `app-hints`, `mindful-browser`, `break-reminder`
- **Assistant:** `ai-os` (`services/checkin`, Hue, reminders), `school`
- **Music:** `qwerty-midi-plugin`, `qwerty-midi-hammerspoon`, `talk-to-synth`, `ableton-llm-composer`, `synthesia-clone`, `music-cross-linker`
- **AI OS:** `ai-os`, `model-charts`, `mattmurphy.ca`

ai-os is shared by all four (rules, scripts); that's fine since Remote Control threads open it per thread.

---

### Per-project instructions

Each project's instructions = the current pointer-only block (Where rules live, Talking to Matt, Cross-session essentials) + 3–5 lines of scope:

- **Slub Utils:** what the suite is, palette + shared-module + tweaks rules pointers, repos list.
- **Assistant:** be proactive; school pointer (`docs/SCHOOL.md`); no sleep reminders; habits tiny-first; reminders go to Apple Reminders.
- **Music:** no AI music; Slub synth focus; Apple Music link rule.
- **AI OS:** keeps coordinator routing (full version).

Drafts get written as files once Matt 👍s; he pastes them.

---

### Order of steps after 👍

1. I write the four instruction drafts and the memory split list (files, no moves).
2. Matt creates the three projects, pastes instructions, approves the folder.
3. Agents in each new project: recreate reminders, copy library files, start fresh threads for the live threads above.
4. Update the voice/Mac-connector routing to target projects.
5. After a week: per-project custodians.

### Risky or untested

- Cross-project routing for `send_task` hasn't been checked; it may only know one channel.
- Whether a routine can be created for a project from a thread in another project is untested; plan assumes it's done from inside the new project.

### How to undo

Nothing has moved. If the split is dropped, nothing to undo; if done and regretted, the old Everything (AI OS) still has all history.
