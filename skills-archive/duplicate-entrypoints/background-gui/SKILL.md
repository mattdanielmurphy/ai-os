---
title: "macOS Background GUI Access (LaunchDaemons / tmux)"
name: "macos-background-gui"
description: "Guidelines and workarounds for accessing the macOS GUI (clipboard, notifications) from background daemons, launch agents, and tmux sessions."
category: macos
---

# macOS Background GUI Access

When running scripts from macOS LaunchDaemons, LaunchAgents, or background `tmux` sessions (such as `tmux-agent-wrapper.sh`), processes exist outside the active graphical user's bootstrap namespace. This prevents simple GUI commands like `pbcopy` or `osascript` from reliably interacting with the clipboard pasteboard or Notification Center.

## The Solution

To securely bridge commands into the user's graphical session namespace, use `/bin/launchctl asuser <uid> <command>`.

### Copying to the Clipboard (`pbcopy`)

Instead of standard `pbcopy`, execute:
```bash
/bin/launchctl asuser $(id -u) /usr/bin/pbcopy
```

### Sending Notifications

Avoid `osascript -e 'display notification...'` as it often fails headlessly. Use `terminal-notifier` instead:
```bash
/bin/launchctl asuser $(id -u) /usr/local/bin/terminal-notifier -title "My App" -message "Message goes here"
```

### Node.js Example

```javascript
const { spawn } = require('child_process');

const uid = process.getuid();

// Copy to clipboard
const pbcopy = spawn('/bin/launchctl', ['asuser', uid.toString(), '/usr/bin/pbcopy']);
pbcopy.stdin.write("My clipboard text");
pbcopy.stdin.end();

// Send notification
spawn('/bin/launchctl', ['asuser', uid.toString(), '/usr/local/bin/terminal-notifier', '-title', 'Notice', '-message', 'Task completed.']);
```
