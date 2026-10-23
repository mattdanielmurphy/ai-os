# Quick file search for the launcher (2026-10-23)

Thread: "Quick file search" in the Everything project. Earlier: "Better Mac file search" (Oct 18) and
"Claude search and launcher" (Oct 22, built `pf`).

## 00:20 Cardinal as the engine, findd built and live

**Asked (via coordinator):** study Cling as the quality bar, evaluate Cardinal (MIT) as base or reference,
recommend an approach and how it plugs into the launcher, continue building.

---

### findd is live

New daemon `findd` in `~/projects/claude-palette/findd`, running as login agent `ca.mattmurphy.findd`.
It indexes every file name under `~` (3.78M items, OneDrive included) and answers queries over a Unix socket.
`pf` now uses it for files and falls back to Spotlight if it's down.

Measured on Matt's Mac:
- First walk of `~`: 14.6s. OneDrive alone (112k items) took 38s on a cold first walk.
- Start from the saved index: 2.2s. Index file: 63 MB.
- Queries: 26-170 ms for real words; a one-letter query (2.2M matches) 670 ms.
- A new file shows up within ~1-2s (FSEvents), also in ~/Documents while running under launchd.

---

### Why Cardinal engine

- **MIT licence**, checked in the repo (`LICENSE`, "Copyright (c) 2025 Cardinal Contributors"). Active (last commit 2026-06-26).
- It works the way Matt asked for on Oct 18 ("why isn't there a cache, just ask anything new?"): one walk,
  a persistent index, and FSEvents replay from the last saved event id. Cling works the same way.
- It's split into crates: `search-cache` (index + Everything-style query syntax), `cardinal-sdk` (FSEvents),
  `fswalk`. We use those as a pinned git dependency (rev 4c50734) and ignore its Tauri/React app.

Rejected:
- **Cardinal's app as-is**: a separate Tauri web-UI app; Matt wants one suite app with Swift HUDs (ARCHITECTURE.md).
- **Forking all of Cardinal**: ~12k lines in search-cache alone; a pinned dependency lets us take upstream fixes.
- **Spotlight only (old pf)**: slower (~0.5s), misses hidden/dot folders, and ranking had to fight junk.
- **Cling itself**: closed source, paid Pro; it's the bar, not a base.

---

### Cling quality bar

From lowtechguys.com/cling: own binary index (not Spotlight) of the whole disk; claims <50 ms search,
<100 MB RAM; fuzzy matching; operators (`ext:`, `in:`, `!`, `size:`, `dm:`); quick filters on ⌥+key;
folder/volume scopes; recents on empty query; stash; preview pane; scripts on selected files; drop to
app; Spotlight for content search; MCP server.

Where findd stands: speed and live index match. Missing: fuzzy (Cardinal does substring/AND, prefix,
globs, regex), content search, quick filters, preview, stash, scripts. Those belong in the palette UI layer.

---

### How it plugs into the launcher

- findd is the file engine; the palette (Swift on hud-kit, per ARCHITECTURE.md) sends one JSON line per
  keystroke (debounced) to `~/Library/Caches/ca.mattmurphy.findd/findd.sock` and shows hits next to QMD's
  thread/note hits. `pf` is the CLI over the same pieces; its Haiku → Sonnet fallback stays.
- Ranking is ours (Cardinal returns matches unranked): exact/prefix/word-boundary name matches, zoxide
  frecency for folders and their contents, project roots (+.git), recency; junk (node_modules, worktrees,
  ~/Library except CloudStorage, caches, hidden, src/components trees) ranked last but still findable.

---

### iCloud hangs the walk

The first test walk froze at 0% CPU for 9+ minutes inside `~/Library/Mobile Documents` (Ulysses,
Notability bundles). That folder is excluded; iCloud stays with Spotlight/QMD (the Obsidian vault is
already in QMD). This may also be part of Raycast's old freezes; not confirmed.

---

### Untested and risks

- A full FSEvents **rescan** under launchd is untested; macOS privacy rules (TCC) could block Documents/Desktop then.
- `launchctl bootstrap` alone didn't start the agent; `build.sh` now kickstarts it. Login start after reboot not yet seen.
- No fuzzy matching yet; typos miss (pf's Haiku fallback still catches them).
- Ranking weights are constants, not yet in tweaks.json (live-tweaks rule).
- Needs the Rust nightly toolchain pinned in `findd/rust-toolchain.toml`.

Undo: `launchctl bootout gui/$(id -u)/ca.mattmurphy.findd`, move `~/Library/LaunchAgents/ca.mattmurphy.findd.plist`
to Trash; pf falls back to Spotlight automatically.

---

### Next steps

1. Palette UI (Swift, hud-kit) over findd + QMD.
2. Fuzzy matching and recents-on-empty-query in findd.
3. iCloud via mdfind in pf.
4. Ranking weights into tweaks.json.

## 00:55 Palette window v0 is live on ⌥Space

**Asked:** Matt 👍'd "build the palette window on top of it".

---

### Palette on Option-Space

`~/projects/claude-palette/app` (Swift/AppKit, compiles hud-kit in), installed as login agent
`ca.mattmurphy.palette`. ⌥Space toggles a centred search window: files from findd (~50 ms), threads and
notes from QMD (~120 ms warm) in a second section. Footer shows every key: ↩ open, ⌘↩ Finder, ⌘Y Quick
Look, ⇧⌘C copy path, ⇥ ask Haiku (runs `pf --ai`), esc close. Drag background to move, edges to resize;
position remembered. Knobs in `claude-palette/tweaks.json` (⌃⌥⌘T panel).

Why ⌥Space: Raycast holds ⌘Space; nothing in Hammerspoon or macOS shortcuts uses ⌥Space.

---

### Kept deliberately plain

System materials and label colours only: the suite palette isn't picked, so no colours of its own. The
look and interaction are open design, so per the think-alone rule Matt should sketch his own version
before anything is styled; this v0 only proves the plumbing.

hud-kit change: `HUDWindow.canMove` lets a panel say where a press may start a window move, so selecting
text or scrolling the list doesn't drag the window. hud-kit tests pass.

---

### Palette untested parts

- The ⌥Space hotkey itself: I didn't press keys on Matt's Mac. The agent runs and logged no hotkey clash.
- Typing, arrows, Quick Look and ⇥ Haiku by hand: untested. Tested: launching with `--query "phil 120"`
  showed both syllabus PDFs (screenshot below in the thread).
- First search after a cold launch took ~4 s (QMD/bun warm-up); warm searches are fast.

Undo: `launchctl bootout gui/$(id -u)/ca.mattmurphy.palette`.
