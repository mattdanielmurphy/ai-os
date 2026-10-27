# About Matt: where things live

Read this first in any session. It holds pointers, not copies: open the linked file when you need the detail.
No secrets or sensitive personal data belong here. Keep it short; update it when a fact changes.

## Rule: search the Mac before asking Matt about himself
Before asking Matt anything about himself, his work, his files or past conversations, look here first:
1. This file.
2. QMD (vault + all past threads): `qmd query "<question>"` or the `qmd` MCP tools.
3. Spotlight: `mdfind -onlyin ~ "<words>"` or `mdfind -name "<filename>"`.
4. Old Gemini/Antigravity threads: `python3 ~/projects/ai-os/scripts/threads.py search "<words>"`.
Ask him only if all of these come up empty, and say what you searched.

## Right now (update as it changes)
- **Location**: Edmonton, Alberta (Mountain time).
- **School**: University of Alberta, Fall 2026: CMPUT 174, MUSIC 102 (Intro to World Music), PHIL 120 (Symbolic Logic, *forall x* textbook), plus XImE ensemble (MUSIC 193A). **Class times, rooms, due dates and where he is in each course: [`docs/SCHOOL.md`](SCHOOL.md)** (check its refreshed date). Canvas: signed in via the built-in browser pane (and a dedicated Chrome profile).
- **Music**: makes music in Ableton Live; plays drums, piano and guitar/bass. Gear at home: Yamaha digital piano (X-stand, sustain pedal), electronic drum kit (packed away as of Oct 2026), electric guitar/bass, studio monitor.
- **Listening gear / smart home**: owns a receiver and a very big speaker with strong bass (plans to try them in the bedroom first), a JBL Charge 6 (finds it thin and bad-sounding) and a Raspberry Pi. Frugal about audio gear ($300 for an amp is too much). Wants a voice-controlled smart speaker that runs his lights with a better assistant than Siri; won't pay for a Google AI subscription. Idea in progress: Shairport Sync on the Pi + a shortcut that starts Claude voice mode (Oct 2026).
- **Home/desk**: apartment in Edmonton; MacBook on a riser + external monitor, Logitech ergonomic keyboard and mouse, AirPods. Has a bike and a kettlebell.
- **Car**: 2009 Toyota Yaris sedan, manual (Oct 2026); rarely downshifts, coasts in neutral and brakes little (Alberta flat roads). No CarPlay/Android Auto, uses his phone; has an old iPad mini he might mount as a dash screen. Buys gas around Edmonton / Fort Saskatchewan.
- **Voice chat**: likes claude.ai voice for thinking out loud and for in-the-moment support while walking around (wants more of that, Oct 22), then hands building to the project coordinator (`docs/VOICE_TASKS.md`). Calls are reviewed with the `_review-voice-calls` skill.
- **Apple Watch** (since ~Apr 2026): barely uses it. Main wish: persistent now-playing controls (phone and Mac music) and one-tap favourite. Interested in a fully programmable smartwatch (idea, Oct 23).
- **Coffee**: Hoffman's single-cup V60 (15 g / 250 g, grinder ~4.4, Sharpie channel + swirls); prefers paper filters; has a Doppelganger Goods cloth filter mainly for cold brew.
- **Calls with Tyler**: FaceTime audio; owns Audio Hijack; ~$190 Deepgram credits; building his own live voice mode / call transcriber (Oct 23).
- **Sport**: plays in the U of A pickleball league as a free agent (paid $110, Fall 2026); games are at 9 pm.
- **Main projects**: ai-os (this repo, his agent setup), qwerty MIDI plugin, daily mini crossword (mattmurphy.ca). Decided Oct 22 to build an anti-sycophancy AI therapist harness (not started; idea in `IDEAS.md`).
- **Brother**: one of his brothers also builds software with Claude; they work well together. Family notes: vault `Family Relationships & Dynamics.md`.
- **Slub** (2026-10-22): software company Matt is starting with his brother, focused on audio. The brother is strong in audio engineering and plugins and is building Ableton plugins that do multimodal sample analysis for very accurate categorisation. Shared goal: make generative synthesis more accessible, with great interfaces and sound.
- **Working style**: procrastinates and rabbit-holes into big builds; keep steps small, but new projects are no longer flagged (Oct 22). Tends to feel he has to let people off the hook, then regrets it, and wants to change that. Full preferences: `~/.claude/CLAUDE.md`.

## Where things live
| What | Where |
|---|---|
| Agent rules (single source) | `~/projects/ai-os/.rules/` → built into `~/.claude/CLAUDE.md`, `~/.gemini/GEMINI.md`, `~/.codex/AGENTS.md` by `scripts/build_rules.py` |
| Claude's own memory | `~/.claude/projects/-Users-matt-projects-ai-os/memory/` (`MEMORY.md` index) |
| Notes / wiki (Obsidian) | `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/` (start at `index.md`) |
| U of A planning notes | vault `U of A/` (dashboard: `00 - Master Dashboard & Executive Overview.md`) |
| School schedule + due dates snapshot | `~/projects/ai-os/docs/SCHOOL.md` (refresh: `scripts/canvas_school_snapshot.js`) |
| Course files and syllabi | `~/Documents/School/<course>/` (`CMPUT 174`, `World Music`, `Symbolic Logic`, `XIME`) |
| U of A admin docs (enrolment, aid, accommodations) | `~/Documents/University of Alberta/` |
| Older school work (precalc, calculus) | `~/projects/school/` |
| Flashcard decks / daily check-in | `~/projects/ai-os/services/checkin/` |
| Code projects | `~/projects/<name>/` (each its own private repo) |
| UI design: mix-and-match tool + design lessons | `~/projects/ui-mixer/` (README, TECHNIQUES.md) |
| Project backlog | `~/projects/ai-os/PROJECT_BOARD.md` |
| Thread handoffs | `~/projects/ai-os/docs/handoffs/` |
| Past threads (searchable) | QMD collections `claude-threads`, `gemini-threads`, `antigravity-threads`, `vault` |
| Device and product manuals | `~/Documents/Books & Reference Documents/Manuals/` (books and other references one level up) |
| Ableton projects and User Library | `~/Music/Ableton/` |
| Other music files | `~/Documents/music by Matt`, `~/Documents/Audio Clips`, `~/Documents/Sounds` |
| Resumes | `~/Documents/Resumes/` |
| Personal admin (government, financial, medical, receipts) | matching folders in `~/Documents/`; open only when a task needs them |
| Identifiers for forms (name, emails, IDs) | `~/projects/ai-os/private/identity.md` (gitignored; read only when a form needs it, never copy) |
| Reminders / to-dos | Apple Reminders via `apple-reminders` CLI |

## Life facts (added 2026-10-26)
- Propranolol worked well for his performance nerves (first used around the Oct 26 show).
- Alcohol tends to bring on low moods for him.
- He wants to stop relying on being high to enjoy things and to improvise. Be warm and non-judgmental about it; don't lecture.

## Not used
- **Mem0**: installed in August, shelved 2026-10-17 (only 20 memories, nothing written after Sept 25). QMD over the vault and all threads replaced it. Data still in `~/.mem0/`; revival steps in `shelf/INDEX.md`.
- Other shelved tools: `shelf/INDEX.md`.
