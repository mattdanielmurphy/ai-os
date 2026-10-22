# Lid sleep menu items

## 18:10 Allow lid sleep from the ⚙︎ menu
- Ask: add "allow lid sleep for N hours" and "until re-enabled" to the existing Hammerspoon ⚙︎ menu, fast version only.
- Found the work already drafted (uncommitted) in ~/.hammerspoon/modules/lid_sleep.lua + one line in menu_bar.lua; lidstay pause support already committed (6bcefdd).
- Mechanism: menu writes /Users/Shared/lidstay/pause_until (epoch or "manual"); root daemon checks every 5s, sets disablesleep 0 while paused; resume = rename to .done.
- Tested: dry-run of manual and expired pauses; module loads in Hammerspoon. Committed 565ff3a, reloaded Hammerspoon.
- Another session concurrently fixed the time format (211be4b, Lua rejects %-I) and installed the new daemon at 18:07.
- Not tested: a real lid close during a pause.
- Undo: remove the require line in menu_bar.lua; `rm` the pause file equivalent = pick "Keep awake with lid closed".
