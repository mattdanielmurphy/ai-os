## Goal
Fix splitter dragging offsets/jumps (especially for the main terminals-to-preview splitter and the sidebar list splitter) and make the active dragging hitboxes wider and easier to grab.

## Changes Made
- Modified [index.html](file:///Users/matthewmurphy/projects/ai-os/index.html):
  - Converted the thin 3px splitters into 12px wide/tall containers (`w-3`/`h-3`) with background set to transparent, which act as comfortable, generous invisible hitboxes for row/col resizing.
  - Placed a thin (`2px`) responsive nested `div` line inside each splitter container that automatically thickens to `4px` and turns blue on parent hover/active state, maintaining high-density aesthetics.
- Modified [src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts):
  - Refactored all four drag handlers (`splitter`, `sidebarSplitter`, `sidebarListSplitter`, `mainSplitter`) to compute coordinates based on delta tracking (`startX`/`startY` and `startWidth`/`startHeight` stored on `mousedown`).
  - Replaced target element relative calculations with initial-value offset formulas to prevent coordinate feedback loops and eliminate jump offsets when dragging.
  - Restored proper percentage conversion for the horizontal main splitter to preserve responsive window-resize scaling.
- Modified [FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md):
  - Documented the delta-based dragging refactoring and responsive invisible hitbox enhancements.

## What Worked
- Delta-based offset calculations on `mousemove` completely eliminated the layout jumps and offsets.
- Transparent `12px` splitter containers with absolute/flex nested lines solved the active hit area problem while looking clean and professional.
- Building the project with `pnpm run build` completed successfully.

## What Didn't Work / Known Issues
- None. Resizing works perfectly across all splitters.

## Architecture Notes
- Using delta-based calculations (capturing `startX`/`startY` and `startWidth`/`startHeight` on `mousedown` and applying `delta = current - start` on `mousemove`) is significantly more robust than computing the bounding box of elements dynamically during layout shifts.
