## Goal
Simplify the sidebar layout by removing the two separate sidebar panes and the splitter. Instead, when a project is selected/active, display the threads list directly beneath it in an inline, slightly indented container.

## Changes Made
- Modified [index.html](file:///Users/matthewmurphy/projects/ai-os/index.html):
  - Removed the bottom Project Threads header and list container.
  - Removed the `#sidebar-list-splitter` layout divider.
  - Allowed `#projects-list` to take up the full available vertical height (`flex-grow overflow-y-auto`).
- Modified [src/main.ts](file:///Users/matthewmurphy/projects/ai-os/src/main.ts):
  - Removed the `sidebarListSplitter` row-resize drag handler.
  - Updated the `renderProjects` function so each project is represented by a container card wrapper. Inside this wrapper, clicking the project header switches the active project. If the project is the active project, it appends an inline, slightly indented sub-container containing the project threads list and a small "+" button next to the "Threads" label to start a new thread.
  - Cleaned up obsolete global `newThreadBtn` event listener referencing the removed HTML element.
  - Cleaned up padding and text sizing inside `renderProjectThreads` to fit beautifully in the inline indented panel.
- Modified [FEATURES.md](file:///Users/matthewmurphy/projects/ai-os/FEATURES.md):
  - Documented the transition to inline, indented project threads and the simplified layout.

## What Worked
- High-density rendering of inline, tree-like nested lists under the active project works beautifully and leaves plenty of space for other projects.
- The build succeeded without any TypeScript compiler errors.

## What Didn't Work / Known Issues
- None.
