---
title: "Fix Node-Vibrant Turbopack Import"
date: "2026-08-13"
conversation_id: "581fb0e8-066c-496a-8025-4e70811a544e"
source: "antigravity"
---

# Fix Node-Vibrant Turbopack Import

## User

Fix node-vibrant import in app/lib/palette.ts. Turbopack complains about default import. Change to named import or require/custom sharp color extraction buffer to ensure clean build. Sharp is already installed. Using sharp to resize to 64x64 and extract dominant color + contrast palette is fast, light, and completely avoids Turbopack node-vibrant ESM module export issues.

---

## Assistant

The `node-vibrant` dependency has been replaced with `sharp` in `app/lib/palette.ts` to resolve the Turbopack ESM module export issue. The updated code now fetches the image and uses `sharp` to process it, which is faster and more reliable in this environment.

You can view the updated file here: [palette.ts](file:///Users/matt/projects/music-cross-linker/app/lib/palette.ts)

---
