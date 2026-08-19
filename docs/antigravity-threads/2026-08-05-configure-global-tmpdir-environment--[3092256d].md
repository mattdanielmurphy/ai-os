---
title: "Configure Global TMPDIR Environment"
date: "2026-08-05"
conversation_id: "3092256d-d0ba-45ec-91ed-c61c43a20461"
source: "antigravity"
---

# Configure Global TMPDIR Environment

## User

Create a LaunchAgent plist file at `/Users/matt/Library/LaunchAgents/com.user.tmpdir.plist` to set `TMPDIR=/tmp` permanently for all macOS GUI applications (including Zed launched from Finder/Dock/Spotlight).

Target file path: `/Users/matt/Library/LaunchAgents/com.user.tmpdir.plist`

Content to write:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.tmpdir</string>
    <key>ProgramArguments</key>
    <array>
        <string>launchctl</string>
        <string>setenv</string>
        <string>TMPDIR</string>
        <string>/tmp</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

Use `write_to_file`. Ensure parent directory exists.

---

## Assistant

Created At: 2026-08-05T16:04:08-06:00
Completed At: 2026-08-05T16:04:08-06:00
Created file file:///Users/matt/Library/LaunchAgents/com.user.tmpdir.plist with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T16:04:09-06:00
Completed At: 2026-08-05T16:04:09-06:00
Message sent to "52f35ffb-b73f-4b68-b45d-a7355f38afd1".

---
