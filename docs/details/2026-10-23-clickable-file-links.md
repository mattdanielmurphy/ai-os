# Clickable file and folder links (2026-10-23)

## 13:15 Rule + handler built, waiting on Matt's click test

Asked (coordinator brief): every file or folder an agent mentions must be a clickable link. Folders go to Finder, text files to VS Code. Find formats that work in the Claude app, add the rule, rebuild, push, add a coordinator memory pointer.

---

### Why links go through do.test

Earlier notes (2026-10-21 summon-in-state-demos, 2026-10-22 menu-bar-gear-hidden) say Claude chat drops custom schemes: `hammerspoon://` links already failed for Matt. `vscode://` and `file://` aren't http either, so they likely fail the same way. Plain http survives, and Hammerspoon already runs an action-link server (`modules/action_links.lua`, puma-dev `do.test` → localhost:3095). So I added `http://do.test/open/<absolute path>`.

---

### How the handler decides

`~/.hammerspoon/modules/path_links.lua`:
- folder → shown in Finder
- folder with an extension (`.app`, `.logicx`, `.xcodeproj`) → revealed in its parent, so a click never launches an app or package
- file whose first 8 KB has no NUL byte → VS Code (`code -g`)
- other files (images, audio, PDFs) → revealed in Finder
- missing path → 404 page

Commands run via `hs.task` with argument arrays (no shell), so paths can't inject commands. Any local web page could hit the endpoint, but the worst it can do is show a file in VS Code or a folder in Finder.

Tests: `lua tests/path_links_test.lua` (encoding, decoding, kinds, bundles). Live: curl to the endpoint brought up AG_CONTEXT.md in VS Code, `docs/` in Finder, and the Obsidian index.md (path with spaces). 404 for a missing path.

---

### What is still untested

I can't click inside the Claude app myself (computer use refuses to control Claude's own window) and the browser pane isn't signed in to claude.ai. So whether the app renders `http://do.test/...` as a clickable link, and whether `vscode://`, `file://` or bare paths work, is untested. I posted a test message with links A–E and asked Matt to click them. If do.test links don't render in the app, the rule needs another format.

---

### Rule and pointers

- `.rules/core_safety.md` new bullet after "Link every service" → `build_rules.py` (CLAUDE.md, GEMINI.md, AGENTS.md).
- `~/.claude/CLAUDE.md` one line.
- Mac memory `link-files-and-folders.md`.
- Coordinator asked to add a one-line pointer to its memory.
- Helper: `scripts/file_link.py <path> [--label] [--url]`.

Undo: revert the ai-os and hammerspoon commits; remove the memory file.
