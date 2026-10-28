# Migration dossier: Everything (Projects) → Code-tab Coordinator, 2026-10-28

For the Everything coordinator: please check this against your project files and list anything missing.

## What the new Coordinator has
- Your final handoff (pasted by Matt): saved as `coordinator/handoff-everything-final-2026-10-28.md`.
- Rules: Matt's global rules (`~/.claude/CLAUDE.md`, built from ai-os `.rules/`), `docs/ABOUT_MATT.md`, `docs/SCHOOL.md`.
- Coordinator instructions: `docs/coordinator/code-coordinator.md`, `project-coordinator.md`; registry `coordinator/threads.json`.
- Per-project coordinators: Glass TV, Slub.

## What the new Coordinator CANNOT see
- Anything in the Projects shared folder (`/mnt/project-files/…`), incl. `coordinator/routing-rules.md`, the older `handoff-2026-10-28.md`, and any other files there.
- Old Projects threads (cmsg_…): not readable from the Code tab.
**Ask:** paste `routing-rules.md` and list any other files/folders in the project that hold rules, memory, or state not already in ai-os.

## Status of each handoff item (as of now)
| Item | Status here |
|---|---|
| Respondus testing account (Oct 29, URGENT) | Not started here yet |
| Caps Lock hold → held Esc | Thread running, waiting on Matt's OK |
| X-Ray in Glass TV | Built and live (face-clarity search, playback fixes) via Glass TV Coordinator |
| Glass TV player / Stremio add-ons / Explore | Merged catalog + vertical boxes live; rest unchecked |
| Slack vs Telegram, coordinator rules for Tyler, Claude Team, Slub UI kit | Handed to Slub Coordinator (setup export to Tyler already live) |
| Tab Tidy, call-music ducking, Linear→Plane, menu bar manager, tweaks-first, email Zoho→iCloud, lidstay, iPad Glass TV, OpenRouter in Warp, Linear board | Not started here; known only from your handoff |
| iPad Tailscale → oracle-vps | Not started here |

## Gap check closed (2026-10-28)
- **Custodian**: cloud trigger `trig_0172AJbbznF4f1E1XoaekCFH` paused; ported to launchd `com.matt.agent.coordinator-custodian` (08:41) → `scripts/coordinator_custodian.py` → Coordinator inbox; job in `docs/coordinator/custodian.md`.
- **Memory**: export prompt in `coordinator/memory-export-prompt.md` (awaiting Matt's paste).
- **Open threads**: 20 added to `threads.json` as `parked`; ideas parked in Linear MAT-45/46/47 (Figma plugin already MAT-38).
- **Cloud-only files**, on the Mac already: project-mode.md (docs/), talk-to-synth (~/projects), claude-notify / piano-hud (Hammerspoon modules), piano-airports m4a (claude-ambient/out), voice samples (services/reels/samples), Compustar manual (Documents/Manuals), dad-excel debug notes (docs/details).
- Missing and worth getting: routing-rules.md, eating-plan.md (private), custodian-state.md (via the export prompt), dad-excel fixed spreadsheets (ask Matt if Dad still needs them). Not worth it: ~200 cloud details files (history only), design screenshots, Arduino tutorial PDFs, menu-cleanup Lua (menu_bar.lua supersedes, unverified).

## Projects memory (copied 2026-10-28)
- Full verbatim export of Projects memory, custodian state and routing rules: `private/projects-memory/memory-export-2026-10-28.md` (gitignored, has health notes).
- Gap list from the migration check: `private/projects-memory/migration-gaps-2026-10-28.md`.
