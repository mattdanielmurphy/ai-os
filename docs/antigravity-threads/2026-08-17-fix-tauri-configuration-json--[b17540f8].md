---
title: "Fix Tauri Configuration JSON"
date: "2026-08-17"
conversation_id: "b17540f8-234f-46f9-9c42-f3114d00f4a1"
source: "antigravity"
---

# Fix Tauri Configuration JSON

## User

In `/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/tauri.conf.json`, fix the `allowlist` block inside `"tauri"` so it is valid JSON:

```json
  "tauri": {
    "macOSPrivateApi": true,
    "allowlist": {
      "all": true
    },
    "windows": [
```

---

## Assistant

The `allowlist` block in `/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/tauri.conf.json` has been updated to be valid JSON.

---
