# Lid-closed setup (lidstay)

## 18:08 Lid-sleep toggle in the Hammerspoon menu
- Asked: a way to allow lid sleep for N hours or until re-enabled, inside the existing ⚙︎ Hammerspoon menu (no new icon); keep it quick. Monorepo for Mac utilities: deferred (Matt said not now).
- Did: lidstay reads `/Users/Shared/lidstay/pause_until` each tick (epoch = pause until then, `manual` = until removed). While paused it restores Low Power and sets `disablesleep 0`, so macOS sleeps normally. Expired/garbage file is moved to `.done`. install.sh creates the folder owned by the logged-in user.
- Menu: `~/.hammerspoon/modules/lid_sleep.lua` adds a "Lid" submenu to `menu_bar.lua`: status line, Allow for 1/2/4/8 hours, Allow until I turn it back, Keep awake.
- Why a file: the daemon runs as root; a user-writable file is the simplest IPC with no extra permissions. Risk: any local user can pause it (harmless).
- Tested: dry runs (manual, future, expired, garbage, none); plain-Lua smoke test of the menu (caught a Lua 5.4 `%-I` date bug, fixed); live: writing `manual` flipped SleepDisabled to 0 within 7s, removing it flipped back to 1. Not tested: clicking the actual menu items.
- Undo: remove the `lid_sleep` line from `menu_bar.lua`; lidstay ignores a missing pause file.
