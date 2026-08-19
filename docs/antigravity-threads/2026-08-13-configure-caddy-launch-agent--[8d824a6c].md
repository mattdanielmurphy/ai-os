---
title: "Configure Caddy Launch Agent"
date: "2026-08-13"
conversation_id: "8d824a6c-ed31-4349-901e-98f3bd1b623f"
source: "antigravity"
---

# Configure Caddy Launch Agent

## User

Please create two files to set up Caddy as a macOS launch agent:

1. Directory: `/Users/matt/projects/ai-os/caddy`
2. Run script `/Users/matt/projects/ai-os/caddy/run_caddy.sh`:
```zsh
#!/bin/zsh
# run_caddy.sh — Start Caddy reverse proxy for LLM/LiteLLM

if [ -f ~/.zshrc ]; then
    source ~/.zshrc
fi

cd /Users/matt/projects/ai-os
exec /opt/homebrew/bin/caddy run --config /Users/matt/projects/ai-os/Caddyfile
```

Make `/Users/matt/projects/ai-os/caddy/run_caddy.sh` executable using `chmod +x`.

3. Launch Agent Plist `/Users/matt/Library/LaunchAgents/com.matt.agent.caddy.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.matt.agent.caddy</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/matt/Library/Scripts/tmux-agent-wrapper.sh</string>
        <string>keepalive</string>
        <string>agent-caddy</string>
        <string>/Users/matt/projects/ai-os/caddy/run_caddy.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>ThrottleInterval</key>
    <integer>5</integer>
    <key>WorkingDirectory</key>
    <string>/Users/matt/projects/ai-os</string>
    <key>StandardOutPath</key>
    <string>/Users/matt/Library/Logs/launch-agents/caddy.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/matt/Library/Logs/launch-agents/caddy.log</string>
</dict>
</plist>
```

Use `write_to_file` to create both files.

---

## Assistant

The Caddy configuration files have been successfully created:

1.  Created run script: [`/Users/matt/projects/ai-os/caddy/run_caddy.sh`](file:///Users/matt/projects/ai-os/caddy/run_caddy.sh) (made executable)
2.  Created Launch Agent plist: [`/Users/matt/Library/LaunchAgents/com.matt.agent.caddy.plist`](file:///Users/matt/Library/LaunchAgents/com.matt.agent.caddy.plist)

---
