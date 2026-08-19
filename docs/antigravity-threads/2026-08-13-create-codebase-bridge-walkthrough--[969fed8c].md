---
title: "Create Codebase Bridge Walkthrough"
date: "2026-08-13"
conversation_id: "969fed8c-f1b9-4c37-9519-e924ac90b321"
source: "antigravity"
---

# Create Codebase Bridge Walkthrough

## User

Create the walkthrough artifact at /Users/matt/.gemini/antigravity/brain/03ac5033-bf95-41aa-9286-83948adacf66/walkthrough.md with content:

# Walkthrough - Live Codebase Context Bridge for Perplexity

We have built and verified the **Live Codebase Context Bridge for Perplexity**, allowing Perplexity to read live uncommitted files from your working directory on demand via pull-based HTML navigation.

## Key Changes Created

### New Service: `services/perplexity-code-bridge`
- [package.json](file:///Users/matt/projects/ai-os/services/perplexity-code-bridge/package.json)
- [src/auth.ts](file:///Users/matt/projects/ai-os/services/perplexity-code-bridge/src/auth.ts) - Manages secure persistent secret tokens saved to `~/.config/perplexity-code-bridge/token.json` and validates `?token=` parameter or `Authorization: Bearer` headers.
- [src/filter.ts](file:///Users/matt/projects/ai-os/services/perplexity-code-bridge/src/filter.ts) - Enforces strict exclusions (`.git`, `node_modules`, `.env`, secrets, `.DS_Store`) and parses `.gitignore` dynamically.
- [src/views.ts](file:///Users/matt/projects/ai-os/services/perplexity-code-bridge/src/views.ts) - HTML generators for file pre blocks, directory indexes, and full codebase manifests.
- [src/server.ts](file:///Users/matt/projects/ai-os/services/perplexity-code-bridge/src/server.ts) - Bun HTTP server returning `text/html` with `Cache-Control: no-store`.
- [src/index.ts](file:///Users/matt/projects/ai-os/services/perplexity-code-bridge/src/index.ts) - Service entrypoint listening on port `10000`.

---

## Verification Results

### Local Bridge Verification
- Tested HTTP GET on `http://localhost:10000/?token=df85b66d1b50cba39e95f06adc1d03576255e5b361475954` -> Returns 200 OK with crawlable HTML directory listing.
- Tested HTTP GET on `http://localhost:10000/package.json?token=df85b66d1b50cba39e95f06adc1d03576255e5b361475954` -> Returns 200 OK wrapping raw code in HTML `<pre><code>` block.
- Confirmed `Cache-Control: no-store, no-cache` header is active.
- Confirmed 401 Unauthorized without valid token.

---
