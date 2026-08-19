---
title: "Create MacOS LaunchAgent Plist"
date: "2026-08-05"
conversation_id: "4cb6b206-5cd1-4b4d-b095-499d1d1fda9e"
source: "antigravity"
---

# Create MacOS LaunchAgent Plist

## User

Please create the macOS LaunchAgent plist at `/Users/matt/Library/LaunchAgents/com.matt.agent.ai-os-wiki.plist` with the following content:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.matt.agent.ai-os-wiki</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/matt/projects/ai-os/bin/ai-os-wiki</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/Users/matt/projects/ai-os</string>
    <key>StandardOutPath</key>
    <string>/Users/matt/Library/Logs/launch-agents/ai-os-wiki.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/matt/Library/Logs/launch-agents/ai-os-wiki.log</string>
</dict>
</plist>
```
Ensure directory `/Users/matt/Library/Logs/launch-agents` exists as well.

---

## Assistant

Created At: 2026-08-05T01:33:42-06:00
Completed At: 2026-08-05T01:33:42-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-05T01:33:45-06:00
Completed At: 2026-08-05T01:33:45-06:00
Created file file:///Users/matt/Library/LaunchAgents/com.matt.agent.ai-os-wiki.plist with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T01:33:46-06:00
Completed At: 2026-08-05T01:33:46-06:00
Message sent to "fd282fc4-76da-473a-95ac-f18bc6ccd868".

The macOS LaunchAgent plist has been created at [/Users/matt/Library/LaunchAgents/com.matt.agent.ai-os-wiki.plist](file:///Users/matt/Library/LaunchAgents/com.matt.agent.ai-os-wiki.plist), and the log directory [/Users/matt/Library/Logs/launch-agents](file:///Users/matt/Library/Logs/launch-agents) has been created.

---
