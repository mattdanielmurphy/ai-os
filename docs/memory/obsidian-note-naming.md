---
name: obsidian-note-naming
description: Notes saved to Obsidian use human-friendly filenames with clickable links
metadata:
  type: feedback
---

When saving notes to the Obsidian vault at `/Users/matthewmurphy/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal/`, always:

1. **Use a human-readable filename** derived from the note's content (e.g. `Space Facts 🚀.md`, `Recipe Ideas.md`). Never use robotic timestamp-based names like `User_Note_YYYY-MM-DD_HHMMSS.md`.
2. **Provide a clickable `file://` URL** after saving so the user can open the file directly from the terminal.

**Why:** Timestamp-based filenames are uninformative and frustrating to browse. Human names make the vault navigable and pleasant to use.

**How to apply:** Derive the filename from the content's title/theme. After writing, output a clickable link.