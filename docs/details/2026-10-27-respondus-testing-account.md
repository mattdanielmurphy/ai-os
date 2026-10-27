# Clean Testing account for Respondus LockDown Browser

## 17:50 Setup scripts ready

Matt asked (via the coordinator) for a clean macOS account so nothing in the background trips LockDown Browser before the CMPUT 174 test (due Thu Oct 29, 20:00; midterm Nov 5 also uses Respondus). Goal is compliance, never hiding anything.

### What already existed

A "Testing" account (uid 503, admin) was created at 17:37 today but has never been logged into. LockDown Browser 2.1.5 is installed in /Applications.

---

### What starts for every user

- /Library/LaunchAgents start in every account: Little Snitch agent, Arturia Software Center, Adobe ARMDC helper, Jump Desktop Connect agent, Rogue Amoeba arkaudiod, two Zoom updaters.
- /Library/LaunchDaemons run as root once for the whole Mac, so they can't be skipped per user. The one that matters is Jump Desktop Connect's service (remote access), which runs as root right now.
- Login items (Hammerspoon, Keyboard Maestro, Raycast, etc.) are per user, so Testing has none.

---

### How Testing skips them

`launchctl disable gui/503/<label>` writes a per-user override, so the agent never starts in Testing and keeps running in Matt's account. It only works while Testing is logged in (the gui/503 domain doesn't exist otherwise; tested: "Domain does not support specified action"), so setup.sh runs inside Testing with Testing's password. Skipped: Jump agent, both Zoom updaters, Arturia, Adobe. Kept on purpose: Little Snitch agent (without it Little Snitch can't prompt about LockDown's connections, which could silently block it) and arkaudiod (audio helper; removing it could break mic/webcam). The dry run will show whether LockDown objects to either.

Rejected: editing the vendor plists (updates overwrite them, and it would affect Matt's account), and a guard wrapper per agent (more moving parts than the built-in override).

---

### Prefs copied

Trackpad (tap to click, three-finger drag, gestures, speed 3), keyboard repeat 5/15, natural scrolling, auto dark mode, en_CA, Dock with only LockDown Browser + Safari (128 px, auto-hide). Display arrangement is already shared Mac-wide. Safari's homepage lives in its sandbox container; the script tries to set it and falls back to telling Matt to set it in Safari Settings.

---

### Pre-test check

pretest_check.sh lists other logged-in users and any risky app or helper from any user (remote access, screen/audio capture, automation, launchers, AI apps, VMs). Run in Matt's account it flagged 24, which is the point: on test day Matt must log out of his own account (not just switch users), because fast user switching keeps all his apps running. `--pause-jump` stops the root Jump Connect service until `--resume-jump` or a restart (this affects the whole Mac briefly).

---

### Untested

setup.sh only ran as a dry run (Testing hasn't been logged into). Whether LockDown objects to Little Snitch, arkaudiod or Jump's root service is unknown until the dry run with LockDown's practice/Help Center check.

### Undo

`bash /Users/Shared/testing-account/setup.sh --undo` inside Testing re-enables the agents. Deleting the Testing account in System Settings removes everything else.
