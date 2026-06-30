# Refactored Pane Splitters & Improved Drag Hitboxes

I have completed the changes to resolve the jumping issues and improve the hitboxes for all layout pane splitters.

## Implemented Fixes

1. **Delta-Based Dragging (No Jumping or Jitter)**
   - Swapped out layout-dependent absolute position calculations for delta-offset tracking on all four splitters (`pane-splitter`, `sidebar-splitter`, `sidebar-list-splitter`, and `main-splitter`) in [main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts).
   - The dragging math now captures initial click coordinates and pane dimensions on `mousedown` and applies relative deltas on `mousemove`. This prevents feedback loops and eliminates the 200px sudden jumping completely.
   - Restored proper percentage width conversions for the main terminal vs preview splitter to maintain window resizability scaling.

2. **Generous 12px Hitboxes (Easier to Grab)**
   - Replaced thin 3px splitters in [index.html](file:///Users/matthewmurphy/projects/ai-os/index.html) with a transparent `12px` wide/high container (`w-3` / `h-3`) which makes grabbing the dividers extremely easy.
   - Enclosed a responsive `2px` nested line inside each splitter that expands to `4px` and turns blue on hover/active, keeping the UI sleek and elegant without visual clutter.

3. **Projects List Resizing Fixed**
   - The projects list height now resizes smoothly using vertical dragging offsets without getting stuck or restricted by `getBoundingClientRect()` feedback.
