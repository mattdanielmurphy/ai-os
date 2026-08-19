---
title: "Fix Server Path Resolution"
date: "2026-08-13"
conversation_id: "9cbd890f-1d12-4f8d-883c-9eb960c6a95a"
source: "antigravity"
---

# Fix Server Path Resolution

## User

Inspect and fix /Users/matt/projects/ai-os/services/perplexity-code-bridge/src/server.ts.

Make sure that when pathname is "/" or empty, targetPath is set to absoluteRootDir so that existsSync(targetPath) evaluates to true and it returns renderDirectoryView.

Here is the exact replace required in server.ts:

Replace:
      const targetPath = resolve(join(absoluteRootDir, pathname.slice(1)));

      if (!targetPath.startsWith(absoluteRootDir)) {
        return new Response("Forbidden: Path traversal blocked", { status: 403, headers: { "Content-Type": "text/plain" } });
      }

With:
      const relSubPath = pathname.startsWith("/") ? pathname.slice(1) : pathname;
      const targetPath = relSubPath === "" ? absoluteRootDir : resolve(join(absoluteRootDir, relSubPath));

      if (!targetPath.startsWith(absoluteRootDir)) {
        return new Response("Forbidden: Path traversal blocked", { status: 403, headers: { "Content-Type": "text/plain" } });
      }

---

## Assistant

The requested changes have been applied to `/Users/matt/projects/ai-os/services/perplexity-code-bridge/src/server.ts`. The path resolution logic now correctly handles root and empty paths by setting `targetPath` to `absoluteRootDir`.

---
