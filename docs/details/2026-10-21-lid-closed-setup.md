# Lid-closed setup (lidstay)

## 18:08 Lid-sleep toggle in the Hammerspoon menu
- Asked: a way to allow lid sleep for N hours or until re-enabled, inside the existing ⚙︎ Hammerspoon menu (no new icon); keep it quick. Monorepo for Mac utilities: deferred (Matt said not now).
- Did: lidstay reads `/Users/Shared/lidstay/pause_until` each tick (epoch = pause until then, `manual` = until removed). While paused it restores Low Power and sets `disablesleep 0`, so macOS sleeps normally. Expired/garbage file is moved to `.done`. install.sh creates the folder owned by the logged-in user.
- Menu: `~/.hammerspoon/modules/lid_sleep.lua` adds a "Lid" submenu to `menu_bar.lua`: status line, Allow for 1/2/4/8 hours, Allow until I turn it back, Keep awake.
- Why a file: the daemon runs as root; a user-writable file is the simplest IPC with no extra permissions. Risk: any local user can pause it (harmless).
- Tested: dry runs (manual, future, expired, garbage, none); plain-Lua smoke test of the menu (caught a Lua 5.4 `%-I` date bug, fixed); live: writing `manual` flipped SleepDisabled to 0 within 7s, removing it flipped back to 1. Not tested: clicking the actual menu items.
- Undo: remove the `lid_sleep` line from `menu_bar.lua`; lidstay ignores a missing pause file.

## 18:20 Standalone menu bar icon for Tyler
- Asked: when Tyler installs lidstay he gets a menu bar icon just for lidstay; Matt keeps his ⚙︎ Lid submenu.
- Did: `menubar.swift` (AppKit status item, SF Symbols laptop/moon), same items as lid_sleep.lua. install.sh compiles it with swiftc (ships with git's Command Line Tools, so Tyler already has it) and loads user LaunchAgent `local.lidstay.menu`. KeepAlive only on crash, so "Quit" stays quit until login.
- Decision: default on, auto-off if `~/.hammerspoon/modules/lid_sleep.lua` exists, so Matt's reinstalls never add a second icon. Override `MENUBAR=1|0`.
- Rejected: SwiftBar/xbar (Tyler would need another app), Hammerspoon (same).
- Tested: compiles; launched 4s without crashing. Not tested: icon visible (screenshot missed menu bar), menu clicks, the install.sh run itself (needs sudo).
- Undo: `MENUBAR=0 ./install.sh` or `./uninstall.sh`; revert lidstay commit 7e70d2b.

## 18:25 lidstay-only menu bar icon for Tyler
- Asked: Tyler should get a menu bar icon just for lidstay when he fetches the repo. (Rest of that message, shared self-updating suite etc., went to the "Shared self-updating utility suite" thread per the coordinator.)
- Two versions got built at once: mine (SwiftBar plugin, needs SwiftBar app + manual plugin-folder pick) and a duplicate thread's native `menubar.swift` (AppKit status item, built by install.sh with swiftc, per-user LaunchAgent `local.lidstay.menu`, skipped where Hammerspoon's `lid_sleep.lua` exists). Kept the native one: no extra app, auto-starts, `git pull && ./install.sh` rebuilds it. Removed the SwiftBar plugin (git rm).
- Added: install.sh skips the icon with a hint when Command Line Tools (swiftc) are missing, instead of aborting.
- Tested: menubar.swift compiles; binary ran 5s without crashing (with claude-control clearance). Repo is public; logged-out clone works. Not tested: clicking the icon's items, or a full install on a Mac without Hammerspoon.
- Tyler's final prompt: posted as a card in the thread.

## 18:27 Rule: ask Matt to test menu bar items
- Matt: menu bar icons are hard for agents to test (Bartender drawer); ask him instead.
- Saved: ai-os `.rules/core_safety.md` (compiled into CLAUDE.md / GEMINI.md via build_rules.py), `~/.claude/CLAUDE.md`, memory `menu-bar-ask-matt-to-test`. First put it in `.rules/mac_env.md`, but that file isn't compiled into the prompts, so moved it.
- Asked Matt to click through the ⚙︎ → Lid items on his Mac.
