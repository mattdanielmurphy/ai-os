---
title: "Ai-os: swap_turn.py [71ed87]"
date: "2026-07-29"
conversation_id: "71ed874d-2236-4aa8-996f-6c50a82f1b3d"
source: "antigravity"
---

# Ai-os: swap_turn.py [71ed87]

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

## Assistant

Created At: 2026-07-29T12:57:20-06:00
Completed At: 2026-07-29T12:57:20-06:00
Created file file:///Users/matt/projects/ai-os/scripts/swap_turn.py with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-07-29T12:57:20-06:00
Completed At: 2026-07-29T12:57:20-06:00
Created file file:///Users/matt/Library/LaunchAgents/com.matt.agent.turn-swap.plist with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-07-29T12:57:20-06:00
Completed At: 2026-07-29T12:57:20-06:00
File Path: `file:///Users/matt/.local/bin/la`
Total Lines: 459
Total Bytes: 16510
Showing lines 1 to 459
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: #!/usr/bin/env python3
2: """la — Launch Agent Manager: list, load, unload, restart, view, tail logs."""
3: 
4: import argparse
5: import os
6: import plistlib
7: import re
8: import subprocess
9: import sys
10: from pathlib import Path
11: 
12: # ── Paths ─────────────────────────────────────────────────────────────────────
13: HOME = Path.home()
14: USER_AGENTS = HOME / "Library" / "LaunchAgents"
15: SYSTEM_AGENTS = Path("/Library/LaunchAgents")
16: SYSTEM_DAEMONS = Path("/Library/LaunchDaemons")
17: LOG_DIR = HOME / "Library" / "Logs" / "launch-agents"
18: TMUX_BIN = Path("/usr/local/bin/tmux")
19: KNOWN_AGENTS = {  # label → (plist path, type)
20:     "irig-watcher": (USER_AGENTS / "com.matt.agent.irig-watcher.plist", "user"),
21:     "gemini-thread-saver": (USER_AGENTS / "com.matt.agent.gemini-thread-saver.plist", "user"),
22:     "litellm": (USER_AGENTS / "com.matt.agent.litellm.plist", "user"),
23:     "userscript-bundler": (USER_AGENTS / "com.mattmurphy.userscript-bundler.plist", "user"),
24:     "chrome-debug": (USER_AGENTS / "com.matt.agent.chrome-debug.plist", "user"),
25:     "hermes-gateway": (USER_AGENTS / "com.matt.agent.hermes-gateway.plist", "user"),
26:     "rules-watcher": (USER_AGENTS / "com.matt.agent.rules-watcher.plist", "user"),
27:     "energy-monitor": (USER_AGENTS / "com.matt.agent.energy-monitor.plist", "user"),
28:     "gemini-ingest": (USER_AGENTS / "com.matt.agent.gemini-ingest.plist", "user"),
29:     "notesync": (USER
<truncated 15109 bytes>
="Agent name(s)")
407: 
408:     # unload
409:     p_unload = sub.add_parser("unload", help="Unload (stop) an agent")
410:     p_unload.add_argument("name", nargs="+", help="Agent name(s)")
411: 
412:     # restart
413:     p_re = sub.add_parser("restart", help="Unload + load (restart) an agent")
414:     p_re.add_argument("name", nargs="+", help="Agent name(s)")
415: 
416:     # start
417:     p_start = sub.add_parser("start", help="Start (run) an agent immediately")
418:     p_start.add_argument("name", nargs="+", help="Agent name(s)")
419: 
420:     # view
421:     p_view = sub.add_parser("view", help="View plist contents")
422:     p_view.add_argument("name", help="Agent name")
423: 
424:     # logs
425:     p_logs = sub.add_parser("logs", help="Tail logs from tmux or log file")
426:     p_logs.add_argument("name", help="Agent name")
427:     p_logs.add_argument("-n", "--lines", type=int, default=50, help="Number of lines (default: 50)")
428: 
429:     # edit
430:     p_edit = sub.add_parser("edit", help="Open plist in default editor")
431:     p_edit.add_argument("name", help="Agent name")
432: 
433:     # which
434:     p_which = sub.add_parser("which", help="Show plist path")
435:     p_which.add_argument("name", help="Agent name")
436: 
437:     args = parser.parse_args()
438: 
439:     if args.command is None:
440:         # Bare `la` — show your agents
441:         cmd_list(argparse.Namespace(all=False))
442:     else:
443:         dispatch = {
444:             "list": cmd_list,
445:             "status": cmd_status,
446:             "load": cmd_load,
447:             "unload": cmd_unload,
448:             "restart": cmd_restart,
449:             "start": cmd_start,
450:             "view": cmd_view,
451:             "logs": cmd_logs,
452:             "edit": cmd_edit,
453:             "which": cmd_which,
454:         }
455:         dispatch[args.command](args)
456: 
457: 
458: if __name__ == "__main__":
459:     main()
The above content shows the entire, complete file contents of the requested file.

---
