---
title: "Overwrite `/Users/matt/projects/ai-os/scripts/photon_notify.py` with the following python code:"
date: "2026-08-05"
conversation_id: "628de2cd-5b0f-486a-89f6-bb5c9efd1715"
source: "antigravity"
---

# Overwrite `/Users/matt/projects/ai-os/scripts/photon_notify.py` with the following python code:

## User

Overwrite `/Users/matt/projects/ai-os/scripts/photon_notify.py` with the following python code:

```python
#!/usr/bin/env python3
import os
import sys
import subprocess
import json
from pathlib import Path

def load_env(path: Path):
    if not path.exists():
        return
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip().strip("'").strip('"')

load_env(Path("/Users/matt/.hermes/.env"))

def send_photon_message(text: str, recipient: str = None) -> bool:
    project_id = os.getenv("PHOTON_PROJECT_ID")
    project_secret = os.getenv("PHOTON_PROJECT_SECRET")
    
    if not recipient:
        recipient = os.getenv("PHOTON_PHONE_NUMBER") or os.getenv("PHOTON_HOME_CHANNEL") or "+18259775250"
    
    if not project_id or not project_secret:
        print("Error: PHOTON_PROJECT_ID and PHOTON_PROJECT_SECRET must be set.")
        return False

    escaped_text = text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')
    escaped_recipient = recipient.replace('\\', '\\\\').replace("'", "\\'")

    node_script = f"""
import {{ Spectrum, text }} from 'spectrum-ts';
import {{ imessage }} from 'spectrum-ts/providers/imessage';

async function send() {{
    try {{
        const app = await Spectrum({{
            projectId: '{project_id}',
            projectSecret: '{project_secret}',
            providers: [imessage.config()],
            options: {{ flattenGroups: true }},
            telemetry: false,
        }});
        const im = imessage(app);
        const space = await im.space.create('{escaped_recipient}');
        await space.send(text('{escaped_text}'));
        await app.stop();
        console.log('Success');
        process.exit(0);
    }} catch (e) {{
        console.error(e);
        process.exit(1);
    }}
}}

send();
"""

    cwd = "/Users/matt/.hermes/hermes-agent/plugins/platforms/photon/sidecar"
    
    try:
        result = subprocess.run(
            ["node", "--input-type=module", "-e", node_script],
            cwd=cwd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"Message sent successfully to {recipient}")
            return True
        else:
            print(f"Failed to send message: {result.stderr}")
            return False
    except Exception as e:
        print(f"Exception while running node script: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 photon_notify.py 'Message content'")
        sys.exit(1)
    
    message = sys.argv[1]
    success = send_photon_message(message)
    sys.exit(0 if success else 1)
```

Make sure it's executable!

---
