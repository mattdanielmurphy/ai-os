# Slub notes folder in slub-hq (2026-10-27)

## 16:15 Built notes/ in slub-hq

Asked: a `notes/` folder in slub-hq that works with the shared Obsidian vault, holding call summaries plus Slub notes from Matt's Obsidian. Slub only.

### What's in it

- `notes/README.md`: how to open it (own vault, or symlinked into yours) and the Slub-only rule.
- `notes/calls/2026-10-24.md`: copied from Obsidian `Calls/2026-10-24-slub-call-summary.md`, with "Kristy (Tyler's girlfriend)" shortened to "Kristy" and Matt's "block time for school" to-do removed.
- `notes/calls/2026-10-26.md`: moved from `calls/2026-10-26-notes.md`.

### What was left out and why

- `2026-10-24-tyler-summary.md`: has a relationship section and a personal call mention. The clean slub-call-summary covers the same Slub content.
- `2026-10-24-tyler-condensed.md`, raw 10-23/10-24 transcripts: personal chatter mixed in.
- No other Slub notes exist in the vault (searched the whole vault for "slub").

### Pipeline change

`CALLS.md` now tells the extraction agent to write call notes to `notes/calls/YYYY-MM-DD.md` instead of `calls/YYYY-MM-DD-notes.md`. Tonight's call will land there when it ends. Rule 9 added to `CLAUDE.md`/`AGENTS.md`.

### Matt's vault

Symlink `Personal/Slub` → `~/projects/slub-hq/notes`. Works in Obsidian on the Mac. Untested risk: iCloud doesn't sync symlink contents, so the Slub folder will likely be empty or broken on his phone.

### Undo

`git revert 94cad90` in slub-hq; move `Personal/Slub` (the symlink) to the Trash.
