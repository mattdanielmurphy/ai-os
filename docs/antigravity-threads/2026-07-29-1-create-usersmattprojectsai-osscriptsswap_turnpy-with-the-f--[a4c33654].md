---
title: "1. Create /Users/matt/projects/ai-os/scripts/swap_turn.py with the fol"
date: "2026-07-29"
conversation_id: "a4c33654-627f-45e3-9e73-948167f90511"
source: "antigravity"
---

# 1. Create /Users/matt/projects/ai-os/scripts/swap_turn.py with the fol

## User

1. Create /Users/matt/projects/ai-os/scripts/swap_turn.py with the following content:
```python
#!/usr/bin/env python3
import sys
import os
import shutil
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8649

def swap_turn_by_url(url_str: str) -> str:
    \"\"\"
    Parses ai-os-turn:// URL arguments and copies the specified history/turn_XX.md
    file over conversation_response.md in-place.
    Returns a status message.
    \"\"\"
    print(f\"Processing URL: {url_str}\")
    parsed = urllib.parse.urlparse(url_str)
    
    # Check scheme
    if parsed.scheme != \"ai-os-turn\":
        raise ValueError(f\"Invalid scheme: {parsed.scheme}. Expected ai-os-turn.\")
        
    query_params = urllib.parse.parse_qs(parsed.query)
    
    conv_id = None
    turn_val = None
    
    # Try query parameters
    for key in ['conversation_id', 'conversation-id', 'conv', 'id']:
        if key in query_params:
            conv_id = query_params[key][0]
            break
            
    for key in ['turn_index', 'turn-index', 'turn', 'index', 'file']:
        if key in query_params:
            turn_val = query_params[key][0]
            break
            
    # Try parsing path segments/netloc if query parameters are missing
    if not conv_id or not turn_val:
        netloc = parsed.netloc
        path_parts = [p for p in parsed.path.split('/') if p]
        all_parts = []
        if netloc and netloc != 'swap':
            all_parts.append(netloc)
        all_parts.extend(path_parts)
        
        for part in all_parts:
            if 'turn' in part.lower() or part.endswith('.md') or part.isdigit():
                turn_val = part
            elif len(part) > 8:
                conv_id = part

    if not conv_id:
        raise ValueError(\"Could not extract conversation_id from URL.\")
    if not turn_val:
        raise ValueError(\"Could not extract turn identifier/index from URL.\")
        
    brain_dir = Path(\"/Users/matt/.gemini/antigr
<truncated 4461 bytes>
n as e:
            print(f\"Error: {e}\", file=sys.stderr)
            sys.exit(1)
    else:
        print(f\"Starting agent-turn-swap HTTP server on port {PORT}...\")
        server = HTTPServer((\"127.0.0.1\", PORT), TurnSwapHandler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print(\"Shutting down server...\")
            server.server_close()

if __name__ == \"__main__\":
    main()
```
Make /Users/matt/projects/ai-os/scripts/swap_turn.py executable (chmod +x).

2. Create Launch Agent plist at /Users/matt/Library/LaunchAgents/com.matt.agent.turn-swap.plist:
```xml
<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
    <key>Label</key>
    <string>com.matt.agent.turn-swap</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/matt/Library/Scripts/tmux-agent-wrapper.sh</string>
        <string>keepalive</string>
        <string>agent-turn-swap</string>
        <string>/usr/bin/python3</string>
        <string>/Users/matt/projects/ai-os/scripts/swap_turn.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/matt/Library/Logs/launch-agents/turn-swap.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/matt/Library/Logs/launch-agents/turn-swap.log</string>
</dict>
</plist>
```

3. Modify /Users/matt/.local/bin/la to add:
```python
    \"turn-swap\": (USER_AGENTS / \"com.matt.agent.turn-swap.plist\", \"user\"),
```
to KNOWN_AGENTS dict.

4. Run `launchctl load -w /Users/matt/Library/LaunchAgents/com.matt.agent.turn-swap.plist` to start it, or use `la load turn-swap` since it is registered.

5. Run git auto commit script:
`python3 /Users/matt/projects/ai-os/scripts/auto_commit.py` to commit changes.

---
