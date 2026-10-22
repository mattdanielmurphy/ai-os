# ⚙︎ AI-OS menu not in menu bar

## 10:30 Why ⚙︎ was missing

---

### hidden by bartender

The Hammerspoon item exists and is "in menu bar" (`isInMenuBar() == true`, title ⚙︎), but its frame is x=-9474, i.e. off-screen. That's Bartender stashing it, not Hammerspoon failing.

---

### new hotkey

Added ⌃⌥⌘M in `~/.hammerspoon/modules/menu_bar.lua`: pops the same ⚙︎ menu at the mouse via `mb:popupMenu`. Checked for conflicts with existing hotkeys (only ⌃⌥⌘L used). Commit 3df4714 on main, reloaded, hotkey confirmed registered. Not clicked by me (menu-bar rule); Matt to test.

Rejected: a new URL scheme (hammerspoon:// links already failed for him from chat).

Undo: remove the hotkey block at the end of menu_bar.lua and reload.
