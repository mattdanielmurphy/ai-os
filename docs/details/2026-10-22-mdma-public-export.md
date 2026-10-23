# MDMA Appothecary: public export for Tyler

## 18:40 Is everything in the app, can Tyler install it, public/Matt-only tags

Asked (via the coordinator): is every Hammerspoon script part of the app now, can Tyler install it today, tag every module public or Matt-only, and build a public export with no personal info.

---

### every script in app

Yes. Every module in `~/.hammerspoon/modules` that does something is loaded by `init.lua` and shows as a toggle in the ⚙︎ menu (⌃⌥⌘M), filed under its category (Claude & AI, Typing & Mouse, Music & Audio, Focus & Study, Mac & Devices, Other). The rest are shared libraries (brand, tweaks, hud_layout, claude_links, lid_sleep for the menu), plus `_keyprobe.lua` (a temporary key-timing test, untracked) and `turn_swap.lua` (an old `ai-os-turn://` URL handler that nothing loads; left alone).

---

### tyler can install today

Yes. The public export already existed: `bin/ship-public` publishes the shareable modules to [mac-utilities](https://github.com/mattdanielmurphy/mac-utilities) (public), and Tyler runs one line:

`bash <(curl -fsSL https://raw.githubusercontent.com/mattdanielmurphy/mac-utilities/main/install.sh)`

It installs Hammerspoon if missing, clones the repo into `~/.hammerspoon` (backs up an existing one), switches on shared mode, and opens the Accessibility setting. Every utility starts off; the ⚙︎ menu turns them on. It pulls updates hourly. Checked: the installer URL answers 200, and I ran the installer against a fresh export in a fake home folder: it installed, wrote the `shared` profile, copied only the 15 public modules, and its own test passed. Every `require` in the export resolves to a file in the export.

The public copy was last published at 17:31 today, so it's a few commits behind (tweaks module, grouped menu, branding). Not republished: publishing to a public repo waits for Matt's 👍.

---

### tags enforced by test

`modules/suite.lua` now has `MATT_ONLY` (16 modules, each with a one-line reason) next to the existing `SHAREABLE` list (public: 15 committed, plus the GIF picker another thread is adding). `tests/suite_test.lua` fails if a module `init.lua` loads is in neither list, in both, or if a Matt-only entry is no longer loaded. `ship-public` runs that test first, so an untagged module blocks publishing. Matt's own Mac still loads everything with the full categorised menu; shared mode only loads `SHAREABLE`.

Rejected: a per-module `public = true` field inside each module file. The central list already existed, ship-public reads it, and one list is easier to audit.

---

### export bug fixed

`ship-public` read the module list from the working tree, so a module still being written locally (gif_picker, listed in suite.lua but not committed) made the export crash, and could have put an unpushed name into the export. It now reads the list from `origin/main`, same as the files. Dry run: clean, privacy scan passed.

---

### known rough edges

- Song Key's "listen" fallback runs a Python script whose interpreter path is Matt's own venv; on Tyler's Mac it shows an error state instead (the Hooktheory lookup still works).
- Clipboard's ⌥C/⌥H and Bag Guard's text call Matt-only tools; UTILITIES.md already says they do nothing elsewhere.
- Tyler still sees "Hammerspoon" in ⌘-Tab and Bartender; renaming the app itself is option 2 in [Hammerspoon suite as its own app](#cmsg_01CUPXyY9oUwKVDFREVDpYDr3ESVFenmsZhBuro4Rgy8CU), still waiting on Matt.

Commits: `b7a3f05` (tags + test), `95046d5` (ship-public fix), both pushed to ~/.hammerspoon main. Another thread's uncommitted GIF picker files were left untouched. Undo: `git revert` either commit.
