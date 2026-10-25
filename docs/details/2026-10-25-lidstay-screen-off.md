# lidstay: screen stays on with the lid closed

## 16:08 Why the screen stayed lit, and the fix

Matt: "lidstay doesn't turn the brightness to zero when the lid closes! big problem".

---

### Screen was lit behind the lid

lidstay never had any screen or brightness code. With `pmset disablesleep 1`, macOS doesn't sleep on lid close, and the display only turns off as part of sleeping, so it stayed on. Proof from `pmset -g log`: "Display is turned on" 2026-10-24 11:19, next "turned off" only at 16:04 today when I tested, while the lid was shut. The backlight read ~380 nits (rawBrightness 1488/2047) and powerd held "Prevent sleep while display is on".

---

### Screen off instead of brightness

I first built a brightness helper (private DisplayServices framework, what the brightness keys use). With the lid closed it reads 0 and setting it changes nothing on the hardware backlight, so it can't work here. Rejected; source kept in lidstay `tmp/brightness.swift`.

`pmset displaysleepnow` did work: the "display is on" assertion vanished and the log shows "Display is turned off". It's better than brightness zero anyway: the panel is fully off, and opening the lid wakes it at the brightness it had, so nothing needs restoring.

How it works: every 5 s tick with the lid closed, if powerd's "Prevent sleep while display is on" assertion exists, lidstay runs `pmset displaysleepnow` and logs "lid closed: screen off". Rechecking every tick also catches anything that wakes the display later.

---

### Install needs his password

The running daemon is a copy in /usr/local/bin, so the fix goes live only after `cd ~/projects/lidstay && ./install.sh` (sudo password). I can't run sudo.

---

### Untested lid-open wake

Not tested live: that opening the lid wakes the screen (normal macOS behaviour, expected) and the full daemon path (only dry-run tests plus a manual displaysleepnow with the lid shut). Undo: `git revert 67f30ef` in lidstay, then `./install.sh`.
