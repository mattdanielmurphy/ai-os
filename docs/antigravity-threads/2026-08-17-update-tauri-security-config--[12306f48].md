---
title: "Update Tauri Security Config"
date: "2026-08-17"
conversation_id: "12306f48-0ec1-4d4d-9b25-badc348d7ad5"
source: "antigravity"
---

# Update Tauri Security Config

## User

In `/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/tauri.conf.json`, update `dangerousRemoteDomainIpcAccess` so `windows` contains `["gemini_main", "perplexity_main", "floating", "main"]` for each domain:

```json
    "security": {
      "csp": null,
      "dangerousRemoteDomainIpcAccess": [
        {
          "domain": "gemini.google.com",
          "windows": ["gemini_main", "perplexity_main", "floating", "main"],
          "enableTauriAPI": true
        },
        {
          "domain": "www.perplexity.ai",
          "windows": ["gemini_main", "perplexity_main", "floating", "main"],
          "enableTauriAPI": true
        },
        {
          "domain": "perplexity.ai",
          "windows": ["gemini_main", "perplexity_main", "floating", "main"],
          "enableTauriAPI": true
        }
      ]
    },
```

---

## Assistant

The `dangerousRemoteDomainIpcAccess` settings in `/Users/matt/projects/ai-os/apps/gemini-companion/src-tauri/tauri.conf.json` have been updated as requested. All three domains—`gemini.google.com`, `www.perplexity.ai`, and `perplexity.ai`—now have their `windows` property set to `["gemini_main", "perplexity_main", "floating", "main"]`.

---
