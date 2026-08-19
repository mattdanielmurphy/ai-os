---
title: "Fix Path Resolution Logic"
date: "2026-08-13"
conversation_id: "67cb063d-69c8-4a05-a998-30ffdef87362"
source: "antigravity"
---

# Fix Path Resolution Logic

## User

In file /Users/matt/projects/ai-os/services/perplexity-code-bridge/src/server.ts, fix the root targetPath resolution so that fetching '/' renders the directory view of absoluteRootDir.

Replace:
const targetPath = resolve(join(absoluteRootDir, pathname.slice(1)));

With:
const targetPath = pathname === "/" ? absoluteRootDir : resolve(join(absoluteRootDir, pathname.slice(1)));

---

## Assistant

The root path resolution in `/Users/matt/projects/ai-os/services/perplexity-code-bridge/src/server.ts` has been fixed.

---
