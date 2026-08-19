---
title: "Create Photon Notification Script"
date: "2026-08-05"
conversation_id: "14b12d5b-25bd-4232-9abf-5dcb6fabbca6"
source: "antigravity"
---

# Create Photon Notification Script

## User

Create script at `/Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/scripts/photon_notify.py` (which writes to VPS via SFTP).

Contents:
```python
#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

def send_photon_message(text: str, recipient: str = "[REDACTED_SECRET:PHOTON_HOME_CHANNEL]") -> bool:
    project_id = os.getenv("PHOTON_PROJECT_ID", "[REDACTED_SECRET:PHOTON_PROJECT_ID]")
    project_secret = os.getenv("PHOTON_PROJECT_SECRET", "[REDACTED_SECRET:PHOTON_PROJECT_SECRET]")

    escaped_text = text.replace('\\', '\\\\').replace("'", "\\'").replace('\n', '\\n')
    escaped_recipient = recipient.replace('\\', '\\\\').replace("'", "\\'")

    node_script = """
import { Spectrum, text } from 'spectrum-ts';
import { imessage } from 'spectrum-ts/providers/imessage';

async function send() {
    try {
        const app = await Spectrum({
            projectId: '""" + project_id + """',
            projectSecret: '""" + project_secret + """',
            providers: [imessage.config()],
            options: { flattenGroups: true },
            telemetry: false,
        });
        const im = imessage(app);
        const space = await im.space.create('""" + escaped_recipient + """');
        await space.send(text('""" + escaped_text + """'));
        await app.stop();
        console.log('Success');
        process.exit(0);
    } catch (e) {
        console.error(e);
        process.exit(1);
    }
}

send();
"""

    cwd = "/home/ubuntu/projects/jules-burner"
    bun_bin = "/home/ubuntu/.bun/bin/bun"
    
    try:
        result = subprocess.run(
            [bun_bin, "eval", node_script],
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

Write this using `write_to_file` tool with `Overwrite: true`.

---

## Assistant

Created At: 2026-08-05T17:02:56-06:00
Completed At: 2026-08-05T17:02:56-06:00
Created file file:///Users/matt/Library/CloudStorage/CloudMounter-OracleVPS/projects/jules-burner/scripts/photon_notify.py with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T17:02:57-06:00
Completed At: 2026-08-05T17:02:57-06:00
Message sent to "b5975665-c0ec-416e-ad2f-f24a34652c81".

---
