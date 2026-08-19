---
title: "Fix Server Path Validation"
date: "2026-08-13"
conversation_id: "859a7a57-bf49-477d-8cf3-429901a519d1"
source: "antigravity"
---

# Fix Server Path Validation

## User

In /Users/matt/projects/ai-os/services/perplexity-code-bridge/src/server.ts:

The root directory absoluteRootDir itself matches filter.isIgnored(targetPath) when targetPath === absoluteRootDir because relative(absoluteRootDir, absoluteRootDir) returns "" which is treated as empty/ignored in filter.ts!

Update line 57 in server.ts to check targetPath !== absoluteRootDir before calling filter.isIgnored(targetPath):

Replace:
      if (!existsSync(targetPath) || filter.isIgnored(targetPath)) {

With:
      if (!existsSync(targetPath) || (targetPath !== absoluteRootDir && filter.isIgnored(targetPath))) {

---

## Assistant

The requested change has been applied to `/Users/matt/projects/ai-os/services/perplexity-code-bridge/src/server.ts`. The check now explicitly avoids treating the root directory as ignored.

---
