---
title: "Update Spectrum SDK Script"
date: "2026-08-05"
conversation_id: "fdf67a07-3ea1-41b3-bf78-8143393c0ff2"
source: "antigravity"
---

# Update Spectrum SDK Script

## User

Update `/Users/matt/projects/ai-os/scripts/photon_notify.py` line 35-56 to use the verified Spectrum SDK pattern:

```javascript
import { Spectrum, text } from 'spectrum-ts';
import { imessage } from 'spectrum-ts/providers/imessage';

async function send() {
  try {
    const app = await Spectrum({
      projectId: '${project_id}',
      projectSecret: '${project_secret}',
      providers: [imessage.config()],
      options: { flattenGroups: true },
      telemetry: false,
    });
    const im = imessage(app);
    const space = await im.space.create('${recipient}');
    await space.send(text('${text_escaped}'));
    await app.stop();
    console.log('Success');
    process.exit(0);
  } catch (e) {
    console.error(e);
    process.exit(1);
  }
}

send();
```

Make sure single quotes / backslashes in `${text}` are properly escaped for js/python formatting!

---

## Assistant

Created At: 2026-08-05T16:55:46-06:00
Completed At: 2026-08-05T16:55:46-06:00
File Path: `file:///Users/matt/projects/ai-os/scripts/photon_notify.py`
Total Lines: 86
Total Bytes: 2382
Showing lines 30 to 60
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
30:     if not project_id or not project_secret:
31:         print("Error: PHOTON_PROJECT_ID and PHOTON_PROJECT_SECRET must be set.")
32:         return False
33: 
34:     # The node script to execute
35:     node_script = f"""
36: import {{ Spectrum }} from 'spectrum-ts';
37: import {{ imessage }} from 'spectrum-ts/providers/imessage';
38: 
39: const spectrum = new Spectrum({{
40:     projectId: '{project_id}',
41:     projectSecret: '{project_secret}'
42: }});
43: 
44: async function send() {{
45:     try {{
46:         await spectrum.send(imessage('{recipient}'), '{text}');
47:         console.log('Success');
48:         process.exit(0);
49:     }} catch (e) {{
50:         console.error(e);
51:         process.exit(1);
52:     }}
53: }}
54: 
55: send();
56: """
57: 
58:     cwd = "/Users/matt/.hermes/hermes-agent/plugins/platforms/photon/sidecar"
59:     
60:     try:
The above content does NOT show the entire file contents. If you need to view any lines of the file which were not shown to complete your task, call this tool again to view those lines.

---
