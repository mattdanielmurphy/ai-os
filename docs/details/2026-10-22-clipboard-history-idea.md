# Clipboard history idea (2026-10-22)

## 10:20 Recorded idea + existing tools

What he asked: clipboard history for the Raycast replacement (smarter search, auto snippets, autocomplete from past clips, image/doc preview + editing, long history with small disk use). Idea only, no build.

What I did: added `~/projects/claude-palette/IDEAS.md` (the palette project is the Raycast replacement; it had VISION.md but no IDEAS.md). Committed and pushed.

---

### Existing tools compared

- **Raycast Clipboard History**: already installed, free, search + image preview, history length configurable. Dies when Raycast is retired.
- **Maccy**: free, open source, tiny, keyboard-first, fuzzy search, image support. Open source means the palette could later read its SQLite store.
- **Paste**: paid subscription, rich previews, pinboards, iCloud sync, unlimited history.
- **Alfred Clipboard**: needs Alfred Powerpack; another launcher, overlaps what he's replacing.

None do auto snippets or AI autocomplete. Recommendation: Maccy for capture/history now (survives retiring Raycast, open data), Claude features layered in the palette later.

Undo: `git revert` the IDEAS.md commit in claude-palette.
