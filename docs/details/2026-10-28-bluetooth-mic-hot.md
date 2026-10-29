## Bluetooth mic kept hot

### Cause
PS5Voice (right-Cmd / Cmd-Tab voice app switcher, ~/projects/ps5-controller-hammerspoon/bin/ps5_voice.swift) kept the mic open 1 h after each use on power (commit d224b52). An open Bluetooth mic forces the headset into the call profile.

### Fix
Commit b9110e3: if the default input is a Bluetooth mic, close the mic as soon as listening stops (and the 15 s timer closes it if a BT mic becomes default while warm). Built-in/USB mics stay warm as before. Rejected: pinning the engine to the built-in mic (fails in clamshell mode).

### Untested
Old helper killed (mic released); Hammerspoon relaunches it on next right-Cmd press, so that first press may miss. claude-control reported "hammerspoon unreachable", so I didn't relaunch it myself. Live BT test needs Matt. Undo: git revert b9110e3 && make PS5Voice.app.
