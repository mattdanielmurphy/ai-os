---
title: "Remove Dotenv Dependency Script"
date: "2026-08-05"
conversation_id: "fe2d824a-b99c-4f1f-8aeb-725c094e90f1"
source: "antigravity"
---

# Remove Dotenv Dependency Script

## User

Fix `/Users/matt/projects/ai-os/scripts/photon_notify.py` to parse `/Users/matt/.hermes/.env` manually using simple line splitting (e.g. key=val) or standard python regex rather than importing `dotenv`, so it doesn't depend on python package `dotenv` being installed. Make sure it runs without external dependencies outside standard python libraries (`os`, `sys`, `subprocess`, `re`, `pathlib`, `json`). Make sure `chmod +x` is set.

---

## Assistant

Created At: 2026-08-05T16:55:37-06:00
Completed At: 2026-08-05T16:55:37-06:00
File Path: `file:///Users/matt/projects/ai-os/scripts/photon_notify.py`
Total Lines: 75
Total Bytes: 2038
Showing lines 1 to 75
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: #!/usr/bin/env python3
2: import os
3: import sys
4: import subprocess
5: import json
6: from pathlib import Path
7: from dotenv import load_dotenv
8: 
9: # Load credentials
10: load_dotenv(Path("/Users/matt/.hermes/.env"))
11: 
12: def send_photon_message(text: str, recipient: str = None) -> bool:
13:     project_id = os.getenv("PHOTON_PROJECT_ID")
14:     project_secret = os.getenv("PHOTON_PROJECT_SECRET")
15:     
16:     if not recipient:
17:         recipient = os.getenv("PHOTON_PHONE_NUMBER") or os.getenv("PHOTON_HOME_CHANNEL") or "[REDACTED_SECRET:PHOTON_HOME_CHANNEL]"
18:     
19:     if not project_id or not project_secret:
20:         print("Error: PHOTON_PROJECT_ID and PHOTON_PROJECT_SECRET must be set.")
21:         return False
22: 
23:     # The node script to execute
24:     node_script = f"""
25: import {{ Spectrum }} from 'spectrum-ts';
26: import {{ imessage }} from 'spectrum-ts/providers/imessage';
27: 
28: const spectrum = new Spectrum({{
29:     projectId: '{project_id}',
30:     projectSecret: '{project_secret}'
31: }});
32: 
33: async function send() {{
34:     try {{
35:         await spectrum.send(imessage('{recipient}'), '{text}');
36:         console.log('Success');
37:         process.exit(0);
38:     }} catch (e) {{
39:         console.error(e);
40:         process.exit(1);
41:     }}
42: }}
43: 
44: send();
45: """
46: 
47:     cwd = "/Users/matt/.hermes/hermes-agent/plugins/platforms/photon/sidecar"
48:     
49:     try:
50:         result = subprocess.run(
51:             ["node", "--input-type=module", "-e", node_script],
52:             cwd=cwd,
53:             capture_output=True,
54:             text=True
55:         )
56:         
57:         if result.returncode == 0:
58:             print(f"Message sent successfully to {recipient}")
59:             return True
60:         else:
61:             print(f"Failed to send message: {result.stderr}")
62:             return False
63:     except Exception as e:
64:         print(f"Exception while running node script: {e}")
65:         return False
66: 
67: if __name__ == "__main__":
68:     if len(sys.argv) < 2:
69:         print("Usage: python3 photon_notify.py 'Message content'")
70:         sys.exit(1)
71:     
72:     message = sys.argv[1]
73:     success = send_photon_message(message)
74:     sys.exit(0 if success else 1)
75: 
The above content shows the entire, complete file contents of the requested file.

Created At: 2026-08-05T16:55:39-06:00
Completed At: 2026-08-05T16:55:41-06:00
The following changes were made by the replace_file_content tool to: /Users/matt/projects/ai-os/scripts/photon_notify.py. If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.
[diff_block_start]
@@ -4,10 +4,21 @@
 import subprocess
 import json
 from pathlib import Path
-from dotenv import load_dotenv
 
 # Load credentials
-load_dotenv(Path("/Users/matt/.hermes/.env"))
+def load_env(path: Path):
+    if not path.exists():
+        return
+    with open(path, 'r') as f:
+        for line in f:
+            line = line.strip()
+            if not line or line.startswith('#'):
+                continue
+            if '=' in line:
+                key, val = line.split('=', 1)
+                os.environ[key.strip()] = val.strip().strip("'").strip('"')
+
+load_env(Path("/Users/matt/.hermes/.env"))
 
 def send_photon_message(text: str, recipient: str = None) -> bool:
     project_id = os.getenv("PHOTON_PROJECT_ID")
[diff_block_end]

Please note that the above snippet only shows the MODIFIED lines from the last change. It shows up to 3 lines of unchanged lines before and after the modified lines. The actual file contents may have many more lines not shown.

We did our best to apply changes despite some inaccuracies. Double check if the edit applied is what you intended.

---
