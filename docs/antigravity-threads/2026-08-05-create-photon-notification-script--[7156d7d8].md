---
title: "Create Photon Notification Script"
date: "2026-08-05"
conversation_id: "7156d7d8-b8f2-438d-a82f-0098cc331628"
source: "antigravity"
---

# Create Photon Notification Script

## User

Create a standalone Python script at `/Users/matt/projects/ai-os/scripts/photon_notify.py`.

Requirements:
1. It should load credentials from `/Users/matt/.hermes/.env` or accept environment variables:
   - PHOTON_PROJECT_ID
   - PHOTON_PROJECT_SECRET
   - PHOTON_PHONE_NUMBER / PHOTON_HOME_CHANNEL (default "[REDACTED_SECRET:PHOTON_HOME_CHANNEL]")
2. Function `send_photon_message(text: str, recipient: str = "[REDACTED_SECRET:PHOTON_HOME_CHANNEL]") -> bool`
3. Since Python doesn't have an official HTTP REST endpoint for Photon (it uses spectrum-ts / Node sidecar), `send_photon_message` should run a quick Node inline script or call the node module `spectrum-ts` to send the message.
   Specifically, Node inline snippet:
   ```javascript
   import { Spectrum, text } from '/Users/matt/.hermes/hermes-agent/plugins/platforms/photon/sidecar/node_modules/spectrum-ts/dist/index.mjs'; // or import from 'spectrum-ts' with Cwd set to /Users/matt/.hermes/hermes-agent/plugins/platforms/photon/sidecar
   import { imessage } from 'spectrum-ts/providers/imessage';
   ```
   Or executing `node --input-type=module -e "..."` in working directory `/Users/matt/.hermes/hermes-agent/plugins/platforms/photon/sidecar`.
4. Command line usage:
   `python3 /Users/matt/projects/ai-os/scripts/photon_notify.py "Message content here"`
5. Include robust error handling and log/output status.
Make sure the file is executable (`chmod +x` or standard python header).

---

## Assistant

Created At: 2026-08-05T16:55:30-06:00
Completed At: 2026-08-05T16:55:30-06:00
Created file file:///Users/matt/projects/ai-os/scripts/photon_notify.py with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission.

Created At: 2026-08-05T16:55:31-06:00
Completed At: 2026-08-05T16:55:31-06:00

				The command exited with code 0.
				Stdout:
				
				Stderr:

Created At: 2026-08-05T16:55:33-06:00
Completed At: 2026-08-05T16:55:33-06:00
Message sent to "b5975665-c0ec-416e-ad2f-f24a34652c81".

OK. I have created the script and confirmed it is executable.

---
