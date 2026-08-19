---
title: "Restore Tauri Windows Configuration"
date: "2026-08-17"
conversation_id: "69bdf1ad-7e86-4d9f-a3db-3efb6d46411b"
source: "antigravity"
---

# Restore Tauri Windows Configuration

## User

In `/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/tauri.conf.json`, restore the `windows` array so it only defines the main window (because the other windows are constructed dynamically in `main.rs`):

```json
    "windows": [
      {
        "title": "ai-os",
        "width": 1000,
        "height": 800
      }
    ],
```

---

## Assistant

The `tauri.conf.json` file in `/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/` has been updated to only define the main window in the `windows` array. Correspondingly, the `dangerousRemoteDomainIpcAccess` configuration was updated to reference only the `main` window for the relevant domains.

---
