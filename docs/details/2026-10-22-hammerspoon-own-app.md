# Hammerspoon suite as its own app

## 17:20 Options for an own-app feel

Matt asked: make his Hammerspoon tools feel like their own independent app with a proper name, still built on
Hammerspoon. Coordinate with the menu-name thread (⚙︎ autosave name is "AI-OS Controls", commit 6ff1fb6).

Checked: installed Hammerspoon 1.1.1, `org.hammerspoon.Hammerspoon`, signed by the Hammerspoon team, Sparkle
auto-update feed set. Bartender labels items by owning app, so only a bundle rename changes "Hammerspoon" there.
Searched for an existing rebrand tool or Spoon: found none.

---

### Option 1 brand from config

- `hs.menuIcon(false)` hides 🔨; `hs.dockIcon(false)` keeps it out of Dock/⌘-Tab.
- Name the ⚙︎ menu title/header, console window title, alerts and toasts after the app.
- Small, reversible, no permission changes. Limit: Bartender, Activity Monitor and System Settings still say
  Hammerspoon.

---

### Option 2 branded app copy

- Script copies Hammerspoon.app to `~/Applications/<Name>.app`, sets CFBundleName/DisplayName, swaps the icon,
  ad-hoc re-signs. Keeps reading `~/.hammerspoon` (config path is set via `MJConfigFile` default if the bundle id
  changes).
- Wins: Bartender, ⌘-Tab, Activity Monitor, permissions list all show the name.
- Costs: re-signing breaks the team signature, so Accessibility / Screen Recording must be re-granted; Sparkle
  updates must be off and the script re-run after each Hammerspoon update (schedulable).
- Risk: medium. Could break `hs` CLI / IPC until checked. Undo: quit it, relaunch the real Hammerspoon.app.

---

### Option 3 fork and build

- Build Hammerspoon from source under a new name. Full control, but Xcode builds, signing and merging upstream
  forever. Rabbit hole; only if option 2 keeps breaking.

---

### Name

Default suggestion "AI-OS" (the menu is already "AI-OS Controls"). Matt's call.

Recorded the vision in `~/.hammerspoon/IDEAS.md`.

## 17:20 The app is the utilities suite

Matt: the own-app idea is almost the same as the mac-utilities suite. Agreed: the suite (toggleable modules in
`modules/suite.lua`, ⚙︎ menu, hourly self-update, `UTILITIES.md`) already behaves like an app. So the name belongs
to the suite, and option 1 should rename the suite, the ⚙︎ menu and the mac-utilities repo together.

Changed the default name from "AI-OS" to "Mac Utilities": AI-OS is his agent setup, and the suite already matches
the mac-utilities repo. Rename later is cheap. Option 2 (renamed .app) stays a per-Mac step, not shipped in the suite.

The 2FA "G-" ask that arrived alongside is already handled in its own thread (MessAuto regex), so not touched here.
