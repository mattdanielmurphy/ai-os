---
title: "Fix Python NameError Script"
date: "2026-08-05"
conversation_id: "97c74969-c719-4c94-9538-35d269569bdb"
source: "antigravity"
---

# Fix Python NameError Script

## User

Fix `NameError: name 'escaped_recipient' is not defined` in `/Users/matt/projects/ai-os/scripts/photon_notify.py`.

Make sure `escaped_recipient` and `escaped_text` are defined before `node_script = ...`:
```python
escaped_text = text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')
escaped_recipient = recipient.replace('\\', '\\\\').replace("'", "\\'")
```
Ensure the script is valid Python and executable!

---

## Assistant

Created At: 2026-08-05T16:56:01-06:00
Completed At: 2026-08-05T16:56:01-06:00
File Path: `file:///Users/matt/projects/ai-os/scripts/photon_notify.py`
Total Lines: 91
Total Bytes: 2678
Showing lines 1 to 91
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: #!/usr/bin/env python3
2: import os
3: import sys
4: import subprocess
5: import json
6: from pathlib import Path
7: 
8: # Load credentials
9: def load_env(path: Path):
10:     if not path.exists():
11:         return
12:     with open(path, 'r') as f:
13:         for line in f:
14:             line = line.strip()
15:             if not line or line.startswith('#'):
16:                 continue
17:             if '=' in line:
18:                 key, val = line.split('=', 1)
19:                 os.environ[key.strip()] = val.strip().strip("'").strip('"')
20: 
21: load_env(Path("/Users/matt/.hermes/.env"))
22: 
23: def send_photon_message(text: str, recipient: str = None) -> bool:
24:     project_id = os.getenv("PHOTON_PROJECT_ID")
25:     project_secret = os.getenv("PHOTON_PROJECT_SECRET")
26:     
27:     if not recipient:
28:         recipient = os.getenv("PHOTON_PHONE_NUMBER") or os.getenv("PHOTON_HOME_CHANNEL") or "[REDACTED_SECRET:PHOTON_HOME_CHANNEL]"
29:     
30:     if not project_id or not project_secret:
31:         print("Error: PHOTON_PROJECT_ID and PHOTON_PROJECT_SECRET must be set.")
32:         return False
33: 
34:     # The node script to execute
35:     node_script = """
36: import { Spectrum, text } from 'spectrum-ts';
37: import { imessage } from 'spectrum-ts/providers/imessage';
38: 
39: async function send() {
40:     try {
41:         const app = await Spectrum({
42:             projectId: '""" + project_id + """',
43:             projectSecret: '""" + project_secret + """',
44:             providers: [imessage.config()],
45:             options: { flattenGroups: true },
46:             telemetry: false,
47:         });
48:         const im = imessage(app);
49:         const space = await im.space.create('""" + escaped_recipient + """');
50:         await space.send(text('""" + escaped_text + """'));
51:         await app.stop();
52:         console.log('Success');
53:         process.exit(0);
54:     } catch (e) {
55:         console.error(e);
56:         process.exit(1);
57:     }
58: }
59: 
60: send();
61: """
62: 
63:     cwd = "/Users/matt/.hermes/hermes-agent/plugins/platforms/photon/sidecar"
64:     
65:     try:
66:         result = subprocess.run(
67:             ["node", "--input-type=module", "-e", node_script],
68:             cwd=cwd,
69:             capture_output=True,
70:             text=True
71:         )
72:         
73:         if result.returncode == 0:
74:             print(f"Message sent successfully to {recipient}")
75:             return True
76:         else:
77:             print(f"Failed to send message: {result.stderr}")
78:             return False
79:     except Exception as e:
80:         print(f"Exception while running node script: {e}")
81:         return False
82: 
83: if __name__ == "__main__":
84:     if len(sys.argv) < 2:
85:         print("Usage: python3 photon_notify.py 'Message content'")
86:         sys.exit(1)
87:     
88:     message = sys.argv[1]
89:     success = send_photon_message(message)
90:     sys.exit(0 if success else 1)
91: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-05T16:56:02-06:00
Completed At: 2026-08-05T16:56:02-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/ai-os/scripts/photon_notify.py. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -31,6 +31,9 @@
         print("Error: PHOTON_PROJECT_ID and PHOTON_PROJECT_SECRET must be set.")
         return False
 
+    escaped_text = text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')
+    escaped_recipient = recipient.replace('\\', '\\\\').replace("'", "\\'")
+
     # The node script to execute
     node_script = """
 import { Spectrum, text } from 'spectrum-ts';
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

---
