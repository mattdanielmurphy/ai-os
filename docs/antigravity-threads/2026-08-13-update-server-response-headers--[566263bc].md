---
title: "Update Server Response Headers"
date: "2026-08-13"
conversation_id: "566263bc-f860-4304-a2c6-aaf755d38302"
source: "antigravity"
---

# Update Server Response Headers

## User

In /Users/matt/projects/ai-os/services/perplexity-code-bridge/src/server.ts, add "Bypass-Tunnel-Remainder": "true" to the Response headers object:

Replace:
      const headers = {
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
      };

With:
      const headers = {
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": "no-store, no-cache, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
        "Bypass-Tunnel-Remainder": "true"
      };

---

## Assistant

The "Bypass-Tunnel-Remainder": "true" header has been successfully added to the `headers` object in `/Users/matt/projects/ai-os/services/perplexity-code-bridge/src/server.ts`.

---
